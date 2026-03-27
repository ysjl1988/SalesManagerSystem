# 需求文档：用户角色与权限管理系统

> **需求编号**: REQ-002  
> **提出日期**: 2026-03-27  
> **优先级**: P0  
> **状态**: 已完成

---

## 一、需求描述

### 1.1 背景
当前系统所有用户权限相同，无法区分管理员和普通用户。需要引入角色机制，实现分级权限管理。

### 1.2 功能要求

#### FR-001: 用户角色定义
- 系统支持两种角色：**管理员(ADMIN)** 和 **普通用户(USER)**
- 通过注册进来的用户默认都是 **普通用户**

#### FR-002: 初始管理员账号
- 程序启动时自动创建一个管理员账号
- 账号信息：
  - 手机号：`13564612895`
  - 邮箱：`admin@gmail.com`
  - 密码：`Zk123456`
  - 角色：**管理员**

#### FR-003: 管理员功能
- 管理员可以访问 **用户管理页面**
- 管理员可以在用户管理页面 **删除普通用户**（逻辑删除，非物理删除）
- 管理员可以为普通用户 **重置密码**（重置为 `111111`）

#### FR-003-1: 逻辑删除约束（通用规范）
- **所有数据库表的删除操作都必须是逻辑删除**
- 逻辑删除实现方式：添加 `is_deleted` 字段（Boolean，默认 False）
- 删除时将 `is_deleted` 设为 True，而不是物理删除记录
- 查询时默认过滤 `is_deleted=False` 的记录
- **特殊情况需要物理删除时，必须和用户确认后才能执行**
- 用户管理页面显示用户时，默认不显示已删除用户

#### FR-004: 普通用户限制
- 普通用户 **不能访问用户管理页面**
- 尝试访问时应该被重定向到首页或显示无权限提示

#### FR-005: 强制修改密码
- 被管理员重置密码的普通用户，**首次登录必须修改密码**
- 修改密码后才能正常访问页面
- 强制修改密码页面只显示密码修改表单，无其他导航

### 1.3 验收标准

- [x] 数据库用户表包含角色字段（role）和逻辑删除字段（is_deleted）
- [x] 程序启动时自动创建管理员账号（如果不存在）
- [x] 管理员可以正常登录并访问用户管理页面
- [x] 普通用户注册时角色默认为 USER
- [x] 普通用户访问用户管理页面被拦截（重定向/提示）
- [x] 管理员可以在用户管理页面**逻辑删除**普通用户（is_deleted=True）
- [x] 管理员可以在用户管理页面为普通用户重置密码
- [x] 被重置密码的普通用户首次登录被强制要求修改密码
- [x] 密码修改成功后才能正常访问系统
- [x] 用户查询默认过滤已删除用户（is_deleted=False）
- [x] 添加相关单元测试和UI测试

---

## 二、设计方案

### 2.1 数据库设计

#### 用户表扩展
在现有 `user` 表基础上增加字段：

```python
class User(UserMixin, db.Model):
    # 现有字段...
    role = db.Column(db.String(20), nullable=False, default='USER')  # ADMIN/USER
    password_reset_required = db.Column(db.Boolean, nullable=False, default=False)  # 是否需要强制修改密码
    is_deleted = db.Column(db.Boolean, nullable=False, default=False)  # 逻辑删除标记
```

#### 字段说明
| 字段名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| role | String(20) | 'USER' | 用户角色：ADMIN 或 USER |
| password_reset_required | Boolean | False | 是否需要强制修改密码 |
| is_deleted | Boolean | False | 逻辑删除标记：True表示已删除 |

### 2.2 权限控制设计

#### 装饰器设计
创建权限检查装饰器：

```python
def admin_required(f):
    """要求管理员权限"""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if current_user.role != 'ADMIN':
            flash('您没有权限访问此页面', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function
```

#### 路由保护
- `/user_management` - 使用 `@admin_required` 装饰器
- `/reset_password/<user_id>` - 使用 `@admin_required` 装饰器
- `/delete_user/<user_id>` - 使用 `@admin_required` 装饰器

### 2.3 强制修改密码流程

```
用户登录
    ↓
检查 password_reset_required
    ↓ 为 True
重定向到强制修改密码页面
    ↓
提交新密码
    ↓
更新密码，设置 password_reset_required = False
    ↓
重定向到首页
```

### 2.4 UI 设计

