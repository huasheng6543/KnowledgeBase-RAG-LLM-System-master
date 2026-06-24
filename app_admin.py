"""
商家管理后台
用于管理商家、商品、上传知识库、查看修改日志
面向商家本人使用
"""
import streamlit as st
from merchant_manager import (
    list_merchants,
    create_merchant,
    add_product,
    get_merchant,
    update_merchant,
    delete_merchant,
    update_product,
    delete_product,
)
from merchant_kb import MerchantKnowledgeBase
from log_manager import read_logs, clear_logs
import config_data as config


st.set_page_config(
    page_title="商家管理后台",
    page_icon="🏪",
    layout="wide",
)


# ========== 初始化 session_state ==========
if "current_merchant" not in st.session_state:
    st.session_state["current_merchant"] = None
if "current_product" not in st.session_state:
    st.session_state["current_product"] = None


# ========== 侧边栏：商家选择 ==========
st.sidebar.title("🏪 商家管理")

merchants = list_merchants()
merchant_options = ["-- 新建商家 --"] + [f"{m['name']} ({m['merchant_id']})" for m in merchants]

# 计算选中索引
default_index = 0
if st.session_state["current_merchant"]:
    for i, m in enumerate(merchants):
        if m["merchant_id"] == st.session_state["current_merchant"]:
            default_index = i + 1  # +1 因为第一个是"新建商家"选项
            break

selected = st.sidebar.selectbox(
    "选择商家",
    merchant_options,
    index=default_index,
)

if selected == "-- 新建商家 --":
    st.session_state["current_merchant"] = None
    st.sidebar.subheader("➕ 新建商家")
    new_name = st.sidebar.text_input("商家名称")
    new_desc = st.sidebar.text_input("商家描述（可选）")
    if st.sidebar.button("创建商家"):
        if new_name.strip():
            m = create_merchant(new_name.strip(), new_desc.strip())
            st.session_state["current_merchant"] = m["merchant_id"]
            st.sidebar.success(f"已创建商家：{m['name']}")
            st.rerun()
        else:
            st.sidebar.error("请填写商家名称")
elif selected:
    merchant_id = selected.split("(")[-1].rstrip(")")
    st.session_state["current_merchant"] = merchant_id

    m = get_merchant(merchant_id)
    if m:
        st.sidebar.divider()
        st.sidebar.subheader("✏️ 编辑商家")
        edit_name = st.sidebar.text_input("商家名称", value=m["name"], key="edit_merchant_name")
        edit_desc = st.sidebar.text_input("商家描述", value=m["description"], key="edit_merchant_desc")
        if st.sidebar.button("保存修改"):
            if edit_name.strip():
                update_merchant(merchant_id, edit_name.strip(), edit_desc.strip())
                st.sidebar.success("已更新")
                st.rerun()
            else:
                st.sidebar.error("请填写商家名称")

        st.sidebar.divider()
        if "confirm_del_merchant" not in st.session_state:
            st.session_state["confirm_del_merchant"] = False

        if st.session_state["confirm_del_merchant"]:
            st.sidebar.warning("⚠️ 确定要删除商家吗？此操作不可撤销！")
            col_confirm, col_cancel = st.sidebar.columns(2)
            with col_confirm:
                if st.sidebar.button("✅ 确定删除", type="primary"):
                    delete_merchant(merchant_id)
                    st.session_state["current_merchant"] = None
                    st.session_state["confirm_del_merchant"] = False
                    st.sidebar.success("已删除")
                    st.rerun()
            with col_cancel:
                if st.sidebar.button("❌ 取消"):
                    st.session_state["confirm_del_merchant"] = False
        else:
            if st.sidebar.button("🗑️ 删除商家", type="secondary"):
                st.session_state["confirm_del_merchant"] = True
                st.rerun()
else:
    st.session_state["current_merchant"] = None


