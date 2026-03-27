#!/usr/bin/env python
"""
数据库管理脚本

使用方法:
    python manage.py db init      # 初始化迁移环境（只需执行一次）
    python manage.py db migrate   # 生成迁移脚本
    python manage.py db upgrade   # 执行数据库升级
    python manage.py db downgrade # 数据库回滚
    python manage.py init-db      # 初始化数据库和数据
    python manage.py backup       # 备份数据库
"""
from flask.cli import FlaskGroup
from app import app, db
from app.db_init import init_database
import shutil
import os
from datetime import datetime

cli = FlaskGroup(create_app=lambda: app)


@cli.command('init-db')
def init_db():
    """初始化数据库（创建表+初始化数据）"""
    print("🔧 初始化数据库...")
    init_database()
    print("✅ 数据库初始化完成")


@cli.command('backup')
def backup_db():
    """备份数据库"""
    db_path = 'salesmanager.db'
    if not os.path.exists(db_path):
        print(f"❌ 数据库文件不存在: {db_path}")
        return
    
    # 创建 backups 目录
    backup_dir = 'backups'
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    # 生成备份文件名
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = os.path.join(backup_dir, f'salesmanager_backup_{timestamp}.db')
    
    # 复制数据库文件
    shutil.copy2(db_path, backup_file)
    print(f"✅ 数据库已备份到: {backup_file}")
    
    # 清理旧备份（保留最近5个）
    backups = sorted([f for f in os.listdir(backup_dir) if f.startswith('salesmanager_backup_')])
    if len(backups) > 5:
        for old_backup in backups[:-5]:
            os.remove(os.path.join(backup_dir, old_backup))
            print(f"🗑️  清理旧备份: {old_backup}")


if __name__ == '__main__':
    cli()
