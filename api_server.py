"""
API 接口层
将 RAG 服务封装为 RESTful API，便于对接：
- 淘宝千牛插件
- 抖音客服系统
- 微信小程序
- 任何支持 HTTP 的客户端

启动方式：uvicorn api_server:app --host 0.0.0.0 --port 8000
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import uvicorn

from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_models.tongyi import ChatTongyi

from merchant_manager import get_merchant, get_product
from merchant_kb import MerchantKnowledgeBase
from log_manager import log_modification
import config_data as config


app = FastAPI(
    title="个人商家 RAG API",
    description="为多平台对接提供的 RAG 智能客服接口",
    version="1.0.0",
)


# ========== 数据模型 ==========
class QueryRequest(BaseModel):
    merchant_id: str
    product_id: Optional[str] = None
    question: str
    user_id: Optional[str] = "anonymous"
    history: Optional[list] = []  # 格式: [{"role": "user", "content": "..."}, ...]


class QueryResponse(BaseModel):
    answer: str
    merchant_id: str
    product_id: Optional[str]
    success: bool
    error: Optional[str] = None


# ========== RAG 链缓存 ==========
_rag_chain_cache = {}


def get_or_create_chain(merchant_id: str, product_id: str = None):
    """获取或创建 RAG 链（带缓存）"""
    cache_key = f"{merchant_id}_{product_id or 'common'}"
    if cache_key in _rag_chain_cache:
        return _rag_chain_cache[cache_key]

    # 校验商家
    merchant = get_merchant(merchant_id)
    if not merchant:
        raise HTTPException(status_code=404, detail="商家不存在")

    if product_id:
        product = get_product(merchant_id, product_id)
        if not product:
            raise HTTPException(status_code=404, detail="商品不存在")

    kb = MerchantKnowledgeBase(merchant_id, product_id)
    retriever = kb.chroma.as_retriever(
        search_type="similarity",
        search_kwargs={"k": config.similarity_threshold},
    )

    prompt_template = ChatPromptTemplate.from_messages([
        ("system", "你是店铺的 AI 客服，请基于我提供的参考资料，"
                   "用亲切友好的语气回答买家问题。如果资料中没有明确答案，"
                   "请直接说明无法回答，建议咨询店铺真人客服。"
                   "参考资料：{context}"),
        MessagesPlaceholder("history"),
        ("user", "{input}"),
    ])

    chat_model = ChatTongyi(model=config.chat_model_name)

    def format_docs(docs) -> str:
        if not docs:
            return "（暂无参考资料）"
        return "\n\n".join([
            f"【资料{i+1}】{doc.page_content}"
            for i, doc in enumerate(docs)
        ])

    def format_history(history: list) -> list:
        """将 API 的 history 转换为 LangChain 格式"""
        result = []
        for m in history or []:
            if m.get("role") in ["user", "human"]:
                result.append(("human", m["content"]))
            elif m.get("role") in ["assistant", "ai"]:
                result.append(("ai", m["content"]))
        return result

    chain = (
        {
            "input": RunnablePassthrough(),
            "context": retriever | format_docs,
            "history": RunnableLambda(format_history),
        }
        | prompt_template
        | chat_model
        | StrOutputParser()
    )

    _rag_chain_cache[cache_key] = chain
    return chain


# ========== API 端点 ==========
@app.get("/")
def root():
    """根路径，健康检查"""
    return {
        "service": "个人商家 RAG API",
        "status": "running",
        "version": "1.0.0",
    }


@app.get("/api/merchants")
def list_all_merchants():
    """列出所有商家"""
    from merchant_manager import list_merchants
    return {"merchants": list_merchants()}


@app.post("/api/query", response_model=QueryResponse)
def query_knowledge(req: QueryRequest):
    """
    核心接口：问答查询

    请求示例：
    ```json
    {
        "merchant_id": "m_20260101_001",
        "product_id": "p_20260101_001",  // 可选
        "question": "这件衣服会起球吗？",
        "user_id": "buyer_123",
        "history": []
    }
    ```
    """
    try:
        chain = get_or_create_chain(req.merchant_id, req.product_id)

        answer = chain.invoke({
            "input": req.question,
            "history": req.history or [],
        })

        # 记录日志
        log_modification(
            action="api_query",
            target=f"商家{req.merchant_id}/商品{req.product_id or '通用'}",
            detail=f"用户[{req.user_id}] 提问: {req.question[:50]}",
            operator="API买家",
        )

        return QueryResponse(
            answer=answer,
            merchant_id=req.merchant_id,
            product_id=req.product_id,
            success=True,
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        log_modification(
            action="api_query_error",
            target=f"商家{req.merchant_id}",
            detail=f"错误: {str(e)}",
            operator="API买家",
        )
        return QueryResponse(
            answer="",
            merchant_id=req.merchant_id,
            product_id=req.product_id,
            success=False,
            error=str(e),
        )


@app.get("/api/health")
def health_check():
    """健康检查"""
    return {"status": "ok"}


if __name__ == "__main__":
    # 启动 API 服务
    # 部署到服务器后可以：nohup uvicorn api_server:app --host 0.0.0.0 --port 8000 &
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
    )
