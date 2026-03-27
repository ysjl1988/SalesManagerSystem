import pytest
from app import app, db
from app.models.user import User


# 测试配置
@pytest.fixture(scope='function')
def app_context():
    # 设置测试配置
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SECRET_KEY'] = 'test-secret-key'
    app.config['WTF_CSRF_ENABLED'] = False  # 禁用CSRF保护以方便测试
    
    with app.app_context() as context:
        # 创建数据库表
        db.create_all()
        yield context
        # 清理数据库
        db.drop_all()
        db.session.remove()


# 测试客户端
@pytest.fixture(scope='function')
def test_client(app_context):
    with app.test_client() as testing_client:
        yield testing_client


# 获取测试数据库会话
@pytest.fixture(scope='function')
def database_session(app_context):
    yield db.session
    db.session.rollback()


# 测试首页
def test_index(test_client):
    response = test_client.get("/")
    assert response.status_code == 200
    assert "销售管理系统" in response.text


# 测试注册页面
def test_register_form(test_client):
    response = test_client.get("/register")
    assert response.status_code == 200
    assert "注册" in response.text
    # 检查表单元素是否存在
    assert "<form method=\"POST\">" in response.text
    assert "id=\"phone\"" in response.text
    assert "name=\"phone\"" in response.text
    assert "id=\"email\"" in response.text
    assert "name=\"email\"" in response.text
    assert "id=\"password\"" in response.text
    assert "name=\"password\"" in response.text


# 测试注册功能
def test_register(test_client):
    response = test_client.post("/register", data={
        "phone": "13800000030",
        "email": "test30@example.com",
        "password": "Test123456"
    })
    assert response.status_code == 302  # Flask使用302重定向
    assert response.headers["Location"] == "/login"


# 测试登录页面
def test_login_form(test_client):
    response = test_client.get("/login")
    assert response.status_code == 200
    assert "登录" in response.text
    # 检查表单元素是否存在
    assert "<form method=\"POST\">" in response.text
    assert "id=\"phone\"" in response.text
    assert "name=\"phone\"" in response.text
    assert "id=\"password\"" in response.text
    assert "name=\"password\"" in response.text


# 测试登录功能
def test_login(test_client, database_session):
    # 先创建一个测试用户
    user = User(
        phone="13800000031",
        email="test31@example.com",
        password="Test123456"
    )
    database_session.add(user)
    database_session.commit()
    
    # 测试登录
    response = test_client.post("/login", data={
        "phone": "13800000031",
        "password": "Test123456"
    })
    assert response.status_code == 302  # Flask使用302重定向
    assert response.headers["Location"] == "/"


# 测试错误的登录
def test_login_wrong_password(test_client, database_session):
    # 先创建一个测试用户
    user = User(
        phone="13800000032",
        email="test32@example.com",
        password="Test123456"
    )
    database_session.add(user)
    database_session.commit()
    
    # 测试使用错误密码登录
    response = test_client.post("/login", data={
        "phone": "13800000032",
        "password": "WrongPassword"
    })
    assert response.status_code == 200  # 登录失败，返回登录页
    assert "手机号或密码错误" in response.text


# 测试管理员访问用户管理页面
def test_user_management_admin(test_client, database_session):
    # 创建一个管理员用户
    admin = User(
        phone="13564612895",
        email="admin@example.com",
        password="Zk123456",
        role='ADMIN'
    )
    database_session.add(admin)
    database_session.commit()
    
    # 登录管理员
    test_client.post("/login", data={
        "phone": "13564612895",
        "password": "Zk123456"
    })
    
    # 访问用户管理页面
    response = test_client.get("/user_management")
    assert response.status_code == 200
    assert "用户管理" in response.text


# 测试普通用户不能访问用户管理页面
def test_user_management_normal_user_forbidden(test_client, database_session):
    # 创建一个普通用户
    user = User(
        phone="13800000033",
        email="test33@example.com",
        password="Test123456",
        role='USER'
    )
    database_session.add(user)
    database_session.commit()
    
    # 登录普通用户
    test_client.post("/login", data={
        "phone": "13800000033",
        "password": "Test123456"
    })
    
    # 访问用户管理页面，应该被重定向到首页
    response = test_client.get("/user_management")
    assert response.status_code == 302
    assert response.headers["Location"] == "/"


# 测试退出登录
def test_logout(test_client, database_session):
    # 先创建一个测试用户
    user = User(
        phone="13800000034",
        email="test34@example.com",
        password="Test123456"
    )
    database_session.add(user)
    database_session.commit()
    
    # 登录用户
    test_client.post("/login", data={
        "phone": "13800000034",
        "password": "Test123456"
    })
    
    # 退出登录
    response = test_client.get("/logout")
    assert response.status_code == 302  # Flask使用302重定向
    # 退出后如果没有其他session，重定向到登录页
    assert response.headers["Location"] == "/login"


# 测试未认证访问需要认证的页面
def test_unauthorized_access(test_client):
    response = test_client.get("/user_management")
    assert response.status_code == 302  # 重定向到登录页
    assert response.headers["Location"] == "/login"


# ==================== 角色与权限测试 ====================

# 测试强制修改密码
def test_force_change_password_redirect(test_client, database_session):
    """测试被重置密码后首次登录被重定向到强制修改密码页面"""
    # 创建一个需要强制修改密码的用户
    user = User(
        phone="13800000040",
        email="test40@example.com",
        password="111111",
        password_reset_required=True
    )
    database_session.add(user)
    database_session.commit()
    
    # 登录用户
    response = test_client.post("/login", data={
        "phone": "13800000040",
        "password": "111111"
    })
    
    # 应该被重定向到强制修改密码页面
    assert response.status_code == 302
    assert response.headers["Location"] == "/force_change_password"


def test_force_change_password_page_access(test_client, database_session):
    """测试强制修改密码页面访问"""
    # 创建一个需要强制修改密码的用户
    user = User(
        phone="13800000041",
        email="test41@example.com",
        password="111111",
        password_reset_required=True
    )
    database_session.add(user)
    database_session.commit()
    
    # 登录用户
    test_client.post("/login", data={
        "phone": "13800000041",
        "password": "111111"
    })
    
    # 访问强制修改密码页面
    response = test_client.get("/force_change_password")
    assert response.status_code == 200
    assert "修改密码" in response.text


def test_force_change_password_success(test_client, database_session):
    """测试成功修改密码后可以正常访问"""
    # 创建一个需要强制修改密码的用户
    user = User(
        phone="13800000042",
        email="test42@example.com",
        password="111111",
        password_reset_required=True
    )
    database_session.add(user)
    database_session.commit()
    
    # 登录用户
    test_client.post("/login", data={
        "phone": "13800000042",
        "password": "111111"
    })
    
    # 提交新密码
    response = test_client.post("/force_change_password", data={
        "new_password": "NewPass123",
        "confirm_password": "NewPass123"
    })
    
    # 应该重定向到首页
    assert response.status_code == 302
    assert response.headers["Location"] == "/"
    
    # 验证密码已更新
    updated_user = database_session.query(User).filter_by(phone="13800000042").first()
    assert updated_user.password_reset_required is False
    assert updated_user.verify_password("NewPass123")