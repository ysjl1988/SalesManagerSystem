# 销售管理系统功能调用链路

## 概述

本文档使用Mermaid序列图详细描述销售管理系统主要功能的调用链路，包括用户注册、登录、用户管理和退出登录等核心功能的执行流程。

## 1. 用户注册功能调用链路

```mermaid
sequenceDiagram
    participant Browser as 浏览器
    participant Routes as 路由层 (routes.py)
    participant Form as 表单层 (forms.py)
    participant Model as 模型层 (user.py)
    participant DB as 数据库 (SQLite)
    participant Template as 模板层 (register.html)

    Browser->>Routes: GET /register
    Routes->>Form: 创建RegistrationForm实例
    Form-->>Routes: 返回表单对象
    Routes->>Template: 渲染register.html模板
    Template-->>Browser: 返回注册页面

    Browser->>Routes: POST /register (表单数据)
    Routes->>Form: 验证表单数据
    Form-->>Routes: 表单验证结果
    
    alt 表单验证失败
        Routes->>Template: 重新渲染register.html模板（带错误信息）
        Template-->>Browser: 返回包含错误信息的注册页面
    else 表单验证成功
        Routes->>Model: 检查手机号是否已存在
        Model->>DB: 查询用户表
        DB-->>Model: 返回查询结果
        
        alt 手机号已存在
            Routes->>Template: 渲染register.html模板（带错误信息）
            Template-->>Browser: 返回包含错误信息的注册页面
        else 手机号未存在
            Routes->>Model: 检查邮箱是否已存在
            Model->>DB: 查询用户表
            DB-->>Model: 返回查询结果
            
            alt 邮箱已存在
                Routes->>Template: 渲染register.html模板（带错误信息）
                Template-->>Browser: 返回包含错误信息的注册页面
            else 邮箱未存在
                Routes->>Model: 创建新用户对象
                Model->>Model: 加密密码
                Routes->>DB: 添加用户到数据库
                DB-->>Routes: 保存成功
                Routes->>Routes: 设置flash消息
                Routes->>Browser: 重定向到/login
            end
        end
    end
```

## 2. 用户登录功能调用链路

```mermaid
sequenceDiagram
    participant Browser as 浏览器
    participant Routes as 路由层 (routes.py)
    participant Form as 表单层 (forms.py)
    participant Model as 模型层 (user.py)
    participant DB as 数据库 (SQLite)
    participant LoginManager as 登录管理器 (Flask-Login)
    participant Session as 用户会话
    participant Template as 模板层 (login.html)

    Browser->>Routes: GET /login
    Routes->>Form: 创建LoginForm实例
    Form-->>Routes: 返回表单对象
    Routes->>Template: 渲染login.html模板
    Template-->>Browser: 返回登录页面

    Browser->>Routes: POST /login (表单数据)
    Routes->>Form: 验证表单数据
    Form-->>Routes: 表单验证结果
    
    alt 表单验证失败
        Routes->>Template: 重新渲染login.html模板（带错误信息）
        Template-->>Browser: 返回包含错误信息的登录页面
    else 表单验证成功
        Routes->>Model: 根据手机号查询用户
        Model->>DB: 查询用户表
        DB-->>Model: 返回用户对象或None
        
        alt 用户不存在
            Routes->>Template: 渲染login.html模板（带错误信息）
            Template-->>Browser: 返回包含错误信息的登录页面
        else 用户存在
            Routes->>Model: 验证密码
            Model-->>Routes: 密码验证结果
            
            alt 密码错误
                Routes->>Template: 渲染login.html模板（带错误信息）
                Template-->>Browser: 返回包含错误信息的登录页面
            else 密码正确
                Routes->>LoginManager: 登录用户
                LoginManager->>Session: 创建用户会话
                Session-->>LoginManager: 会话创建成功
                Routes->>Model: 更新最后登录时间
                Model->>DB: 保存更新
                DB-->>Model: 保存成功
                Routes->>Routes: 设置flash消息
                Routes->>Browser: 重定向到/
            end
        end
    end
```

## 3. 首页访问功能调用链路

