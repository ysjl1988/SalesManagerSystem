# AGENTS.md - 销售管理系统 (SalesManagerSystem)

> 本文档面向AI编码助手，提供项目背景、架构、开发规范等关键信息。

---

## ⚠️ 启动必读（每次会话开始前）

每次启动处理本项目任务时，**必须**先阅读以下文档：

### 1. 研发流程与约束规范
| 文档 | 路径 | 说明 |
|------|------|------|
| 需求文档管理看板 | `specify/README.md` | 活跃需求列表、需求状态追踪 |
| 智能体开发约束规范 | `specify/AGENT_CONSTRAINTS.md` | **5条核心约束**：中文优先、文档先行、文档驱动编码、自动验收、复杂任务分解 |

### 2. 活跃需求文档（specify/active/）
```
specify/active/
├── 001-password-toggle/01-password-toggle-feature.md         # 密码显示/隐藏
├── 002-user-role-system/02-user-role-system-feature.md       # 用户角色权限
├── 003-multi-user-login/03-multi-user-login-feature.md       # 多用户登录
├── 004-database-management/04-database-management-feature.md # 数据库管理
└── 005-comic-downloader/05-comic-downloader-feature.md       # 漫画下载器
```

### 3. 文档先行原则
> **任何需求开发都必须先进行文档编写，经用户确认后再进行编码。**

开发流程：
```
用户提出需求
    ↓
阅读 specify/AGENT_CONSTRAINTS.md（确保理解约束规范）
    ↓
阅读 specify/README.md（了解当前活跃需求）
    ↓
创建/更新需求文档（specify/active/XXX-需求名称/）
    ↓
与用户讨论确认
    ↓
文档定稿，开始编码
    ↓
自动生成/更新测试案例并验收
```

---

## 项目概述

销售管理系统是一个基于Flask框架开发的Web应用，用于管理销售数据和用户信息。系统目前提供用户注册、登录、用户管理等核心功能，采用现代化的界面设计和安全的用户认证机制。

### 主要功能
- 用户注册（手机号、邮箱、密码）
- 用户登录（手机号、密码）
- 用户列表查看（支持搜索和分页）
- 退出登录
- **漫画下载器**（管理员功能）：支持爬取、查看、打包下载漫画
- **测试漫画网站**：用于测试漫画下载功能的模拟站点

---

## 技术栈

### 后端
- **框架**: Flask 3.0+
- **ORM**: Flask-SQLAlchemy
- **用户认证**: Flask-Login
- **密码加密**: passlib (pbkdf2_sha256)
- **表单验证**: Flask-WTF + WTForms

### 前端
- **模板引擎**: Jinja2
- **样式**: 原生CSS（响应式设计，内联在base.html中）
- **字体**: Google Fonts (Inter)

### 数据库
- **开发环境**: SQLite
- **生产环境**: 可扩展支持MySQL、PostgreSQL等

### 测试
- **单元测试**: pytest
- **覆盖率分析**: pytest-cov
- **UI自动化测试**: Playwright
- **报告生成**: pytest-html

---

## 项目结构

```
SalesManagerSystem/
├── app/                          # 应用主目录
│   ├── __init__.py               # Flask应用初始化、配置、扩展实例化
│   ├── routes.py                 # 路由定义（首页、注册、登录、用户管理、退出）
│   ├── forms.py                  # WTForms表单定义（注册、登录表单）
│   ├── models/                   # 数据模型目录
│   │   └── user.py               # User模型（用户数据、密码加密、验证）
│   ├── templates/                # Jinja2模板目录
│   │   ├── base.html             # 基础模板（布局、导航、样式）
│   │   ├── index.html            # 首页模板
│   │   ├── login.html            # 登录页面模板
│   │   ├── register.html         # 注册页面模板
│   │   └── user_management.html  # 用户管理页面模板
│   └── test/                     # 测试目录
│       ├── test_user.py          # 用户模型单元测试
│       ├── test_routes.py        # 路由功能单元测试
│       ├── TEST_REPORT.md        # 单元测试报告
│       └── uat/                  # UAT测试目录
│           ├── playwright_test.py # UI自动化测试
│           ├── pytest.ini         # UAT测试配置
│           ├── uat_test_report.html # HTML测试报告
│           └── UAT_TEST_REPORT.md   # Markdown测试报告
├── run.py                        # 应用入口文件
├── requirements.txt              # Python依赖列表
├── README.md                     # 项目说明文档
├── sequence.md                   # 功能调用链路文档（Mermaid序列图）
└── ERROR_SUMMARY.md              # 错误总结与经验教训
```

---

## 构建和运行

### 环境要求
- Python 3.8+
- pip

### 安装依赖

```bash
# 创建虚拟环境（推荐）
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 运行应用

```bash
python run.py
```

应用将运行在 `http://127.0.0.1:5000`

### 测试漫画网站

项目内置测试漫画网站（集成在Flask应用中）：

- **访问地址**: `http://127.0.0.1:5000/test_comic/`
- **用途**: 用于测试漫画下载器功能
- **内容**: 模拟漫画《肉包子打狗一去不回》，共16页
- **文件位置**: `test_comic_site/` 目录

