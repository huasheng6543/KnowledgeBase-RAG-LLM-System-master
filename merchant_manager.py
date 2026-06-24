"""
商家管理模块
用于管理多个商家/商品分组的信息
支持为不同商家或商品配置独立的知识库
"""
import os
import json
from datetime import datetime
from pathlib import Path


# 商家数据存储目录
MERCHANT_DIR = "./merchants"
MERCHANT_INDEX = os.path.join(MERCHANT_DIR, "index.json")


def _ensure_merchant_dir():
    """确保商家目录存在"""
    Path(MERCHANT_DIR).mkdir(parents=True, exist_ok=True)
    if not os.path.exists(MERCHANT_INDEX):
        # 初始化空的索引文件
        with open(MERCHANT_INDEX, 'w', encoding='utf-8') as f:
            json.dump({"merchants": []}, f, ensure_ascii=False, indent=2)


def list_merchants() -> list:
    """
    列出所有商家

    返回:
        商家列表，每项包含 merchant_id, name, created_at
    """
    _ensure_merchant_dir()
    with open(MERCHANT_INDEX, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data.get("merchants", [])


def get_merchant(merchant_id: str) -> dict:
    """
    根据 ID 获取商家信息

    返回:
        商家信息字典，找不到返回 None
    """
    merchants = list_merchants()
    for m in merchants:
        if m["merchant_id"] == merchant_id:
            return m
    return None


def create_merchant(name: str, description: str = "") -> dict:
    """
    创建新商家

    参数:
        name: 商家名称（你的店铺名/品牌名）
        description: 描述

    返回:
        新创建的商家信息
    """
    _ensure_merchant_dir()
    merchants = list_merchants()

    # 生成唯一 ID
    merchant_id = f"m_{datetime.now().strftime('%Y%m%d%H%M%S')}_{len(merchants) + 1}"

    new_merchant = {
        "merchant_id": merchant_id,
        "name": name,
        "description": description,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "products": [],  # 关联的商品列表
    }

    merchants.append(new_merchant)

    with open(MERCHANT_INDEX, 'w', encoding='utf-8') as f:
        json.dump({"merchants": merchants}, f, ensure_ascii=False, indent=2)

    # 创建商家专属目录
    merchant_path = os.path.join(MERCHANT_DIR, merchant_id)
    Path(merchant_path).mkdir(parents=True, exist_ok=True)
    Path(os.path.join(merchant_path, "knowledge_base")).mkdir(parents=True, exist_ok=True)
    Path(os.path.join(merchant_path, "chat_history")).mkdir(parents=True, exist_ok=True)

    return new_merchant


def add_product(merchant_id: str, product_name: str, description: str = "") -> dict:
    """
    为指定商家添加商品

    参数:
        merchant_id: 商家 ID
        product_name: 商品名称
        description: 商品描述

    返回:
        新创建的商品信息
    """
    _ensure_merchant_dir()
    with open(MERCHANT_INDEX, 'r', encoding='utf-8') as f:
        data = json.load(f)

    for m in data["merchants"]:
        if m["merchant_id"] == merchant_id:
            product_id = f"p_{datetime.now().strftime('%Y%m%d%H%M%S')}_{len(m['products']) + 1}"
            new_product = {
                "product_id": product_id,
                "name": product_name,
                "description": description,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
            m["products"].append(new_product)

            with open(MERCHANT_INDEX, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            # 为商品创建独立知识库目录
            product_path = os.path.join(MERCHANT_DIR, merchant_id, "knowledge_base", product_id)
            Path(product_path).mkdir(parents=True, exist_ok=True)

            return new_product

    return None


def get_product(merchant_id: str, product_id: str) -> dict:
    """根据商家 ID 和商品 ID 获取商品信息"""
    merchant = get_merchant(merchant_id)
    if not merchant:
        return None
    for p in merchant.get("products", []):
        if p["product_id"] == product_id:
            return p
    return None


def update_merchant(merchant_id: str, name: str = None, description: str = None) -> dict:
    """
    更新商家信息

    参数:
        merchant_id: 商家 ID
        name: 新名称（可选）
        description: 新描述（可选）

    返回:
        更新后的商家信息，找不到返回 None
    """
    _ensure_merchant_dir()
    with open(MERCHANT_INDEX, 'r', encoding='utf-8') as f:
        data = json.load(f)

    for m in data["merchants"]:
        if m["merchant_id"] == merchant_id:
            if name is not None:
                m["name"] = name
            if description is not None:
                m["description"] = description

            with open(MERCHANT_INDEX, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            return m

    return None


def delete_merchant(merchant_id: str) -> bool:
    """
    删除商家（及其所有商品和知识库数据）

    参数:
        merchant_id: 商家 ID

    返回:
        是否删除成功
    """
    _ensure_merchant_dir()
    with open(MERCHANT_INDEX, 'r', encoding='utf-8') as f:
        data = json.load(f)

    for i, m in enumerate(data["merchants"]):
        if m["merchant_id"] == merchant_id:
            del data["merchants"][i]

            with open(MERCHANT_INDEX, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            # 删除商家目录（包括知识库）
            import shutil
            merchant_path = os.path.join(MERCHANT_DIR, merchant_id)
            if os.path.exists(merchant_path):
                shutil.rmtree(merchant_path)

            return True

    return False


def update_product(merchant_id: str, product_id: str, name: str = None, description: str = None) -> dict:
    """
    更新商品信息

    参数:
        merchant_id: 商家 ID
        product_id: 商品 ID
        name: 新名称（可选）
        description: 新描述（可选）

    返回:
        更新后的商品信息，找不到返回 None
    """
    _ensure_merchant_dir()
    with open(MERCHANT_INDEX, 'r', encoding='utf-8') as f:
        data = json.load(f)

    for m in data["merchants"]:
        if m["merchant_id"] == merchant_id:
            for p in m["products"]:
                if p["product_id"] == product_id:
                    if name is not None:
                        p["name"] = name
                    if description is not None:
                        p["description"] = description

                    with open(MERCHANT_INDEX, 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)

                    return p

    return None


def delete_product(merchant_id: str, product_id: str) -> bool:
    """
    删除商品（及其知识库数据）

    参数:
        merchant_id: 商家 ID
        product_id: 商品 ID

    返回:
        是否删除成功
    """
    _ensure_merchant_dir()
    with open(MERCHANT_INDEX, 'r', encoding='utf-8') as f:
        data = json.load(f)

    for m in data["merchants"]:
        if m["merchant_id"] == merchant_id:
            for i, p in enumerate(m["products"]):
                if p["product_id"] == product_id:
                    del m["products"][i]

                    with open(MERCHANT_INDEX, 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)

                    # 删除商品知识库目录
                    import shutil
                    product_path = get_product_kb_path(merchant_id, product_id)
                    if os.path.exists(product_path):
                        shutil.rmtree(product_path)

                    return True

    return False


def get_merchant_kb_path(merchant_id: str) -> str:
    """获取商家知识库的 Chroma 持久化路径"""
    return os.path.join(MERCHANT_DIR, merchant_id, "knowledge_base")


def get_product_kb_path(merchant_id: str, product_id: str) -> str:
    """获取商品知识库的 Chroma 持久化路径"""
    return os.path.join(MERCHANT_DIR, merchant_id, "knowledge_base", product_id)


if __name__ == "__main__":
    # 测试代码
    m = create_merchant("测试小店", "这是一个测试店铺")
    print(f"创建商家: {m}")

    p = add_product(m["merchant_id"], "夏季连衣裙", "清新风格连衣裙")
    print(f"添加商品: {p}")

    merchants = list_merchants()
    print(f"所有商家: {merchants}")
