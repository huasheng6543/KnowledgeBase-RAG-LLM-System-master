# KnowledgeBase-RAG-LLM-System

## 基于 **Streamlit** 的个人商家知识库 RAG 智能客服系统

专为个人商家打造的 AI 智能客服解决方案，支持多商家、多商品独立知识库管理，可快速对接淘宝/抖音/拼多多等平台。

- 多商家、多商品独立知识库，数据隔离
- 网页端上传 TXT 文件，自动切分后写入 Chroma 向量库（MD5 去重）
- 智能客服聊天界面，基于知识库内容进行检索增强回答（RAG）
- 支持会话历史查看，流式思维链输出
- 生成买家咨询链接，可挂到淘宝/抖音/拼多多商品页面
- 修改日志自动记录，方便回溯问题

**技术栈**：Python / Streamlit / LangChain / Chroma / DashScope Embeddings / Qwen ChatModel

---

## ✨ 功能一览

### 🏪 商家管理后台
- 创建/编辑/删除商家，每个商家数据独立隔离
- 添加/编辑/删除商品，为不同商品建立独立知识库
- 上传知识文件（TXT）或直接粘贴文本到知识库
- 为每个商品生成独立的买家咨询链接
- 查看所有操作的修改日志

### 💬 买家咨询页面
- 智能问答，基于知识库内容回答商品相关问题
- 多轮对话支持，上下文理解
- 流式输出，打字机效果
- 移动端友好，扫码即可咨询

### 🔌 API 接口
- RESTful API 接口，支持对接千牛/抖音等系统
- 自动生成接口文档（Swagger UI）

---

## 📸 功能截图

