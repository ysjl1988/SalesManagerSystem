# 需求文档：多用户同时登录支持

> **需求编号**: REQ-003  
> **提出日期**: 2026-03-27  
> **优先级**: P1  
> **状态**: 已完成

---

## 一、需求描述

### 1.1 背景
当前系统使用Flask默认的session机制，一个浏览器只能保持一个用户登录态。用户希望支持在同一个浏览器中同时登录多个账号（如管理员和普通用户），方便测试和演示。

### 1.2 功能要求

#### FR-001: 多用户同时登录
- 同一个浏览器中支持同时保持多个用户的登录态
- 例如：管理员（admin）已登录，同时还可以登录普通用户（user）
- 两个用户的session互不影响

#### FR-002: 用户切换功能
- 提供用户切换界面，显示当前已登录的所有用户
- 可以快速切换到不同用户的操作界面
- 显示每个用户的角色信息（管理员/普通用户）

#### FR-003: 独立操作会话
- 每个用户的操作是独立的（如用户A的操作不影响用户B）
- 每个用户的权限验证独立进行

### 1.3 验收标准

- [ ] 同一浏览器可同时登录多个用户
- [ ] 每个用户的登录态独立保持
- [ ] 提供用户切换界面
- [ ] 可以查看当前所有已登录用户
- [ ] 可以登出指定用户而不影响其他用户
- [ ] 每个用户的权限验证正确
- [ ] 添加相关单元测试和UI测试

---

## 二、设计方案

### 2.1 技术方案对比

| 方案 | 实现方式 | 优点 | 缺点 | 复杂度 |
|------|----------|------|------|--------|
| **A. Token-based** | 使用JWT token，每个用户一个token存储在localStorage | 真正的无状态，支持多用户 | 需要大改现有代码，前后端都要改 | 高 |
| **B. Session前缀** | 修改session key，为每个用户分配独立session（如session_user_1, session_user_2） | 改动相对小，兼容现有代码 | 需要自定义session管理 | 中 |
| **C. 浏览器多标签** | 使用不同端口或子域名，每个标签独立session | 实现简单 | 用户体验差，需要开多个标签 | 低 |
| **D. Tab隔离** | 使用BroadcastChannel + token，每个标签页独立 | 用户体验好 | 实现复杂，需要处理同步 | 高 |

### 2.2 推荐方案：方案B - Session前缀模式

**设计思路：**
```
传统模式：
  Session: {user_id: 1, role: 'ADMIN'}

多用户模式：
  sessions: {
    'session_admin_abc123': {user_id: 1, role: 'ADMIN'},
    'session_user_def456': {user_id: 2, role: 'USER'}
  }
  current_session: 'session_admin_abc123'  // 当前激活的session
```

**实现方式：**
1. 使用自定义session管理，支持多个session并存
2. 每个session有唯一标识符（UUID）
3. Cookie中存储session ID列表和当前激活的session ID
4. 提供切换接口，切换当前激活的session

### 2.3 数据模型设计

#### Session存储结构
```python
# 服务器端存储（使用数据库或Redis）
class UserSession(db.Model):
    id = db.Column(db.String(36), primary_key=True)  # UUID
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_active = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
```

#### Cookie结构
```json
{
  "sessions": ["uuid-1", "uuid-2"],
  "current": "uuid-1"
}
```

### 2.4 UI设计

#### 用户切换组件
```
┌─────────────────────────────────┐
│ 👤 当前用户: admin (管理员)  ▼  │
├─────────────────────────────────┤
│ 👤 admin (管理员)          ✓    │
│ 👤 user001 (普通用户)           │
│ ─────────────────────────────── │
│ ➕ 登录新账号                   │
│ ⏏️  退出当前账号                │
│ ⏏️  退出所有账号                │
└─────────────────────────────────┘
```

#### 多用户管理页面
```
┌─────────────────────────────────────┐
│ 多用户会话管理                       │
├─────────────────────────────────────┤
│                                     │
│ 当前激活会话:                        │
│ ┌───────────────────────────────┐   │
│ │ 👤 admin (管理员)      [当前] │   │
│ │    登录时间: 2024-03-27 10:00 │   │
│ │    [切换] [退出]              │   │
│ └───────────────────────────────┘   │
│                                     │
│ 其他会话:                            │
│ ┌───────────────────────────────┐   │
│ │ 👤 user001 (普通用户)         │   │
│ │    登录时间: 2024-03-27 10:30 │   │
│ │    [切换] [退出]              │   │
│ └───────────────────────────────┘   │
│                                     │
│ [+ 登录新账号]                      │
│                                     │
└─────────────────────────────────────┘
```

