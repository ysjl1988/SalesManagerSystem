import pytest
from datetime import datetime
from app import app, db
from app.models.user import User
import os


# 测试配置
@pytest.fixture(scope='module')
def app_context():
    # 设置测试配置
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SECRET_KEY'] = 'test-secret-key'
    
    with app.app_context() as context:
        # 创建数据库表
        db.create_all()
        yield context
        # 清理数据库
        db.drop_all()


# 获取测试数据库会话
@pytest.fixture
def database_session(app_context):
    yield db.session


# 测试用户创建
def test_create_user(database_session):
    user = User(
        phone="13800000001",
        email="test@example.com",
        password="Test123456"
    )
    database_session.add(user)
    database_session.commit()
    
    assert user.id is not None
    assert user.phone == "13800000001"
    assert user.email == "test@example.com"
    assert user.registered_at is not None
    assert user.password_hash is not None
    assert user.password_hash != "Test123456"


# 测试密码验证
def test_verify_password(database_session):
    user = User(
        phone="13800000002",
        email="test2@example.com",
        password="Test123456"
    )
    database_session.add(user)
    database_session.commit()
    
    # 正确密码
    assert user.verify_password("Test123456") is True
    
    # 错误密码
    assert user.verify_password("WrongPassword") is False


# 测试获取用户
def test_get_user_by_phone(database_session):
    user = User(
        phone="13800000003",
        email="test3@example.com",
        password="Test123456"
    )
    database_session.add(user)
    database_session.commit()
    
    # 使用SQLAlchemy查询获取用户
    retrieved_user = User.query.filter_by(phone="13800000003").first()
    assert retrieved_user is not None
    assert retrieved_user.phone == "13800000003"
    
    # 测试不存在的用户
    retrieved_user = User.query.filter_by(phone="13899999999").first()
    assert retrieved_user is None


def test_get_user_by_email(database_session):
    user = User(
        phone="13800000004",
        email="test4@example.com",
        password="Test123456"
    )
    database_session.add(user)
    database_session.commit()
    
    # 使用SQLAlchemy查询获取用户
    retrieved_user = User.query.filter_by(email="test4@example.com").first()
    assert retrieved_user is not None
    assert retrieved_user.email == "test4@example.com"
    
    # 测试不存在的用户
    retrieved_user = User.query.filter_by(email="notexists@example.com").first()
    assert retrieved_user is None


def test_get_user_by_id(database_session):
    user = User(
        phone="13800000005",
        email="test5@example.com",
        password="Test123456"
    )
    database_session.add(user)
    database_session.commit()
    
    # 使用SQLAlchemy查询获取用户
    retrieved_user = User.query.get(user.id)
    assert retrieved_user is not None
    assert retrieved_user.id == user.id
    
    # 测试不存在的用户
    retrieved_user = User.query.get(9999)
    assert retrieved_user is None


# 测试获取用户列表
def test_get_users(database_session):
    # 创建多个测试用户
    for i in range(10, 20):
        user = User(
            phone=f"138000000{i}",
            email=f"test{i}@example.com",
            password="Test123456"
        )
        database_session.add(user)
    database_session.commit()
    
    # 获取所有用户
    users = User.query.all()
    assert len(users) >= 10
    
    # 测试按手机号搜索
    users_by_phone = User.query.filter(User.phone.like("%13800000015%")).all()
    assert len(users_by_phone) >= 1
    assert users_by_phone[0].phone == "13800000015"
    
    # 测试按邮箱搜索
    users_by_email = User.query.filter(User.email.like("%test16@example.com%")).all()
    assert len(users_by_email) >= 1
    assert users_by_email[0].email == "test16@example.com"


# 测试用户模型属性
def test_user_properties(database_session):
    user = User(
        phone="13800000021",
        email="test21@example.com",
        password="Test123456"
    )
    database_session.add(user)
    database_session.commit()
    
    # 测试password属性不可读
    with pytest.raises(AttributeError):
        _ = user.password
    
    # 测试last_login_at可以更新
    assert user.last_login_at is None
    user.last_login_at = datetime.utcnow()
    database_session.commit()
    
    # 使用SQLAlchemy查询获取更新后的用户
    updated_user = User.query.get(user.id)
    assert updated_user.last_login_at is not None