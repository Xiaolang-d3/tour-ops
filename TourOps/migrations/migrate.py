"""数据库迁移脚本"""
import os
from pathlib import Path
from alembic.config import Config
from alembic import command

def get_alembic_config():
    """获取 Alembic 配置"""
    migrations_dir = Path(__file__).parent
    alembic_cfg = Config()
    alembic_cfg.set_main_option("script_location", str(migrations_dir))
    alembic_cfg.set_main_option("prepend_sys_path", str(migrations_dir.parent.parent))
    
    from TourOps.core.config import settings
    alembic_cfg.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
    return alembic_cfg

def upgrade(revision: str = "head"):
    """升级到指定版本"""
    alembic_cfg = get_alembic_config()
    command.upgrade(alembic_cfg, revision)
    
    # 获取当前实际版本号
    from alembic.runtime.migration import MigrationContext
    from TourOps.core.database import engine
    with engine.connect() as conn:
        context = MigrationContext.configure(conn)
        current_rev = context.get_current_revision()
    print(f"数据库已升级至 {current_rev or '(无迁移)'}")
    
    # 初始化管理员账号
    init_admin()

def init_admin():
    """初始化管理员账号"""
    from sqlalchemy.orm import Session
    from TourOps.core.database import engine
    from TourOps.models.user import User, UserRole
    from TourOps.core.security import get_password_hash
    
    with Session(engine) as db:
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            admin = User(
                username="admin",
                password_hash=get_password_hash("admin123"),
                name="管理员",
                role=UserRole.ADMIN
            )
            db.add(admin)
            db.commit()
            print("已创建初始管理员账号: admin / admin123")

def downgrade(revision: str = "-1"):
    """回滚到指定版本"""
    alembic_cfg = get_alembic_config()
    command.downgrade(alembic_cfg, revision)
    print(f"数据库已回滚至 {revision}")

def revision(message: str = "auto"):
    """生成迁移脚本"""
    alembic_cfg = get_alembic_config()
    command.revision(alembic_cfg, message=message, autogenerate=True)
    print(f"迁移脚本已生成: {message}")

def current():
    """显示当前版本"""
    alembic_cfg = get_alembic_config()
    command.current(alembic_cfg)

def history():
    """显示迁移历史"""
    alembic_cfg = get_alembic_config()
    command.history(alembic_cfg)

if __name__ == "__main__":
    import sys
    args = sys.argv[1:]
    
    if not args or args[0] == "upgrade":
        rev = args[1] if len(args) > 1 else "head"
        upgrade(rev)
    elif args[0] == "downgrade":
        rev = args[1] if len(args) > 1 else "-1"
        downgrade(rev)
    elif args[0] == "revision":
        msg = args[1] if len(args) > 1 else "auto"
        revision(msg)
    elif args[0] == "current":
        current()
    elif args[0] == "history":
        history()
    else:
        print("用法: python -m app.migrations.migrate [upgrade|downgrade|revision|current|history] [参数]")