#### 用户管理页面（管理员）
```
┌─────────────────────────────────────────────────────────┐
│ 用户管理                                      [退出登录] │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ ┌─────────────┐  ┌─────────────┐                        │
│ │ 搜索用户... │  │ 🔍 搜索     │                        │
│ └─────────────┘  └─────────────┘                        │
│                                                         │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ 手机号        │ 邮箱          │ 角色    │ 操作      │ │
│ ├─────────────────────────────────────────────────────┤ │
│ │ 13800000001   │ user1@test.com│ USER    │ [重置] [删]│ │
│ │ 13564612895   │ admin@test.com│ ADMIN   │ -         │ │
│ │ 13800000003   │ user3@test.com│ USER    │ [重置] [删]│ │
│ └─────────────────────────────────────────────────────┘ │
│                                                         │
│ 第 1 页，共 3 页                              [<] [>]  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

#### 强制修改密码页面
```
┌───────────────────────────────────┐
│ 销售管理系统                       │
├───────────────────────────────────┤
│                                   │
│   🔒 修改密码                     │
│                                   │
│   管理员已重置您的密码，请设置    │
│   新密码以继续使用。              │
│                                   │
│   新密码                          │
│   ┌─────────────────────────────┐ │
│   │                             │ │
│   └─────────────────────────────┘ │
│                                   │
│   确认新密码                      │
│   ┌─────────────────────────────┐ │
│   │                             │ │
│   └─────────────────────────────┘ │
│                                   │
│   ┌─────────────────────────────┐ │
│   │        确认修改             │ │
│   └─────────────────────────────┘ │
│                                   │
└───────────────────────────────────┘
```

---

## 三、实现方案

### 3.1 任务分解

- [ ] **Task 1**: 数据库模型修改（User表添加 role、password_reset_required、is_deleted 字段，修改查询逻辑）
- [ ] **Task 2**: 程序启动时初始化管理员账号
- [ ] **Task 3**: 注册功能修改（新用户默认 role='USER'）
- [ ] **Task 4**: 创建 admin_required 装饰器
- [ ] **Task 5**: 用户管理页面添加权限控制
- [ ] **Task 6**: 用户管理页面添加删除用户功能
- [ ] **Task 7**: 用户管理页面添加重置密码功能
- [ ] **Task 8**: 创建强制修改密码页面
- [ ] **Task 9**: 登录逻辑修改（检查是否需要强制修改密码）
- [ ] **Task 10**: 添加单元测试
- [ ] **Task 11**: 添加UI测试

### 3.2 代码变更清单

| 文件 | 变更类型 | 变更内容 |
|------|----------|----------|
| `app/models/user.py` | 修改 | 添加 role 和 password_reset_required 字段 |
| `app/forms.py` | 新增 | 添加 ChangePasswordForm 表单 |
| `app/routes.py` | 修改 | 添加权限控制、管理员功能、强制修改密码逻辑 |
| `app/decorators.py` | 新增 | 添加 admin_required 装饰器 |
| `run.py` | 修改 | 程序启动时初始化管理员账号 |
| `app/templates/user_management.html` | 修改 | 添加删除、重置密码按钮 |
| `app/templates/force_change_password.html` | 新增 | 强制修改密码页面 |
| `app/templates/base.html` | 修改 | 根据角色显示不同导航（可选） |
| `app/test/test_user.py` | 修改 | 添加角色相关单元测试 |
| `app/test/test_routes.py` | 修改 | 添加权限相关单元测试 |
| `app/test/uat/playwright_test.py` | 修改 | 添加角色相关UI测试 |

### 3.3 关键代码实现

#### 3.3.1 User 模型修改
```python
class User(UserMixin, db.Model):
    # 现有字段...
    role = db.Column(db.String(20), nullable=False, default='USER')
    password_reset_required = db.Column(db.Boolean, nullable=False, default=False)
    
    def is_admin(self):
        return self.role == 'ADMIN'
```

#### 3.3.2 admin_required 装饰器
```python
from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user, login_required