---

## 三、实现方案

### 3.1 任务分解

- [ ] **Task 1**: 设计多用户session存储结构（数据库表设计）
- [ ] **Task 2**: 实现自定义session管理器（MultiUserSessionManager）
- [ ] **Task 3**: 修改登录逻辑，支持新增session而不覆盖
- [ ] **Task 4**: 实现用户切换功能（切换当前激活session）
- [ ] **Task 5**: 实现多用户管理页面
- [ ] **Task 6**: 修改导航栏，添加用户切换组件
- [ ] **Task 7**: 实现退出指定用户功能
- [ ] **Task 8**: 添加单元测试
- [ ] **Task 9**: 添加UI测试

### 3.2 代码变更清单

| 文件 | 变更类型 | 变更内容 |
|------|----------|----------|
| `app/models/session.py` | 新增 | UserSession模型 |
| `app/session_manager.py` | 新增 | 多用户session管理器 |
| `app/routes.py` | 修改 | 修改登录逻辑支持多session |
| `app/routes.py` | 新增 | 用户切换、管理接口 |
| `app/templates/multi_user.html` | 新增 | 多用户管理页面 |
| `app/templates/base.html` | 修改 | 添加用户切换组件 |

### 3.3 关键代码实现

#### 3.3.1 Session管理器
```python
class MultiUserSessionManager:
    """多用户session管理器"""
    
    def __init__(self, session_cookie):
        self.cookie = session_cookie
        self.sessions = self._load_sessions()
    
    def _load_sessions(self):
        """从cookie加载所有session"""
        data = json.loads(self.cookie.get('multi_sessions', '{}'))
        return data.get('sessions', []), data.get('current')
    
    def add_session(self, user_id):
        """添加新用户session"""
        session_id = str(uuid.uuid4())
        # 存储到数据库
        UserSession.create(session_id, user_id)
        self.sessions.append(session_id)
        self.current = session_id
        self._save()
        return session_id
    
    def switch_session(self, session_id):
        """切换到指定session"""
        if session_id in self.sessions:
            self.current = session_id
            self._save()
            return True
        return False
    
    def get_current_user(self):
        """获取当前用户"""
        if not self.current:
            return None
        session = UserSession.query.get(self.current)
        return session.user if session else None
    
    def remove_session(self, session_id):
        """移除指定session"""
        if session_id in self.sessions:
            self.sessions.remove(session_id)
            UserSession.delete(session_id)
            if self.current == session_id and self.sessions:
                self.current = self.sessions[0]
            self._save()
```

#### 3.3.2 修改登录逻辑
```python
@app.route('/login', methods=['POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.get_by_phone(form.phone.data)
        if user and user.verify_password(form.password.data):
            # 多用户模式：添加新session而不是覆盖
            session_manager = MultiUserSessionManager(session)
            session_manager.add_session(user.id)
            flash(f'{user.phone} 登录成功', 'success')
            return redirect(url_for('index'))
```

#### 3.3.3 用户切换接口
```python
@app.route('/switch_user/<session_id>')
def switch_user(session_id):
    """切换到指定用户session"""
    session_manager = MultiUserSessionManager(session)
    if session_manager.switch_session(session_id):
        flash('用户切换成功', 'success')
    else:
        flash('切换失败', 'danger')
    return redirect(url_for('index'))
```

---

## 四、测试方案

### 4.1 单元测试

```python
def test_multi_session_manager():
    """测试多session管理器"""
    manager = MultiUserSessionManager({})
    
    # 添加第一个用户
    session1 = manager.add_session(user_id=1)
    assert session1 in manager.sessions
    assert manager.current == session1
    
    # 添加第二个用户
    session2 = manager.add_session(user_id=2)
    assert session2 in manager.sessions
    assert len(manager.sessions) == 2
    
    # 切换用户
    manager.switch_session(session1)
    assert manager.current == session1
    
    # 移除用户
    manager.remove_session(session2)
    assert session2 not in manager.sessions
    assert len(manager.sessions) == 1
```

### 4.2 UI测试

