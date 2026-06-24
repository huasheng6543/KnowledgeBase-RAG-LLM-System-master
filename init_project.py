"""
项目初始化脚本
首次使用时运行，用于创建必要的目录结构和示例数据
"""
import os
from pathlib import Path


def init_project():
    """初始化项目目录结构"""
    dirs_to_create = [
        "./logs",
        "./merchants",
        "./chroma_db",
        "./chat_history",
    ]

    for d in dirs_to_create:
        Path(d).mkdir(parents=True, exist_ok=True)
        print(f"✓ 创建目录: {d}")

    # 创建 .gitkeep 文件，确保空目录也被版本管理
    for d in dirs_to_create:
        gitkeep = os.path.join(d, ".gitkeep")
        if not os.path.exists(gitkeep):
            open(gitkeep, 'w').close()

    print("\n✅ 项目初始化完成！")
    print("\n下一步：")
    print("1. 配置环境变量：设置 DASHSCOPE_API_KEY")
    print("2. 运行商家管理后台：streamlit run app_admin.py")
    print("3. 在管理后台创建商家和商品")
    print("4. 上传常见问题 TXT 文件")
    print("5. 生成买家咨询链接，挂在各平台商品页")


if __name__ == "__main__":
    init_project()
