"""
多商家知识库服务
支持按商家 ID 隔离知识库，每个商家可以有多个商品
"""
import os
import hashlib
from datetime import datetime
from langchain_chroma import Chroma
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
import config_data as config
from merchant_manager import get_merchant_kb_path, get_product_kb_path
from log_manager import log_modification


def get_string_md5(input_str: str, encoding='utf-8') -> str:
    """计算字符串 MD5"""
    str_bytes = input_str.encode(encoding=encoding)
    md5_obj = hashlib.md5()
    md5_obj.update(str_bytes)
    return md5_obj.hexdigest()


class MerchantKnowledgeBase:
    """
    商家知识库
    支持按 merchant_id 隔离数据，可选地按 product_id 进一步细分
    """

    def __init__(self, merchant_id: str, product_id: str = None):
        """
        参数:
            merchant_id: 商家 ID
            product_id: 商品 ID（可选，不传则用商家级知识库）
        """
        self.merchant_id = merchant_id
        self.product_id = product_id

        # 根据是否指定商品选择不同的持久化目录
        if product_id:
            self.persist_directory = get_product_kb_path(merchant_id, product_id)
        else:
            self.persist_directory = get_merchant_kb_path(merchant_id)

        # collection_name 也按商家/商品区分，避免冲突
        if product_id:
            self.collection_name = f"rag_{merchant_id}_{product_id}"
        else:
            self.collection_name = f"rag_{merchant_id}"

        os.makedirs(self.persist_directory, exist_ok=True)

        self.chroma = Chroma(
            collection_name=self.collection_name,
            embedding_function=DashScopeEmbeddings(model=config.embedding_model_name),
            persist_directory=self.persist_directory,
        )

        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.chunk_size,
            chunk_overlap=config.chunk_overlap,
            separators=config.separators,
            length_function=len,
        )

        # MD5 记录文件路径
        self.md5_path = os.path.join(self.persist_directory, "md5.txt")

    def _check_md5(self, md5_str: str) -> bool:
        """检查 MD5 是否已存在（去重）"""
        if not os.path.exists(self.md5_path):
            open(self.md5_path, 'w', encoding='utf-8').close()
            return False
        with open(self.md5_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip() == md5_str:
                    return True
        return False

    def _save_md5(self, md5_str: str):
        """保存 MD5 到文件"""
        with open(self.md5_path, 'a', encoding='utf-8') as f:
            f.write(md5_str + '\n')

    def upload_text(self, data: str, filename: str = "未命名") -> str:
        """
        上传文本到知识库

        参数:
            data: 文本内容
            filename: 文件名（用于元数据）

        返回:
            操作结果描述
        """
        md5_hex = get_string_md5(data)
        if self._check_md5(md5_hex):
            msg = "[重复] 内容已存在知识库"
            log_modification(
                action="upload",
                target=f"商家{self.merchant_id}/商品{self.product_id}",
                detail=f"重复内容，跳过: {filename}",
                extra={"filename": filename, "md5": md5_hex},
            )
            return msg

        # 切分文本
        if len(data) > config.max_spliter_char_number:
            chunks = self.splitter.split_text(data)
        else:
            chunks = [data]

        # 构建元数据
        target_name = f"商家{self.merchant_id}"
        if self.product_id:
            target_name += f"/商品{self.product_id}"
        metadata = {
            "source": filename,
            "create_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "operator": "商家",
            "merchant_id": self.merchant_id,
            "product_id": self.product_id or "",
        }

        # 写入向量库
        self.chroma.add_texts(
            texts=chunks,
            metadatas=[metadata for _ in chunks],
        )

        self._save_md5(md5_hex)

        msg = f"[成功] 已载入 {len(chunks)} 个文本段到知识库"
        log_modification(
            action="upload",
            target=target_name,
            detail=f"上传文件: {filename}, 共 {len(chunks)} 段",
            extra={"filename": filename, "chunks": len(chunks), "md5": md5_hex},
        )
        return msg

    def search(self, query: str, k: int = None) -> list:
        """
        检索知识库

        参数:
            query: 查询文本
            k: 返回结果数

        返回:
            文档列表
        """
        k = k or config.similarity_threshold
        return self.chroma.similarity_search(query, k=k)


if __name__ == "__main__":
    # 测试代码
    from merchant_manager import create_merchant, add_product

    m = create_merchant("测试商家2", "用于测试")
    p = add_product(m["merchant_id"], "测试商品", "")

    kb = MerchantKnowledgeBase(m["merchant_id"], p["product_id"])
    result = kb.upload_text("这件衣服是纯棉的，适合夏天穿。", "材质说明.txt")
    print(result)

    docs = kb.search("材质")
    for d in docs:
        print(f"- {d.page_content}")
