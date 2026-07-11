# 数据库迁移

基于 Alembic 的数据库版本管理，应用启动时自动升级到最新版本。

## 使用方法

```bash
# 生成迁移脚本（检测模型变更）
python -m app.migrations.migrate revision "描述信息"

# 升级到最新版本
python -m app.migrations.migrate upgrade

# 升级到指定版本
python -m app.migrations.migrate upgrade <revision_id>

# 回滚一个版本
python -m app.migrations.migrate downgrade

# 回滚到指定版本
python -m app.migrations.migrate downgrade <revision_id>

# 查看当前版本
python -m app.migrations.migrate current

# 查看迁移历史
python -m app.migrations.migrate history
```

## 目录结构

```
migrations/
├── versions/       # 迁移版本文件
├── env.py          # Alembic 环境配置
├── migrate.py      # 迁移命令入口
└── script.py.mako  # 迁移脚本模板
```

## 自动迁移

应用启动时会自动执行 `upgrade head`，确保数据库结构与代码同步。

## 开发流程

1. 修改 `app/models/` 下的模型
2. 运行 `python -m app.migrations.migrate revision "变更描述"`
3. 检查生成的迁移脚本
4. 启动应用或手动运行 `upgrade`

## 注意事项

- 首次运行前确保数据库已创建
- 迁移脚本需要提交到代码仓库
- 生产环境回滚前请备份数据
