# 销售管理系统 (SalesManagerSystem)

## 项目简介

### 销售管理系统是一个基于Flask框架开发的Web应用，用于管理销售数据和用户信息。系统提供用户注册、登录、用户管理等核心功能，采用现代化的界面设计和安全的用户认证机制。

## 技术栈

### 后端技术

- **框架**: Flask 3.0+
- **ORM**: Flask-SQLAlchemy
- **数据库迁移**: Flask-Migrate
- **用户认证**: Flask-Login + 自定义会话管理
- **密码加密**: passlib (pbkdf2\_sha256)
- **表单验证**: Flask-WTF

### 前端技术

- **模板引擎**: Jinja2
- **样式**: 原生CSS (响应式设计)
- **字体**: Google Fonts (Inter)

### 数据库

- **SQLite**: 开发环境默认数据库
- **支持**: 可扩展支持MySQL、PostgreSQL等

### 测试技术

- **单元测试**: pytest
- **覆盖率分析**: pytest-cov
- **UI自动化测试**: Playwright
- **报告生成**: pytest-html

## 功能模块

### 用户管理

- 用户注册 (手机号、邮箱、密码)
- 用户登录 (手机号、密码)
- **用户角色管理** (ADMIN/USER 权限控制)
- **多用户同时登录** (支持浏览器会话隔离)
- 用户列表查看
- 退出登录

### 销售管理

- 待开发：销售数据录入
- 待开发：销售报表生成
- 待开发：数据分析

### 系统功能

- 响应式设计，支持移动端访问
- 安全的密码加密存储
- 会话管理
- 错误处理和用户反馈

## 项目结构

```
SalesManagerSystem/
├── app/
│   ├── __init__.py               # 应用初始化
│   ├── routes.py                 # 路由定义
│   ├── session_manager.py        # 多用户会话管理
│   ├── models/
│   │   ├── user.py               # 用户模型
│   │   └── session.py            # 会话模型
│   ├── forms.py                  # 表单定义
│   ├── templates/                # Jinja2模板
│   │   ├── base.html             # 基础模板
│   │   ├── index.html            # 首页
│   │   ├── login.html            # 登录页面
│   │   ├── register.html         # 注册页面
│   │   ├── user_management.html  # 用户管理页面
│   │   └── change_password.html  # 修改密码页面
│   └── test/                     # 测试目录
│       ├── test_user.py                  # 用户模型单元测试
│       ├── test_routes.py                # 路由功能单元测试
│       ├── test_multi_user_session.py    # 多用户会话单元测试
│       ├── test_browser_isolation.py     # 浏览器隔离单元测试
│       ├── TEST_REPORT.md                # 单元测试报告
│       └── uat/                          # UAT测试目录
│           ├── playwright_test.py        # UI自动化测试
│           ├── test_browser_isolation.py # 浏览器隔离测试
│           ├── pytest.ini                # 测试配置
│           ├── uat_test_report.html      # HTML测试报告
│           └── UAT_TEST_REPORT.md        # Markdown测试报告
├── run.py                   # 应用入口
├── requirements.txt         # 依赖列表
├── README.md                # 项目说明
└── ERROR_SUMMARY.md         # 错误总结
```

## 安装和运行

### 环境要求

- Python 3.8+
- pip

### 安装步骤

1. **克隆仓库**
   ```bash
   git clone <仓库地址>
   cd SalesManagerSystem
   ```
2. **创建虚拟环境**
   ```bash
   python -m venv venv
   ```
3. **激活虚拟环境**
   - Windows: `venv\Scripts\activate`
   - Linux/macOS: `source venv/bin/activate`
4. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```
5. **运行应用**
   ```bash
   python run.py
   ```
6. **访问应用**
   打开浏览器访问：`http://127.0.0.1:5000`

## 测试

### 单元测试

1. **运行所有单元测试**
   ```bash
   python -m pytest app/test/ -v
   ```
2. **生成测试报告**
   ```bash
   python -m pytest app/test/ --cov=app --cov-report=html
   ```

### UI自动化测试

1. **安装Playwright依赖**
   ```bash
   pip install pytest-playwright playwright
   playwright install
   ```
2. **运行UAT测试**
   ```bash
   python -m pytest app/test/uat/ 
   ```
3. **查看测试报告**
   - HTML报告：`app/test/uat/uat_test_report.html`
   - Markdown报告：`app/test/uat/UAT_TEST_REPORT.md`

## 开发说明

### 数据库迁移

项目已集成Flask-Migrate，应用启动时会自动执行迁移：

```bash
# 手动创建迁移（模型变更后）
flask db migrate -m "迁移说明"

# 手动执行迁移
flask db upgrade
```

### 配置文件

当前配置直接在`app/__init__.py`中定义，生产环境建议使用环境变量或配置文件。

主要配置项：

- SECRET\_KEY: 用于会话加密
- SQLALCHEMY\_DATABASE\_URI: 数据库连接字符串
- SQLALCHEMY\_TRACK\_MODIFICATIONS: 禁用修改跟踪以提高性能
- PERMANENT\_SESSION\_LIFETIME: 会话有效期

## 安全说明

1. **密码安全**：使用pbkdf2\_sha256算法加密存储密码
2. **会话管理**：使用自定义多用户会话管理器，支持浏览器会话隔离
3. **表单验证**：使用Flask-WTF进行表单验证
4. **CSRF保护**：默认启用CSRF保护
5. **角色权限**：基于角色的访问控制 (RBAC)，区分ADMIN和USER权限

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request。

## 联系方式

如有问题或建议，请联系项目维护者。

***

**最后更新**: 2026-03-27
