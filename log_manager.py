"""
修改日志记录模块
用于记录所有对知识库、配置、模型等关键内容的修改操作，方便回溯与问题排查
日志格式：JSON Lines（每行一个 JSON 对象），便于追加和按行解析
"""
import os
import json
from datetime import datetime
from pathlib import Path


# 日志存储目录
LOG_DIR = "./logs"
LOG_FILE = os.path.join(LOG_DIR, "modifications.jsonl")


def _ensure_log_dir():
    """确保日志目录存在"""
    Path(LOG_DIR).mkdir(parents=True, exist_ok=True)
    if not os.path.exists(LOG_FILE):
        # 创建空文件
        open(LOG_FILE, 'a', encoding='utf-8').close()


def log_modification(
    action: str,
    target: str,
    detail: str = "",
    operator: str = "商家",
    extra: dict = None,
):
    """
    记录一次修改操作

    参数:
        action: 操作类型，如 "upload" / "delete" / "update" / "query" / "config_change"
        target: 操作对象，如 "知识库/商品A" / "配置/chunk_size"
        detail: 操作详情描述
        operator: 操作人，默认 "商家"
        extra: 额外信息（字典）
    """
    _ensure_log_dir()
    record = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "action": action,
        "target": target,
        "detail": detail,
        "operator": operator,
    }
    if extra:
        record["extra"] = extra

    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def read_logs(limit: int = 100, action_filter: str = None) -> list:
    """
    读取最近的修改记录

    参数:
        limit: 返回最近多少条
        action_filter: 可选，按操作类型过滤

    返回:
        记录列表（按时间倒序）
    """
    _ensure_log_dir()
    records = []
    if not os.path.exists(LOG_FILE):
        return records

    with open(LOG_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
                if action_filter and record.get("action") != action_filter:
                    continue
                records.append(record)
            except json.JSONDecodeError:
                # 跳过损坏行
                continue

    # 按时间倒序
    records.reverse()
    return records[:limit]


def clear_logs():
    """清空日志（谨慎使用）"""
    _ensure_log_dir()
    open(LOG_FILE, 'w', encoding='utf-8').close()
    log_modification(
        action="clear_logs",
        target="日志文件",
        detail="清空所有历史修改记录",
    )


if __name__ == "__main__":
    # 测试代码
    log_modification("test", "测试对象", "这是一条测试记录")
    logs = read_logs(limit=5)
    for log in logs:
        print(log)
