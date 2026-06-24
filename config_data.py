

# ===================== 商家服务部署配置 =====================
# 商家管理后台地址（商家自己使用）
base_url = "http://localhost:8501"

# 买家咨询页面地址（买家访问）
# 本地测试：http://localhost:8502
# 部署到服务器后改为：http://你的服务器IP:8502 或 绑定域名
buyer_base_url = "http://localhost:8502"

# 买家侧页面文件名
buyer_page = "app_buyer.py"
admin_page = "app_admin.py"

# ===================== 原有配置 =====================
md5_path = "./md5.text"

# Chroma
collection_name="rag"
persist_directory="./chroma_db"

# spliter
chunk_size= 1000
chunk_overlap= 100
separators =["\n\n","\n",".","!","?","。","！","？"," ",""]

max_spliter_char_number= 1000  # 文本分割阈值

# 相似度K值
similarity_threshold =1     # 检索返回匹配的文档数量

embedding_model_name="text-embedding-v4"
chat_model_name="qwen3-max"

#
session_config = {
    "configurable": {
        "session_id": "user_001",
    }
}