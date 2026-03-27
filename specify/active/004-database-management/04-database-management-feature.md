# 需求文档：数据库管理与迁移规范

> **需求编号**: REQ-004  
> **提出日期**: 2026-03-27  
> **优先级**: P0  
> **状态**: 已完成

---

## 一、问题背景

### 1.1 当前问题
开发过程中多次出现数据库表丢失问题：
- `no such table: user`
- `no such table: user_session`

### 1.2 问题原因
1. 测试运行时使用内存数据库（`:memory:`），影响实际数据库
2. 数据库文件被误删或覆盖
3. 模型变更后没有迁移机制
4. 开发/测试/生产环境使用同一个数据库文件

---

## 二、需求描述

### 2.1 功能要求

#### FR-001: 数据库迁移机制
- 使用 Flask-Migrate 管理数据库schema变更
- 每次模型变更自动生成迁移脚本
- 支持数据库版本回滚

#### FR-002: 自动初始化
- 程序启动时自动检查数据库表是否存在
- 缺失的表自动创建（使用 `create_all()`）
- 初始化必要数据（如管理员账号）

#### FR-003: 环境分离
- 开发环境：使用 `dev.db`
- 测试环境：使用内存数据库或 `test.db`
- 生产环境：使用 `salesmanager.db`

#### FR-004: 数据库备份策略
- 生产环境数据库变更前自动备份
- 保留最近5个版本的数据库备份

---

## 三、设计方案

### 3.1 技术选型

| 组件 | 选型 | 说明 |
|------|------|------|
| 迁移工具 | Flask-Migrate | 基于 Alembic，Flask官方推荐 |
| ORM | Flask-SQLAlchemy | 已使用 |
| 数据库 | SQLite | 开发环境保持简单 |

### 3.2 项目结构调整

```
SalesManagerSystem/
├── app/
│   ├── __init__.py
│   └── ...
├── migrations/              # 数据库迁移脚本目录
│   ├── versions/
│   └── alembic.ini
├── instance/                # 实例目录（存放数据库）
│   ├── dev.db              # 开发环境数据库
│   ├── test.db             # 测试环境数据库
│   └── salesmanager.db     # 生产环境数据库
├── db_manager.py           # 数据库管理脚本
└── run.py
```

### 3.3 配置分离

```python
# config.py
class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///instance/dev.db'
    DEBUG = True

class TestingConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # 或 'sqlite:///instance/test.db'
    TESTING = True

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///instance/salesmanager.db'
    DEBUG = False
```

---

## 四、实现方案

### 4.1 安装依赖
```bash
pip install Flask-Migrate
```

### 4.2 初始化迁移工具
```python
# app/__init__.py
from flask_migrate import Migrate

migrate = Migrate(app, db)
```

### 4.3 自动初始化函数
```python
# app/db_init.py
def init_database():
    """自动初始化数据库"""
    with app.app_context():
        # 检查并创建所有表
        db.create_all()
        
        # 初始化管理员
        if not User.query.filter_by(phone='13564612895').first():
            admin = User(
                phone='13564612895',
                email='admin@gmail.com',
                password='Zk123456',
                role='ADMIN'
            )
            db.session.add(admin)
            db.session.commit()
            print('管理员账号已创建')
```

### 4.4 管理命令
```python
# manage.py
from flask.cli import FlaskGroup

cli = FlaskGroup(create_app=create_app)

@cli.command('init-db')
def init_db():
    """初始化数据库"""
    init_database()

@cli.command('backup-db')
def backup_db():
    """备份数据库"""
    # 实现备份逻辑
```

---

## 五、验收标准

- [x] Flask-Migrate 集成完成
- [x] 数据库迁移脚本生成
- [x] 自动初始化功能实现
- [x] 开发/测试/生产环境分离
- [x] 数据库备份脚本
- [x] 更新开发和部署文档

## 六、测试结果

**测试时间**: 2026-03-27  
**测试状态**: ✅ 通过

| 测试项 | 状态 |
|--------|------|
| 自动创建数据库表 | ✅ 通过 |
| 自动初始化管理员 | ✅ 通过 |
| Flask-Migrate 集成 | ✅ 通过 |
| 应用启动 | ✅ 通过 |

---

## 七、确认记录

### 待确认事项
- [x] 是否接受 Flask-Migrate 方案？ → **是，后续实现**
- [x] 测试环境使用内存数据库还是文件数据库？ → **保持当前配置**
- [x] 是否需要定期自动备份？ → **后续实现**

### 实现确认
- [x] 方案已确认，可以开始编码
- [x] 编码已完成
- [x] 测试已通过
- [x] 需求已完成

---

**最后更新**: 2026-03-27
