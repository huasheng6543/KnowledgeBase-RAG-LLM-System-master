# KnowledgeBase-RAG-LLM-System

## Personal Merchant Knowledge Base RAG Intelligent Customer Service System

Built on **Streamlit**, this is an AI intelligent customer service solution designed specifically for personal merchants. It supports multi-merchant and multi-product independent knowledge base management, and can quickly integrate with platforms like Taobao, Douyin, and Pinduoduo.

### Core Features
- Multi-merchant, multi-product independent knowledge base with data isolation
- Web-based TXT file upload, automatic text splitting, and storage into Chroma vector database (MD5 deduplication)
- Intelligent customer service chat interface with RAG-based retrieval-augmented answering
- Session history viewing and streaming thinking chain output
- Buyer consultation link generation for Taobao/Douyin/Pinduoduo product pages
- Automatic modification log recording for problem tracing

### Technology Stack
- **Language**: Python 3.10+
- **Frontend Framework**: Streamlit
- **LLM Framework**: LangChain
- **Vector Database**: ChromaDB
- **Embedding Model**: DashScope Text Embedding v4
- **Chat Model**: Qwen3-Max
- **API Framework**: FastAPI
- **Database**: SQLite (built-in with Chroma)

---

## ✨ Features Overview

### 🏪 Merchant Management Dashboard
- Create/edit/delete merchants with data isolation
- Add/edit/delete products with independent knowledge bases
- Upload knowledge files (TXT) or paste text directly
- Generate unique consultation links for each product
- View modification logs

### 💬 Buyer Consultation Page
- Intelligent Q&A based on knowledge base content
- Multi-turn conversation support with context understanding
- Streaming output with typewriter effect
- Mobile-friendly design, scan to consult

### 🔌 API Interface
- RESTful API for integrating with Qianniu/Douyin systems
- Auto-generated Swagger UI documentation

---

## 📁 Project Structure

```text
KnowledgeBase-RAG-LLM-System/
├── app_admin.py              # Merchant management dashboard (Streamlit)
├── app_buyer.py              # Buyer consultation page (Streamlit)
├── app_chat.py               # Legacy chat interface (kept for compatibility)
├── app_upload.py             # Legacy upload service (kept for compatibility)
├── api_server.py             # FastAPI interface service
├── init_project.py           # Project initialization script
├── merchant_manager.py       # Merchant/product management module
├── merchant_kb.py            # Multi-merchant isolated knowledge base service
├── knowledge_base.py         # Knowledge base processing: read, split, store, deduplicate
├── rag.py                    # RAG chain assembly
├── vector_stores.py          # Vector database retrieval wrapper (persistent)
├── file_history_store.py     # Session history storage
├── log_manager.py            # Modification log recording module
├── config_data.py            # Model, path, chunk parameter configuration
├── requirements.txt          # Project dependencies
├── assets/                   # Sample knowledge base files
│   ├── sample_knowledge_faq.txt
│   ├── size_recommendation.txt
│   ├── washing_care.txt
│   └── color_recommendation.txt
├── images/                   # Feature screenshots
├── merchants/                # Merchant data directory (auto-generated)
│   ├── index.json            # Merchant index
│   └── m_xxx/                # Merchant-specific directory
│       └── knowledge_base/   # Chroma vector database
├── logs/                     # Modification logs directory
└── chroma_db/                # Legacy vector database (kept for compatibility)
```

---

## 🚀 Quick Start

### Prerequisites
1. Python 3.10+ installed
2. DashScope API Key (from Alibaba Cloud)

### Installation
```bash
# Clone repository
git clone https://github.com/huasheng6543/KnowledgeBase-RAG-LLM-System-master.git
cd KnowledgeBase-RAG-LLM-System-master

# Install dependencies
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### Configuration
```bash
# Windows PowerShell
$env:DASHSCOPE_API_KEY = "your_api_key_here"

# Linux/Mac
export DASHSCOPE_API_KEY="your_api_key_here"
```

### Run
```bash
# Start merchant management dashboard
python -m streamlit run app_admin.py --server.port 8501

# Start buyer consultation page (in another terminal)
python -m streamlit run app_buyer.py --server.port 8502

# Start API service (optional)
python api_server.py
```

---

## 🔗 Integration with E-commerce Platforms

### Taobao/Tmall
- Add consultation QR code in product detail page
- Buyers scan to consult about product questions

### Douyin/Pinduoduo
- Add consultation link in product description
- Guide buyers to consultation page during live streams

### WeChat
- Generate QR code for consultation link
- Place in Moments or official account articles

---

## 📝 Usage Example

### Knowledge Base File Format
```text
Q: Will this clothing pill?
A: No, the fabric has been treated with anti-pilling technology.

Q: What size for height 170cm and weight 65kg?
A: Recommend size L, or XL for loose fit.

Q: When will you ship?
A: Ship within 48 hours on workdays.

Q: Can I return if I don't like it?
A: 7-day return policy, keep product intact.
```

### Test Questions
| Question | Expected Answer |
|----------|-----------------|
| Will this clothing pill? | No, the fabric has been treated... |
| What size for height 170cm? | Recommend size L... |
| When will you ship? | Within 48 hours on workdays... |
| Can I return? | 7-day return policy... |

---

## 🛠 Configuration Options

| Option | Default | Description |
|--------|---------|-------------|
| base_url | http://localhost:8501 | Merchant dashboard address |
| buyer_base_url | http://localhost:8502 | Buyer consultation address |
| chunk_size | 1000 | Text splitting size |
| chunk_overlap | 100 | Overlap between chunks |
| similarity_threshold | 1 | Number of retrieved documents |
| embedding_model_name | text-embedding-v4 | Embedding model |
| chat_model_name | qwen3-max | Chat model |

---

## 🔧 Troubleshooting

### Q1: Chat doesn't find relevant information after uploading files?
Check:
- Vector database directory consistency between upload and chat services
- Collection name configuration
- Data directory existence

### Q2: Slow response or no output?
Check:
- Text splitting parameters (chunk_size, chunk_overlap)
- API network connectivity
- Vector database initialization

### Q3: "Invalid link" on buyer page?
Check:
- Missing merchant parameter in URL
- Merchant ID exists and not deleted
- Get complete link from dashboard's "Consultation Links" tab

---

## ✨ Future Enhancements

- **Advanced Rerank**: Improve retrieval quality with LangChain EGE rerank
- **More File Types**: PDF, Markdown, Word support
- **Multi-model Support**: Mix of different LLMs
- **FAISS Integration**: Replace Chroma with FAISS for enterprise-scale
- **Real-time Sync**: Auto-sync product info from e-commerce platforms
- **Conversation Memory**: Enhanced context understanding

---

## 📄 License

MIT License

---

## 🙌 Acknowledgments

- Streamlit
- LangChain
- ChromaDB
- Alibaba Cloud DashScope