"""编码工具"""
import secrets
import string

def generate_code(length: int = 32) -> str:
    """生成随机码（用于分享链接等）"""
    return secrets.token_hex(length // 2)

def generate_short_code(length: int = 8) -> str:
    """生成短随机码"""
    chars = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))
