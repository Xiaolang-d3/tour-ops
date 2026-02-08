from typing import Any, List, TypeVar, Generic
from pydantic import BaseModel

T = TypeVar('T')

class Response(BaseModel, Generic[T]):
    code: int = 200
    message: str = "success"
    data: T | None = None

class PageData(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    page_size: int

def success(data: Any = None, message: str = "success") -> dict:
    return {"code": 200, "message": message, "data": data}

def error(message: str = "error", code: int = 400) -> dict:
    return {"code": code, "message": message, "data": None}

def paginate(items: list, total: int, page: int, page_size: int) -> dict:
    return success(data={
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size
    })
