import pytest
from app import app, db
from app.models.user import User


# 测试配置
@pytest.fixture(scope='module')
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


# 测试客户端
@pytest.fixture(scope='module')
def test_client(app_context):
    with app.test_client() as testing_client:
        yield testing_client


# 获取测试数据库会话
@pytest.fixture
def database_session(app_context):
    yield db.session


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


# 测试已认证用户访问用户管理页面
def test_user_management_authenticated(test_client, database_session):
    # 先创建一个测试用户
    user = User(
        phone="13800000033",
        email="test33@example.com",
        password="Test123456"
    )
    database_session.add(user)
    database_session.commit()
    
    # 登录用户
    test_client.post("/login", data={
        "phone": "13800000033",
        "password": "Test123456"
    })
    
    # 访问用户管理页面
    response = test_client.get("/user_management")
    assert response.status_code == 200
    assert "用户管理" in response.text


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
    assert response.headers["Location"] == "/"  # logout路由实际重定向到首页


# 测试未认证访问需要认证的页面
def test_unauthorized_access(test_client):
    response = test_client.get("/user_management")
    assert response.status_code == 302  # Flask-Login会重定向到登录页
    assert response.headers["Location"] == "/login?next=%2Fuser_management"