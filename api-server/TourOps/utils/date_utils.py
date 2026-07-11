"""日期工具"""
from datetime import datetime, date

def format_date(dt: datetime | date, fmt: str = "%Y-%m-%d") -> str:
    """格式化日期"""
    return dt.strftime(fmt) if dt else ""

def format_datetime(dt: datetime, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """格式化日期时间"""
    return dt.strftime(fmt) if dt else ""

def calculate_days(start_date: date, end_date: date) -> int:
    """计算天数"""
    return (end_date - start_date).days + 1

def today() -> date:
    """获取今天日期"""
    return date.today()

def now() -> datetime:
    """获取当前时间"""
    return datetime.now()