> 注意：测试漫画网站通过Flask蓝图提供，无需额外启动服务。

### 默认测试数据

`run.py` 启动时会自动创建20条测试用户数据（手机号：13800000001 ~ 13800000020，密码：Zk123456）。

---

## 配置说明

当前配置直接在 `app/__init__.py` 中定义：

```python
app.config['SECRET_KEY'] = 'your-secret-key-here'              # 会话加密密钥
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///salesmanager.db'  # 数据库URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False           # 禁用修改跟踪
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(days=1)  # 会话有效期
```

**生产环境注意**: 建议将 `SECRET_KEY` 改为环境变量读取，不要硬编码在代码中。

---

## 测试指令

### 单元测试

```bash
# 运行所有单元测试
python -m pytest app/test/ -v

# 运行单个测试文件
python -m pytest app/test/test_user.py -v
python -m pytest app/test/test_routes.py -v

# 生成覆盖率报告
python -m pytest app/test/ --cov=app --cov-report=html
```

### UI自动化测试 (Playwright)

**前置条件**: 确保应用已在 `http://127.0.0.1:5000` 运行

```bash
# 安装Playwright依赖（如未安装）
pip install pytest-playwright playwright
playwright install

# 运行UAT测试
cd app/test/uat
python -m pytest playwright_test.py

# 或从项目根目录运行
python -m pytest app/test/uat/ -c app/test/uat/pytest.ini
```

**测试报告位置**:
- HTML报告: `app/test/uat/uat_test_report.html`
- Markdown报告: `app/test/uat/UAT_TEST_REPORT.md`

---

## 代码规范

### Python代码风格
- 遵循PEP 8规范
- 使用4空格缩进
- 类名使用驼峰命名法（如 `User`, `RegistrationForm`）
- 函数和变量使用小写下划线命名法（如 `create_test_users`, `user_count`）
- 注释使用中文（与项目文档保持一致）

### 项目特定约定

#### 1. 模型层 (app/models/)
- 所有模型继承自 `db.Model`
- 用户模型使用 `UserMixin` 支持Flask-Login
- 密码使用 `pbkdf2_sha256` 加密，不允许明文读取
- 时间字段使用 `datetime.utcnow()`（注意：SQLAlchemy 2.0+建议使用带时区的datetime）

#### 2. 表单层 (app/forms.py)
- 所有表单继承自 `FlaskForm`
- 手机号验证使用正则: `^1[3-9]\d{9}$`
- 密码验证要求: 长度7-20位，必须包含大小写字母和数字
- 表单字段标签使用中文

#### 3. 路由层 (app/routes.py)
- 使用装饰器定义路由
- 受保护的路由使用 `@login_required`
- 使用 `flash()` 进行消息提示，支持分类（success, danger）
- 表单提交成功后使用 `redirect(url_for(...))` 防止重复提交

#### 4. 模板层 (app/templates/)
- 所有模板继承自 `base.html`
- 使用 `{% block content %}` 定义内容区域
- 导航栏根据 `current_user.is_authenticated` 动态显示
- 样式内联在base.html中，使用现代CSS设计

---

## 数据库模型

### User 模型

```python
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(20), unique=True, nullable=False)      # 手机号，唯一
    email = db.Column(db.String(120), unique=True, nullable=False)     # 邮箱，唯一
    password_hash = db.Column(db.String(128), nullable=False)          # 密码哈希
    registered_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)  # 注册时间
    last_login_at = db.Column(db.DateTime, nullable=True)              # 最后登录时间
```

**注意**: 密码通过 `@password.setter` 自动加密，通过 `verify_password()` 方法验证。

---

## 安全注意事项

1. **密码安全**: 使用 `pbkdf2_sha256` 算法加密存储密码，不可逆
2. **会话管理**: 使用Flask的会话管理机制，密钥通过 `SECRET_KEY` 配置
3. **表单验证**: 使用Flask-WTF进行服务器端表单验证
4. **CSRF保护**: 默认启用CSRF保护（测试环境可禁用）
5. **SQL注入防护**: 使用SQLAlchemy ORM，自动参数化查询

---

## 已知问题与改进建议

### 当前警告（来自测试报告）
1. `datetime.utcnow()` 已弃用，建议使用带时区的datetime对象
2. SQLAlchemy 2.0+ 中 `Query.get()` 方法已弃用，建议使用 `Session.get()`

### 待开发功能
- 销售数据录入模块
- 销售报表生成功能
- 数据分析功能

---

## 参考文档

### 项目文档
- `README.md`: 项目说明和使用指南
- `sequence.md`: 功能调用链路图（Mermaid序列图）
- `ERROR_SUMMARY.md`: 测试开发错误总结与经验教训

### 测试报告
- `app/test/TEST_REPORT.md`: 单元测试报告
- `app/test/uat/UAT_TEST_REPORT.md`: UAT测试报告

### 需求与流程规范（⚠️ 开发前必读）
- `specify/README.md`: 需求文档管理看板，活跃需求状态追踪
- `specify/AGENT_CONSTRAINTS.md`: 智能体开发约束规范（5条核心约束）
- `specify/active/`: 活跃需求详细文档目录

---

## 许可证

MIT License

---

**最后更新**: 2026-04-02