```python
def test_multi_user_login(page):
    """测试多用户登录"""
    # 登录第一个用户（管理员）
    page.goto("/login")
    page.fill("id=phone", "13564612895")
    page.fill("id=password", "Zk123456")
    page.click("input[type='submit']")
    page.wait_for_url("/")
    
    # 打开新标签页或保持session
    # 登录第二个用户（普通用户）
    page.goto("/login")
    page.fill("id=phone", "13800000001")
    page.fill("id=password", "Zk123456")
    page.click("input[type='submit']")
    
    # 验证两个用户都显示在用户切换列表中
    page.click("text=用户切换")
    assert "13564612895" in page.content()
    assert "13800000001" in page.content()
```

---

## 五、测试结果

### 5.1 单元测试结果

**测试时间**: 2026-03-27  
**测试状态**: ✅ 通过 (45个测试)

| 测试文件 | 测试数 | 通过数 |
|----------|--------|--------|
| app/test/test_user.py | 16 | 16 ✅ |
| app/test/test_routes.py | 13 | 13 ✅ |
| app/test/test_multi_user_session.py | 16 | 16 ✅ |

覆盖功能：
- UserSession 模型创建和查询
- Session 过期检测
- MultiUserSessionManager 添加/切换/删除 session

### 5.2 UI测试结果

**测试时间**: 2026-03-27  
**测试状态**: ✅ 通过 (18/18)

新增测试：
- test_multi_user_login ✅
- test_multi_user_switch ✅
- test_multi_user_logout_single ✅
- **test_browser_isolation_login** ✅ (浏览器A/B独立登录)
- **test_browser_isolation_after_logout** ✅ (浏览器B退出不影响A)

### 5.3 问题修复验证

**修复时间**: 2026-03-27  
**修复状态**: ✅ 通过

| 测试项 | 状态 |
|--------|------|
| 浏览器A和B独立session | ✅ 通过 |
| 不同浏览器登录不冲突 | ✅ 通过 |
| 不使用Flask-Login session | ✅ 通过 |

### 5.4 功能验证

| 功能 | 状态 |
|------|------|
| 多用户同时登录 | ✅ 支持 |
| 用户切换 | ✅ 可用 |
| 独立session管理 | ✅ 正常 |
| 用户管理页面 | ✅ 可访问 |
| 浏览器隔离 | ✅ 支持 |

---

## 六、确认记录

### 待确认事项
- [x] 确认方案B（Session前缀模式）是否可接受？ → **确认使用方案B**
- [x] 是否需要支持无限多用户，还是限制数量？ → **无限多用户**
- [ ] 用户切换组件放在导航栏的哪个位置？
- [ ] 是否需要显示每个用户的未读消息/通知？

### 技术问题讨论（已确认）
1. **Session存储**：✅ 使用**数据库存储**
2. **Session过期**：✅ **每个session独立过期时间**
3. **用户数量**：✅ **支持无限多用户**

### 实现确认
- [x] 方案已确认，可以开始编码
- [x] 编码已完成
- [x] 测试用例已添加/更新
- [x] 测试中（运行单元测试和UI测试）
- [x] 测试已通过
- [x] 需求已完成

---

## 七、备注

- 这是一个架构级别的改动，需要仔细测试
- 可能影响现有的session相关功能
- 已实现无限多用户同时登录
- 每个session有独立的过期时间（默认1天）

---

## 八、问题修复记录

### 问题 001: 浏览器间session冲突

**发现时间**: 2026-03-27  
**问题描述**: 
- 浏览器A登录admin后，浏览器B登录新用户，浏览器A刷新后显示为新用户
- 预期：两个浏览器应该保持独立的登录状态

**根本原因**:
- Flask-Login的`login_user()`在session中存储`user_id`
- 不同浏览器共享了Flask的session cookie，导致登录状态互相干扰

**修复方案**:
- [x] 完全移除`login_user`调用，不使用Flask-Login的session存储
- [x] 自定义`load_user`，从多session管理器获取用户
- [x] 自定义`login_required_custom`装饰器
- [x] 添加全局上下文处理器，模板使用`session_manager`
- [x] 更新模板，使用`session_manager.get_current_user()`
- [x] 添加测试用例验证浏览器隔离

**修复状态**: ✅ 已完成并通过测试

**新增UI测试** (app/test/uat/test_browser_isolation.py):
- `test_browser_isolation_login` - 验证浏览器A和B独立登录
- `test_browser_isolation_after_logout` - 验证浏览器B退出不影响A

**测试结果**: ✅ 2/2 通过 (使用Playwright的browser.new_context()创建独立浏览器上下文)

---

**最后更新**: 2026-03-27
