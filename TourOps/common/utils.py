import secrets
import string
from datetime import datetime, date
from typing import Any

def generate_code(length: int = 32) -> str:
    """生成随机码（用于分享链接等）"""
    return secrets.token_hex(length // 2)

def generate_short_code(length: int = 8) -> str:
    """生成短随机码"""
    chars = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))

def format_date(dt: datetime | date, fmt: str = "%Y-%m-%d") -> str:
    """格式化日期"""
    return dt.strftime(fmt) if dt else ""

def format_datetime(dt: datetime, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """格式化日期时间"""
    return dt.strftime(fmt) if dt else ""

def calculate_days(start_date: date, end_date: date) -> int:
    """计算天数"""
    return (end_date - start_date).days + 1

def safe_get(data: dict, key: str, default: Any = None) -> Any:
    """安全获取字典值"""
    return data.get(key, default) if data else default

def to_dict(obj: Any, exclude: list = None) -> dict:
    """对象转字典"""
    exclude = exclude or []
    if hasattr(obj, '__dict__'):
        return {k: v for k, v in obj.__dict__.items() if not k.startswith('_') and k not in exclude}
    return {}

def truncate(text: str, length: int = 100, suffix: str = "...") -> str:
    """截断文本"""
    if not text or len(text) <= length:
        return text or ""
    return text[:length] + suffix

def is_empty(value: Any) -> bool:
    """判断是否为空"""
    if value is None:
        return True
    if isinstance(value, str):
        return len(value.strip()) == 0
    if isinstance(value, (list, dict)):
        return len(value) == 0
    return False
