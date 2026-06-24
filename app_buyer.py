"""
买家咨询页面
买家通过二维码或链接打开，进行商品咨询
特点：界面简洁、移动端友好、不需要登录
"""
import streamlit as st
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_models.tongyi import ChatTongyi
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_chroma import Chroma

import config_data as config
from merchant_manager import get_merchant, get_product
from merchant_kb import MerchantKnowledgeBase
from log_manager import log_modification


# 从 URL 获取参数
query_params = st.query_params
merchant_id = query_params.get("merchant", "")
product_id = query_params.get("product", "")


st.set_page_config(
    page_title="AI 智能客服",
    page_icon="💬",
    layout="centered",
)


# ========== 校验商家 ==========
if not merchant_id:
    st.error("❌ 链接无效：缺少商家信息")
    st.stop()

merchant = get_merchant(merchant_id)
if not merchant:
    st.error("❌ 商家不存在或链接已失效")
    st.stop()


# ========== 页面头部 ==========
st.title(f"💬 {merchant['name']} 智能客服")
st.caption(f"AI 7×24 小时为你解答商品疑问")

if product_id:
    product = get_product(merchant_id, product_id)
    if product:
        st.info(f"📦 当前咨询商品：**{product['name']}**")
        st.session_id_prefix = f"buyer_{merchant_id}_{product_id}"
    else:
        st.session_id_prefix = f"buyer_{merchant_id}"
else:
    st.session_id_prefix = f"buyer_{merchant_id}"


# ========== 初始化 RAG 链 ==========
@st.cache_resource
def get_rag_chain(_merchant_id, _product_id):
    """获取 RAG 链（缓存以提升性能）"""
    kb = MerchantKnowledgeBase(_merchant_id, _product_id)
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

    def format_docs(docs: list) -> str:
        if not docs:
            return "（暂无参考资料）"
        return "\n\n".join([
            f"【资料{i+1}】{doc.page_content}"
            for i, doc in enumerate(docs)
        ])

    def get_input_text(value):
        return value["input"]

    chain = (
        {
            "input": RunnablePassthrough(),
            "context": RunnableLambda(get_input_text) | retriever | format_docs,
            "history": RunnableLambda(lambda x: x.get("history", [])),
        }
        | prompt_template
        | chat_model
        | StrOutputParser()
    )
    return chain


chain = get_rag_chain(merchant_id, product_id)


# ========== 会话状态 ==========
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "content": f"你好！我是 {merchant['name']} 的 AI 客服，可以问我商品相关问题哦~"}
    ]


# ========== 显示历史消息 ==========
for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])


# ========== 用户输入 ==========
if prompt := st.chat_input("请输入你的问题..."):
    # 显示用户消息
    st.chat_message("user").write(prompt)
    st.session_state["messages"].append({"role": "user", "content": prompt})

    # 构造历史消息
    history = []
    for m in st.session_state["messages"][:-1]:
        if m["role"] == "user":
            history.append(("human", m["content"]))
        else:
            history.append(("ai", m["content"]))

    # 调用 AI
    with st.chat_message("assistant"):
        with st.spinner("思考中..."):
            try:
                # 简化：直接调用链，不使用 message history（避免 session_id 复杂度）
                # 用一次性 prompt 包含历史
                response_placeholder = st.empty()
                full_response = ""

                # 流式输出
                for chunk in chain.stream({
                    "input": prompt,
                    "history": history[-6:],  # 只保留最近 3 轮对话
                }):
                    full_response += chunk
                    response_placeholder.write(full_response + "▌")

                response_placeholder.write(full_response)

                st.session_state["messages"].append({
                    "role": "assistant",
                    "content": full_response,
                })

                # 记录到日志
                log_modification(
                    action="buyer_query",
                    target=f"商家{merchant_id}/商品{product_id or '通用'}",
                    detail=f"提问: {prompt[:50]}...",
                    operator="买家",
                )
            except Exception as e:
                st.error(f"出错了：{e}")
                log_modification(
                    action="buyer_query_error",
                    target=f"商家{merchant_id}/商品{product_id or '通用'}",
                    detail=f"错误: {str(e)}",
                    operator="买家",
                )


# ========== 底部信息 ==========
st.divider()
st.caption("💡 提示：本 AI 客服仅供参考，重要问题请联系店铺真人客服")
