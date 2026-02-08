"""字符串工具"""
from typing import Any

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

def safe_get(data: dict, key: str, default: Any = None) -> Any:
    """安全获取字典值"""
    return data.get(key, default) if data else default
