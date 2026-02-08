from fastapi import HTTPException

class BusinessException(HTTPException):
    """业务异常"""
    def __init__(self, message: str, code: int = 400):
        super().__init__(status_code=code, detail=message)

class NotFoundException(BusinessException):
    """资源不存在"""
    def __init__(self, message: str = "资源不存在"):
        super().__init__(message=message, code=404)

class UnauthorizedException(BusinessException):
    """未授权"""
    def __init__(self, message: str = "未授权"):
        super().__init__(message=message, code=401)

class ForbiddenException(BusinessException):
    """禁止访问"""
    def __init__(self, message: str = "禁止访问"):
        super().__init__(message=message, code=403)
