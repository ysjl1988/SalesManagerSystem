# 需求文档：密码显示/隐藏切换功能

> **需求编号**: REQ-001  
> **提出日期**: 2026-03-27  
> **状态**: 已完成

---

## 一、需求描述

### 1.1 背景
用户在登录和注册页面输入密码时，无法确认自己输入的内容是否正确，特别是在移动设备或复杂密码场景下容易出错。增加密码显示/隐藏功能可以提升用户体验。

### 1.2 功能要求
1. 在登录页面的密码输入框增加显示/隐藏切换按钮
2. 在注册页面的密码输入框增加显示/隐藏切换按钮
3. 点击按钮可在明文显示和密文隐藏之间切换

### 1.3 验收标准
- [x] 登录页面密码框有显示/隐藏切换按钮
- [x] 注册页面密码框有显示/隐藏切换按钮
- [x] 默认状态下密码为隐藏状态
- [x] 点击眼睛图标可切换显示/隐藏状态
- [x] 切换时图标同步变化（睁开/闭合）
- [x] 样式统一，可通过 CSS 类复用
- [x] 添加 UI 自动化测试用例

---

## 二、设计方案

### 2.1 UI设计

**布局效果：**
```
┌──────────────────────────────────┐
│ 密码                             │
│ ┌──────────────────────────┬─────┐
│ │ 请输入密码               │ 👁️  │
│ └──────────────────────────┴─────┘
└──────────────────────────────────┘
```

**设计要点：**
1. **图标位置**：密码输入框外部右侧（紧邻，间距8px）
2. **默认状态**：密码隐藏（符合安全惯例）
3. **图标颜色**：固定颜色 `#57606a`（灰色），悬停时 `#24292f`（深灰）

### 2.2 技术方案

**实现方式**：纯前端实现（HTML + CSS + JS），无需修改后端

**复用设计**：
- 创建通用的 CSS 类 `.password-input-wrapper` 和 `.password-toggle-btn`
- 创建通用的 JavaScript 函数 `togglePasswordVisibility()`
- 通过 `data-target` 属性关联按钮和输入框，支持一个页面多个密码框

**图标方案**：内嵌 SVG，无需外部依赖

---

## 三、实现方案

### 3.1 CSS 样式（添加到 base.html）

```css
/* 密码输入容器 - 用于密码显示/隐藏切换功能 */
.password-input-wrapper {
    display: flex;
    align-items: center;
    gap: 8px;
}

.password-input-wrapper input[type="password"],
.password-input-wrapper input[type="text"] {
    flex: 1;
    width: auto;
}

.password-toggle-btn {
    background: transparent;
    border: none;
    padding: 8px;
    cursor: pointer;
    color: #57606a;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 4px;
    transition: color 0.2s ease, background-color 0.2s ease;
}

.password-toggle-btn:hover {
    color: #24292f;
    background-color: #f6f8fa;
}

.password-toggle-btn svg {
    width: 20px;
    height: 20px;
}
```

### 3.2 JavaScript 功能（添加到 base.html）

```javascript
// 密码显示/隐藏切换功能
function togglePasswordVisibility(button) {
    const targetId = button.getAttribute('data-target');
    const input = document.getElementById(targetId);
    const icon = button.querySelector('.password-toggle-icon');
    
    if (input.type === 'password') {
        input.type = 'text';
        // 切换到"眼睛睁开"图标
        icon.innerHTML = '<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle>';
        button.setAttribute('aria-label', '隐藏密码');
    } else {
        input.type = 'password';
        // 切换到"眼睛闭合"图标
        icon.innerHTML = '<path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path><line x1="1" y1="1" x2="23" y2="23"></line>';
        button.setAttribute('aria-label', '显示密码');
    }
}

// 页面加载时自动绑定事件
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.password-toggle-btn').forEach(function(btn) {
        btn.addEventListener('click', function() {
            togglePasswordVisibility(this);
        });
    });
});
```

### 3.3 HTML 结构修改

**login.html 和 register.html 的密码框改为：**

```html
<div class="form-group">
    {{ form.password.label }}
    <div class="password-input-wrapper">
        {{ form.password(placeholder="请输入密码", id="password") }}
        <button type="button" class="password-toggle-btn" data-target="password" aria-label="显示密码">
            <svg class="password-toggle-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <!-- 默认眼睛闭合图标 -->
                <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path>
                <line x1="1" y1="1" x2="23" y2="23"></line>
            </svg>
        </button>
    </div>
    {% for error in form.password.errors %}
        <div style="color: #cf222e; font-size: 12px; margin-top: 4px;">{{ error }}</div>
    {% endfor %}
</div>
```

### 3.4 UI 测试方案

添加到 `app/test/uat/playwright_test.py`：

```python
def test_login_password_toggle(page):
    """测试登录页面密码显示/隐藏切换功能"""
    page.goto("http://127.0.0.1:5000/login")
    
    password_input = page.locator("#password")
    password_input.fill("TestPassword123")
    
    # 验证默认隐藏
    expect(password_input).to_have_attribute("type", "password")
    
    # 点击显示
    toggle_btn = page.locator("button[data-target='password']")
    toggle_btn.click()
    expect(password_input).to_have_attribute("type", "text")
    
    # 再次点击隐藏
    toggle_btn.click()
    expect(password_input).to_have_attribute("type", "password")


def test_register_password_toggle(page):
    """测试注册页面密码显示/隐藏切换功能"""
    page.goto("http://127.0.0.1:5000/register")
    
    password_input = page.locator("#password")
    password_input.fill("TestPassword123")
    
    expect(password_input).to_have_attribute("type", "password")
    
    toggle_btn = page.locator("button[data-target='password']")
    toggle_btn.click()
    expect(password_input).to_have_attribute("type", "text")
    
    toggle_btn.click()
    expect(password_input).to_have_attribute("type", "password")
```

---

## 四、文件变更清单

| 文件 | 变更类型 | 变更内容 |
|------|----------|----------|
| `app/templates/base.html` | 修改 | 添加 CSS 样式和 JavaScript 函数 |
| `app/templates/login.html` | 修改 | 修改密码输入框结构 |
| `app/templates/register.html` | 修改 | 修改密码输入框结构 |
| `app/test/uat/playwright_test.py` | 修改 | 添加 UI 测试用例 |
| `specify/01-password-toggle-feature.md` | 新增 | 本文档 |

---

## 五、确认记录

### 待确认事项
- [x] 眼睛图标位置：密码框外部右侧
- [x] 默认状态：密码隐藏
- [x] 图标颜色：固定颜色 #57606a
- [x] 统一样式：通过 CSS 类实现复用

### 实现确认
- [x] 方案已确认，可以开始编码
- [x] 编码已完成
- [x] 测试已通过
- [x] 需求已完成

---

## 六、备注

- 所有样式通过 CSS 类管理，不内联样式
- JavaScript 功能封装为独立函数，可复用
- 图标使用内嵌 SVG，无需外部依赖
- 按钮类型为 `type="button"`，避免触发表单提交
- 添加 `aria-label` 属性，提升无障碍访问体验

---

**最后更新**: 2026-03-27