```mermaid
sequenceDiagram
    participant Browser as 浏览器
    participant Routes as 路由层 (routes.py)
    participant LoginManager as 登录管理器 (Flask-Login)
    participant Session as 用户会话
    participant Model as 模型层 (user.py)
    participant DB as 数据库 (SQLite)
    participant Template as 模板层 (index.html)

    Browser->>Routes: GET /
    Routes->>LoginManager: 获取当前用户信息
    LoginManager->>Session: 查询用户会话
    
    alt 会话不存在（未登录）
        LoginManager-->>Routes: 返回匿名用户
        Routes->>Template: 渲染index.html模板（user_count=0）
        Template-->>Browser: 返回首页（未登录状态）
    else 会话存在（已登录）
        LoginManager-->>Routes: 返回当前用户对象
        Routes->>Model: 查询用户总数
        Model->>DB: 查询用户表
        DB-->>Model: 返回用户总数
        Routes->>Template: 渲染index.html模板（user_count=N）
        Template-->>Browser: 返回首页（已登录状态）
    end
```

## 4. 用户管理页面访问功能调用链路

```mermaid
sequenceDiagram
    participant Browser as 浏览器
    participant Routes as 路由层 (routes.py)
    participant LoginManager as 登录管理器 (Flask-Login)
    participant Session as 用户会话
    participant Model as 模型层 (user.py)
    participant DB as 数据库 (SQLite)
    participant Template as 模板层 (user_management.html)

    Browser->>Routes: GET /user_management
    Routes->>LoginManager: 检查用户是否已登录
    LoginManager->>Session: 查询用户会话
    
    alt 未登录
        LoginManager-->>Routes: 登录检查失败
        Routes->>Browser: 重定向到/login（带next参数）
    else 已登录
        Routes->>Model: 查询所有用户
        Model->>DB: 查询用户表
        DB-->>Model: 返回用户列表
        Routes->>Template: 渲染user_management.html模板（用户列表）
        Template-->>Browser: 返回用户管理页面
    end
```

## 5. 退出登录功能调用链路

```mermaid
sequenceDiagram
    participant Browser as 浏览器
    participant Routes as 路由层 (routes.py)
    participant LoginManager as 登录管理器 (Flask-Login)
    participant Session as 用户会话

    Browser->>Routes: GET /logout
    Routes->>LoginManager: 登出用户
    LoginManager->>Session: 清除用户会话
    Session-->>LoginManager: 会话清除成功
    Routes->>Browser: 重定向到/
```

## 6. 核心组件交互关系

```mermaid
sequenceDiagram
    participant User as 用户
    participant Browser as 浏览器
    participant FlaskApp as Flask应用
    participant Routes as 路由处理
    participant Forms as 表单验证
    participant Models as 数据模型
    participant DB as 数据库
    participant Templates as 模板渲染

    User->>Browser: 发起请求
    Browser->>FlaskApp: HTTP请求
    FlaskApp->>Routes: 路由匹配
    
    alt 需要表单验证
        Routes->>Forms: 验证请求数据
        Forms-->>Routes: 验证结果
    end
    
    alt 需要数据库操作
        Routes->>Models: 业务逻辑处理
        Models->>DB: 数据库操作
        DB-->>Models: 返回数据
        Models-->>Routes: 返回处理结果
    end
    
    Routes->>Templates: 渲染模板
    Templates-->>FlaskApp: 返回HTML
    FlaskApp-->>Browser: HTTP响应
    Browser-->>User: 展示页面
```

## 7. 数据模型关系

```mermaid
erDiagram
    USER ||--o{ SALES : creates
    USER { 
        int id PK
        string phone UK
        string email UK
        string password_hash
        datetime registered_at
        datetime last_login_at
    }
    SALES {
        int id PK
        int user_id FK
        string product_name
        decimal amount
        datetime sale_date
    }
```

## 8. 系统架构分层

```mermaid
sequenceDiagram
    participant Client as 客户端层
    participant Presentation as 表示层
    participant Business as 业务逻辑层
    participant Data as 数据访问层
    participant Database as 数据库层

    Client->>Presentation: HTTP请求
    Presentation->>Business: 调用业务逻辑
    Business->>Data: 数据操作请求
    Data->>Database: SQL查询/更新
    Database-->>Data: 返回数据
    Data-->>Business: 返回处理结果
    Business-->>Presentation: 业务处理结果
    Presentation-->>Client: HTTP响应
```

## 总结

本项目采用典型的MVC（Model-View-Controller）架构模式：

- **Model（模型层）**: 负责数据的存储和业务逻辑处理，对应`app/models/`目录
- **View（视图层）**: 负责数据的展示，对应`app/templates/`目录
- **Controller（控制层）**: 负责请求的处理和业务逻辑的调度，对应`app/routes.py`文件

通过清晰的分层架构和明确的调用链路，系统实现了高内聚、低耦合的设计目标，便于维护和扩展。

---

**最后更新**: 2026-03-23