# ========== 主界面 ==========
st.title("🏪 个人商家 RAG 知识库管理")
st.divider()

if not st.session_state["current_merchant"]:
    st.info("👈 请在左侧选择或创建一个商家")
    st.markdown("""
    ### 使用说明
    1. **创建商家**：填写你的店铺/品牌名，每个商家数据独立
    2. **添加商品**：为你的商品（如"夏季连衣裙"）建立独立知识库
    3. **上传知识**：上传商品介绍、尺码表、常见问题等 TXT 文件
    4. **生成链接**：为每个商品生成买家咨询页面链接，挂到淘宝/抖音/拼多多商品详情
    5. **查看日志**：所有修改自动记录，方便回溯问题
    """)
else:
    current_merchant = get_merchant(st.session_state["current_merchant"])
    st.subheader(f"📌 当前商家：{current_merchant['name']}")

    # ====== 标签页 ======
    tab1, tab2, tab3, tab4 = st.tabs(["📦 商品管理", "📤 知识库上传", "🔗 咨询链接", "📋 修改日志"])

    # ---------- Tab1: 商品管理 ----------
    with tab1:
        st.subheader("商品列表")
        products = current_merchant.get("products", [])
        if products:
            for p in products:
                with st.expander(f"📦 {p['name']} ({p['product_id']})"):
                    st.write(f"**创建时间**：{p['created_at']}")
                    st.write(f"**描述**：{p['description'] or '无'}")

                    col1, col2 = st.columns(2)
                    with col1:
                        edit_p_name = st.text_input(
                            "编辑名称", value=p["name"], key=f"edit_p_name_{p['product_id']}"
                        )
                    with col2:
                        edit_p_desc = st.text_input(
                            "编辑描述", value=p["description"], key=f"edit_p_desc_{p['product_id']}"
                        )

                    btn_col1, btn_col2 = st.columns(2)
                    with btn_col1:
                        if st.button(f"💾 保存", key=f"save_p_{p['product_id']}"):
                            if edit_p_name.strip():
                                update_product(
                                    st.session_state["current_merchant"],
                                    p["product_id"],
                                    edit_p_name.strip(),
                                    edit_p_desc.strip(),
                                )
                                st.success(f"已更新：{edit_p_name}")
                                st.rerun()
                            else:
                                st.error("请填写商品名称")

                    with btn_col2:
                        if f"confirm_del_{p['product_id']}" not in st.session_state:
                            st.session_state[f"confirm_del_{p['product_id']}"] = False

                        if st.session_state[f"confirm_del_{p['product_id']}"]:
                            st.warning(f"⚠️ 确定要删除 {p['name']} 吗？此操作不可撤销！")
                            col_confirm, col_cancel = st.columns(2)
                            with col_confirm:
                                if st.button(f"✅ 确定删除", key=f"do_del_{p['product_id']}", type="primary"):
                                    delete_product(st.session_state["current_merchant"], p["product_id"])
                                    st.session_state[f"confirm_del_{p['product_id']}"] = False
                                    st.success("已删除")
                                    st.rerun()
                            with col_cancel:
                                if st.button(f"❌ 取消", key=f"cancel_del_{p['product_id']}"):
                                    st.session_state[f"confirm_del_{p['product_id']}"] = False
                        else:
                            if st.button(f"🗑️ 删除", key=f"del_p_{p['product_id']}", type="secondary"):
                                st.session_state[f"confirm_del_{p['product_id']}"] = True
                                st.rerun()
        else:
            st.info("还没有商品，请在下方添加")

        st.divider()
        st.subheader("➕ 添加新商品")
        col1, col2 = st.columns(2)
        with col1:
            product_name = st.text_input("商品名称", key="new_product_name")
        with col2:
            product_desc = st.text_input("商品描述（可选）", key="new_product_desc")
        if st.button("添加商品", key="add_product_btn"):
            if product_name.strip():
                p = add_product(st.session_state["current_merchant"], product_name.strip(), product_desc.strip())
                if p:
                    st.success(f"已添加商品：{p['name']}")
                    st.rerun()
            else:
                st.error("请填写商品名称")

    # ---------- Tab2: 知识库上传 ----------
    with tab2:
        st.subheader("上传知识文件")

        products = current_merchant.get("products", [])

        if not products:
            st.warning("请先在【商品管理】中添加商品")
        else:
            # 选择商品
            product_options = [f"{p['name']} ({p['product_id']})" for p in products]
            product_options.insert(0, "-- 商家通用知识库 --")
            selected_product = st.selectbox("选择目标商品", product_options)

            target_product_id = None
            if selected_product != "-- 商家通用知识库 --":
                target_product_id = selected_product.split("(")[-1].rstrip(")")

            # 文件上传
            uploaded_file = st.file_uploader(
                "选择 TXT 文件",
                type=["txt"],
                help="请上传纯文本文件，常见问题、商品介绍、尺码表等都行",
            )

            # 或者直接输入文本
            st.divider()
            st.markdown("**或者直接粘贴文本**")
            direct_text = st.text_area(
                "文本内容",
                height=200,
                placeholder="例如：Q: 这件衣服会起球吗？A: 不会...",
            )
            direct_name = st.text_input("文本名称", value="手动输入")

            if st.button("🚀 上传", key="upload_btn"):
                kb = MerchantKnowledgeBase(
                    st.session_state["current_merchant"],
                    target_product_id,
                )
                if uploaded_file is not None:
                    content = uploaded_file.read().decode("utf-8")
                    result = kb.upload_text(content, uploaded_file.name)
                    st.success(result)
                elif direct_text.strip():
                    result = kb.upload_text(direct_text.strip(), direct_name or "手动输入")
                    st.success(result)
                else:
                    st.error("请上传文件或粘贴文本")

    # ---------- Tab3: 咨询链接 ----------
    with tab3:
        st.subheader("买家咨询链接")
        st.info("""
        复制下面的链接，生成二维码后可以挂到：
        - 淘宝/天猫商品详情图
        - 抖音/拼多多商品页面
        - 包裹里的售后卡片
        - 微信朋友圈 / 公众号
        """)

        products = current_merchant.get("products", [])

        # 通用链接（无商品）
        st.markdown("**🔗 商家通用咨询链接**")
        st.code(f"{config.buyer_base_url}/?merchant={st.session_state['current_merchant']}", language="text")

        st.divider()

        # 各商品链接
        if products:
            st.markdown("**🔗 各商品咨询链接**")
            for p in products:
                st.markdown(f"📦 **{p['name']}**")
                st.code(
                    f"{config.buyer_base_url}/?merchant={st.session_state['current_merchant']}&product={p['product_id']}",
                    language="text",
                )
        else:
            st.info("添加商品后会显示对应的咨询链接")

        st.divider()
        st.warning("""
        ⚠️ 注意：`config.buyer_base_url` 默认为 `http://localhost:8502`
        部署到云服务器后，需要修改 `config_data.py` 中的 `buyer_base_url` 为你的实际域名或IP
        """)

    # ---------- Tab4: 修改日志 ----------
    with tab4:
        st.subheader("修改日志")
        st.caption("所有上传、删除、配置修改等操作都会被自动记录")

        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("🗑️ 清空日志", type="secondary"):
                clear_logs()
                st.success("已清空")
                st.rerun()

        # 显示日志
        logs = read_logs(limit=200)
        if logs:
            for log in logs:
                with st.container():
                    cols = st.columns([1, 1, 2, 3])
                    cols[0].write(f"🕐 {log['timestamp']}")
                    cols[1].write(f"**{log['action']}**")
                    cols[2].write(log['target'])
                    cols[3].write(log['detail'])
                    st.divider()
        else:
            st.info("暂无日志")
