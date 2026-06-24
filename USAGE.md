# 个人商家 RAG 智能客服系统 - 使用说明

> 面向个人商家的轻量级 AI 客服方案，支持淘宝/抖音/拼多多/微信等多平台

---

## 🎯 适用场景

- 淘宝/天猫/拼多多/抖音小店等个人商家
- 重复性商品咨询自动回复（尺码、材质、洗护、售后等）
- 7×24 小时无人值守
- 无需对接各平台 API，挂二维码即可使用

---

## 🚀 快速开始

### 第 1 步：安装依赖

```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 第 2 步：配置环境变量

设置阿里云通义千问 API Key（Windows PowerShell）：

```powershell
$env:DASHSCOPE_API_KEY = "你的API_KEY"
```

### 第 3 步：初始化项目

```bash
python init_project.py
```

### 第 4 步：启动商家管理后台

```bash
streamlit run app_admin.py
```

浏览器打开 `http://localhost:8501`，按提示操作：
1. 左侧创建你的商家（如"XX 旗舰店"）
2. 添加商品（如"夏季连衣裙"）
3. 上传知识文件（可使用 `assets/示例知识库_常见问题.txt` 测试）

### 第 5 步：启动买家咨询页面

新开一个终端：

```bash
streamlit run app_buyer.py
```

在管理后台【咨询链接】标签页获取链接，挂到商品页。

---

## 📁 项目结构

```
KnowledgeBase-RAG-LLM-System-master/
├─ app_admin.py              # 商家管理后台（新增）
├─ app_buyer.py              # 买家咨询页面（新增）
├─ app_chat.py               # 原有通用聊天页面
├─ app_upload.py             # 原有知识库上传页面
├─ api_server.py             # FastAPI 接口服务（新增）
├─ merchant_manager.py       # 商家/商品管理（新增）
├─ merchant_kb.py            # 多商家知识库（新增）
├─ log_manager.py            # 修改日志（新增）
├─ init_project.py           # 项目初始化（新增）
├─ config_data.py            # 配置文件（已更新）
├─ rag.py                    # RAG 核心
├─ knowledge_base.py         # 知识库处理
├─ vector_stores.py          # 向量库封装
├─ assets/
│  └─ 示例知识库_常见问题.txt    # 示例数据（新增）
├─ merchants/                # 商家数据目录（运行后生成）
├─ logs/                     # 修改日志目录（运行后生成）
└─ requirements.txt          # 依赖清单（已更新）
```

---

## 🔌 对接各平台

### 方式一：通用咨询链接（推荐，最简单）

在管理后台【咨询链接】标签页获取链接，例如：
```
http://你的服务器:8501/?merchant=m_xxx&product=p_xxx
```

挂载方式：
- 淘宝详情图最后一张加"扫码咨询"二维码
- 抖音/拼多多商品详情页加跳转链接
- 包裹里放售后卡片
- 朋友圈/公众号文章中插入

### 方式二：API 对接（进阶）

启动 API 服务：
```bash
uvicorn api_server:app --host 0.0.0.0 --port 8000
```

调用示例（任何语言/平台都能用）：

```python
import requests

response = requests.post("http://你的服务器:8000/api/query", json={
    "merchant_id": "m_xxx",
    "product_id": "p_xxx",  # 可选
    "question": "这件衣服会起球吗？",
    "user_id": "buyer_001"
})

print(response.json()["answer"])
```

---

## 📋 修改日志功能

所有操作自动记录到 `logs/modifications.jsonl`：

| 字段 | 说明 |
|------|------|
| timestamp | 操作时间 |
| action | 操作类型（upload/delete/query 等）|
| target | 操作对象（商家/商品） |
| detail | 操作详情 |
| operator | 操作人 |

在管理后台【修改日志】标签页可视化查看。

---

## ⚙️ 配置说明

### 修改服务地址

部署到云服务器后，编辑 `config_data.py`：

```python
base_url = "http://你的服务器IP:8501"
```

### 修改模型

```python
embedding_model_name = "text-embedding-v4"  # 嵌入模型
chat_model_name = "qwen3-max"               # 对话模型
```

---

## 🛠️ 常见问题

### Q1：买家页面打开后没有回答？
检查 `config_data.py` 中的 `base_url` 是否正确，以及 `DASHSCOPE_API_KEY` 是否配置。

### Q2：知识库检索不到内容？
- 确认在管理后台【知识库上传】中已上传文件
- 商家 ID 和商品 ID 要对应
- 查看【修改日志】确认上传是否成功

### Q3：如何重置某个商家的数据？
删除 `merchants/商家ID/` 目录即可。

### Q4：如何部署到云服务器？
推荐阿里云轻量应用服务器（30-50 元/月）：
1. 购买服务器，选择 Windows 或 Linux
2. 安装 Python 3.10+
3. 上传代码，安装依赖
4. 用 `nohup` 后台运行服务
5. 配置 `base_url` 为服务器 IP

---

## 📞 技术支持

遇到问题可查看：
1. 管理后台【修改日志】
2. `logs/modifications.jsonl` 文件
3. 终端运行的报错信息