### 商品管理
![商品管理](https://github.com/huasheng6543/KnowledgeBase-RAG-LLM-System-master/raw/main/images/商品管理.png)

### 知识库上传
![知识库上传](https://github.com/huasheng6543/KnowledgeBase-RAG-LLM-System-master/raw/main/images/知识库上传.png)

### 尺码推荐问答
![尺码推荐问答](https://github.com/huasheng6543/KnowledgeBase-RAG-LLM-System-master/raw/main/images/尺码推荐问答.png)

### 颜色推荐问答
![颜色推荐问答](https://github.com/huasheng6543/KnowledgeBase-RAG-LLM-System-master/raw/main/images/颜色推荐问答.png)

### 咨询链接生成
![咨询链接](https://github.com/huasheng6543/KnowledgeBase-RAG-LLM-System-master/raw/main/images/咨询链接.png)

---

## 🧩 项目结构

```text
KnowledgeBase-RAG-LLM-System/
├─ app_admin.py               # 商家管理后台（Streamlit）
├─ app_buyer.py               # 买家咨询页面（Streamlit）
├─ app_chat.py                # 原有智能客服（保留）
├─ app_upload.py              # 原有知识库上传（保留）
├─ api_server.py              # FastAPI 接口服务
├─ init_project.py            # 项目初始化脚本
├─ merchant_manager.py        # 商家/商品管理模块
├─ merchant_kb.py             # 多商家隔离的知识库服务
├─ knowledge_base.py          # 知识库处理：读取、切分、写库、去重
├─ rag.py                     # RAG 链组装
├─ vector_stores.py           # 向量库检索封装（持久化）
├─ file_history_store.py      # 会话历史存储
├─ log_manager.py             # 修改日志记录模块
├─ config_data.py             # 模型、路径、chunk 等参数配置
├─ requirements.txt           # 项目依赖
├─ assets/                    # 示例知识库文件
│   ├─ 示例知识库_常见问题.txt
│   ├─ 尺码推荐.txt
│   ├─ 洗涤养护.txt
│   └─ 颜色推荐.txt
├─ images/                    # 功能截图
├─ merchants/                 # 商家数据目录（自动生成）
│   ├─ index.json             # 商家索引
│   └─ m_xxx/                 # 商家专属目录
│       └─ knowledge_base/    # 向量库
├─ logs/                      # 修改日志目录
└─ chroma_db/                 # 原有向量库（保留）
```

---

## ✅ 环境准备

### 1) 安装依赖
```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 2) 配置 API Key
```bash
# Windows PowerShell
$env:DASHSCOPE_API_KEY = "你的阿里云API Key"

# Linux/Mac
export DASHSCOPE_API_KEY="你的阿里云API Key"
```

---

## ⚙️ 配置说明

在 `config_data.py` 中配置：

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `base_url` | http://localhost:8501 | 商家管理后台地址 |
| `buyer_base_url` | http://localhost:8502 | 买家咨询页面地址 |
| `chunk_size` | 1000 | 文本切分大小 |
| `chunk_overlap` | 100 | 相邻片段重叠字数 |
| `similarity_threshold` | 1 | 检索返回文档数量 |
| `embedding_model_name` | text-embedding-v4 | 嵌入模型 |
| `chat_model_name` | qwen3-max | 聊天模型 |

---

## 🚀 快速运行

### 方式一：个人商家模式（推荐）

```bash
# 启动商家管理后台
python -m streamlit run app_admin.py --server.port 8501

# 启动买家咨询页面（另一终端）
python -m streamlit run app_buyer.py --server.port 8502
```

**使用流程**：
1. 打开 http://localhost:8501 创建商家和商品
2. 上传知识库文件（使用 `assets/示例知识库_常见问题.txt` 测试）
3. 在【咨询链接】获取买家咨询链接
4. 买家通过链接访问 http://localhost:8502 进行咨询

### 方式二：API 接口模式

```bash
# 启动 API 服务
python api_server.py

# 接口文档地址：http://localhost:8000/docs
```

### 方式三：原有单知识库模式

```bash
# 启动知识库上传服务
streamlit run app_upload.py

# 启动智能客服
streamlit run app_chat.py
```

---

## 🔗 多平台对接

### 淘宝/天猫
- 在商品详情页添加咨询链接二维码
- 买家扫码即可咨询商品相关问题

### 抖音/拼多多
- 在商品描述中添加咨询链接
- 或在直播间引导买家访问咨询页面

### 微信
- 将咨询链接生成二维码，放在朋友圈或公众号文章中

---

## 📝 使用示例

### 知识库文件格式
```text
Q: 这件衣服会起球吗？
A: 不会，面料经过抗起球处理，正常穿着不易起球。

Q: 身高170体重130穿什么码？
A: 建议 L 码，宽松版型可选 XL。

Q: 多久发货？
A: 工作日 48 小时内发货，节假日顺延。

Q: 不喜欢可以退吗？
A: 支持 7 天无理由退换，需保持商品完好。
```

### 测试问答
| 提问 | 预期回答 |
|------|----------|
| 这件衣服会起球吗？ | 不会，面料经过抗起球处理... |
| 身高170体重130穿什么码？ | 建议 L 码... |
| 多久发货？ | 工作日 48 小时内发货... |
| 不喜欢可以退吗？ | 支持 7 天无理由退换... |

---

## 🛠 常见问题

### Q1：上传文件后，聊天问答仍然像"没有检索到资料"？
#### 可能原因：
- 上传服务和问答服务使用了不同的向量库持久化目录
- `collection_name` 配置不一致
- 上传文件后未正确写入本地数据目录

### Q2：上传文件后，回答显示较慢或没有正常输出？
#### 可能原因：
- 文本切分参数或检索参数设置不合适，调整 chunk、检索 k 值
- 模型接口或网络请求响应较慢
- 本地向量库未正确初始化

### Q3：买家咨询页面显示"链接无效"？
#### 可能原因：
- 链接缺少 `merchant` 参数
- 商家 ID 不存在或已被删除
- 确保从商家管理后台的【咨询链接】标签页获取完整链接

### Q4：项目运行报路径或配置错误怎么办？
#### 建议优先检查：
- `config_data.py` 中的模型配置、路径配置是否正确
- 本地数据目录是否存在
- API Key 是否已配置到环境变量

---

## ✨ 优化方向（仅供参考）

- **增加深度 Rerank**：提升检索结果质量，如 LangChain 的 EGE rerank 模块
- **支持更多文件类型**：PDF / Markdown / Word，增加 LangChain 插件即可实现
- **多模型混合**：单模型 -> 多模型，如豆包的多层推理架构
- **Chroma -> FAISS**：轻量 Chroma 适合个人复现，FAISS 的高效检索适配企业
- **实时数据同步**：对接电商平台 API，自动同步商品信息
- **对话记忆优化**：更智能的上下文理解和记忆管理

---

## 📄 License

本项目仅用于学习与交流，如需商用请自行补全安全、合规与授权相关内容。

---

## 🙌 致谢

- Black Horse
- Streamlit
- LangChain
- Chroma / chromadb
- Aliyun Bai / qwen