def admin_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin():
            flash('您没有权限访问此页面', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function
```

#### 3.3.3 强制修改密码检查
```python
@app.route('/login', methods=['GET', 'POST'])
def login():
    # 现有登录逻辑...
    if form.validate_on_submit():
        user = User.query.filter_by(phone=form.phone.data).first()
        if user and user.verify_password(form.password.data):
            login_user(user)
            
            # 检查是否需要强制修改密码
            if user.password_reset_required:
                return redirect(url_for('force_change_password'))
            
            return redirect(url_for('index'))
```

#### 3.3.4 管理员重置密码
```python
@app.route('/reset_password/<int:user_id>', methods=['POST'])
@admin_required
def reset_password(user_id):
    user = User.query.get_or_404(user_id)
    if user.is_admin():
        flash('不能重置管理员密码', 'danger')
        return redirect(url_for('user_management'))
    
    user.password = '111111'
    user.password_reset_required = True
    db.session.commit()
    flash(f'用户 {user.phone} 的密码已重置为 111111', 'success')
    return redirect(url_for('user_management'))
```

#### 3.3.5 删除用户（逻辑删除）
```python
@app.route('/delete_user/<int:user_id>', methods=['POST'])
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.is_admin():
        flash('不能删除管理员', 'danger')
        return redirect(url_for('user_management'))
    
    # 逻辑删除，不是物理删除
    user.is_deleted = True
    db.session.commit()
    flash(f'用户 {user.phone} 已删除', 'success')
    return redirect(url_for('user_management'))
```

**注意**：根据规范，所有删除都是逻辑删除。如需物理删除必须经用户确认。

#### 3.3.6 初始化管理员
```python
def init_admin():
    """程序启动时初始化管理员账号"""
    admin = User.query.filter_by(phone='13564612895').first()
    if not admin:
        admin = User(
            phone='13564612895',
            email='admin@gmail.com',
            password='Zk123456',
            role='ADMIN'
        )
        db.session.add(admin)
        db.session.commit()
        print('管理员账号创建成功')
```

---

## 四、测试方案

### 4.1 单元测试

```python
# 测试用户角色
def test_user_role_default():
    """测试新用户默认角色为 USER"""
    user = User(phone='13800138000', email='test@test.com', password='123456')
    assert user.role == 'USER'
    assert not user.is_admin()

def test_admin_role():
    """测试管理员角色"""
    admin = User(phone='13564612895', email='admin@test.com', password='123456', role='ADMIN')
    assert admin.role == 'ADMIN'
    assert admin.is_admin()

# 测试权限控制
def test_admin_required_redirect(client):
    """测试普通用户访问管理页面被重定向"""
    # 登录普通用户
    # 访问 /user_management
    # 验证重定向到首页
```

### 4.2 UI 测试

```python
def test_admin_can_access_user_management(page):
    """测试管理员可以访问用户管理页面"""
    # 登录管理员
    # 访问 /user_management
    # 验证页面正常显示

def test_user_cannot_access_user_management(page):
    """测试普通用户不能访问用户管理页面"""
    # 登录普通用户
    # 访问 /user_management
    # 验证被重定向到首页

def test_admin_reset_user_password(page):
    """测试管理员重置用户密码"""
    # 登录管理员
    # 访问用户管理页面
    # 点击重置密码按钮
    # 验证密码重置成功提示

def test_admin_delete_user(page):
    """测试管理员逻辑删除用户"""
    # 登录管理员
    # 访问用户管理页面
    # 点击删除按钮
    # 验证用户被逻辑删除（is_deleted=True）
    # 验证用户列表中不再显示该用户

def test_logical_delete_not_physical(page):
    """测试删除是逻辑删除而非物理删除"""
    # 管理员删除一个用户
    # 直接从数据库查询该用户
    # 验证用户记录仍然存在，但 is_deleted=True

def test_force_change_password_on_first_login(page):
    """测试重置密码后首次登录强制修改密码"""
    # 管理员重置某用户密码
    # 用该用户登录
    # 验证被重定向到强制修改密码页面
    # 修改密码
    # 验证成功跳转到首页
```

---

## 五、测试结果

### 5.1 单元测试结果

**测试时间**: 2026-03-27  
**测试状态**: ✅ 全部通过

| 测试文件 | 测试数 | 通过数 |
|----------|--------|--------|
| app/test/test_user.py | 12 | 12 ✅ |
| app/test/test_routes.py | 13 | 13 ✅ |

**新增测试覆盖**:
- 用户角色默认值为 USER
- 管理员角色判断
- 强制修改密码标记
- 逻辑删除功能
- 查询过滤已删除用户
- 管理员权限控制
- 强制修改密码流程

### 5.2 UI 测试结果

**测试时间**: 2026-03-27  
**测试状态**: ✅ 全部通过 (13/13)

| 测试用例 | 状态 |
|----------|------|
| test_home_page | ✅ 通过 |
| test_register_page | ✅ 通过 |
| test_register_functionality | ✅ 通过 |
| test_login_page | ✅ 通过 |
| test_login_functionality | ✅ 通过 |
| test_user_management | ✅ 通过 |
| test_logout | ✅ 通过 |
| test_login_password_toggle | ✅ 通过 |
| test_register_password_toggle | ✅ 通过 |
| test_admin_can_access_user_management | ✅ 通过 |
| test_normal_user_cannot_access_user_management | ✅ 通过 |
| test_admin_reset_user_password | ✅ 通过 |
| test_force_change_password_on_first_login | ✅ 通过 |

---

## 六、确认记录

### 待确认事项
- [x] 管理员账号信息：13564612895 / admin@gmail.com / Zk123456
- [x] 重置密码默认值：111111
- [x] 普通用户访问用户管理页面处理方式：重定向到首页 + 提示
- [x] 管理员不能被删除
- [x] 管理员密码不能被重置

### 实现确认
- [x] 方案已确认，可以开始编码
- [x] 编码已完成
- [x] 测试已通过
- [x] 需求已完成

---

## 六、备注

- 数据库需要迁移（添加 role、password_reset_required、is_deleted 字段）
- 现有用户默认为普通用户（role='USER'），is_deleted 默认为 False
- 强制修改密码页面的密码强度要求与注册时一致
- **重要**：所有删除操作必须是逻辑删除，除非用户明确确认需要物理删除
- 建议创建一个通用的查询方法，自动过滤已删除记录

---

## 七、变更记录

| 日期 | 变更内容 | 变更人 |
|------|----------|--------|
| 2026-03-27 | 首页用户统计改为只统计有效用户（未删除） | 用户反馈 |
| 2026-03-27 | 程序启动只初始化管理员，不再初始化测试用户 | 用户反馈 |

---

**最后更新**: 2026-03-27
