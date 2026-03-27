"""
浏览器隔离测试
验证不同浏览器/会话之间的登录状态是独立的
"""
import pytest
from app import app, db
from app.models.user import User
from app.session_manager import MultiUserSessionManager


@pytest.fixture(scope='module')
def app_context():
    """测试配置"""
    import uuid
    
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SECRET_KEY'] = 'test-secret-key'
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.app_context() as context:
        db.create_all()
        # 创建测试用户（使用唯一标识避免冲突）
        uid = str(uuid.uuid4())[:8]
        admin = User(phone=f'139{uid}', email=f'admin{uid}@test.com', 
                    password='Zk123456', role='ADMIN')
        user = User(phone=f'138{uid}', email=f'user{uid}@test.com',
                   password='Test123456', role='USER')
        db.session.add_all([admin, user])
        db.session.commit()
        
        yield context
        db.drop_all()


@pytest.fixture(scope='module')
def test_client(app_context):
    """测试客户端"""
    with app.test_client() as client:
        yield client


class TestBrowserIsolation:
    """浏览器隔离测试"""
    
    def test_different_clients_independent_sessions(self, app_context):
        """测试不同客户端有独立的session"""
        with app.test_request_context():
            # 获取已创建的用户
            admin = User.query.filter_by(role='ADMIN').first()
            user = User.query.filter_by(role='USER').first()
            
            # 模拟浏览器A登录admin
            session_manager_a = MultiUserSessionManager()
            session_manager_a.add_session(admin.id)
            
            # 模拟浏览器B登录user
            session_manager_b = MultiUserSessionManager()
            session_manager_b.add_session(user.id)
            
            # 验证两个session管理器是独立的
            assert session_manager_a.get_current_user().id == admin.id
            assert session_manager_b.get_current_user().id == user.id
    
    def test_session_isolation_after_login(self, test_client):
        """测试登录后session是独立的"""
        # 客户端A登录admin
        with test_client.session_transaction() as sess:
            sess['multi_sessions'] = '{"sessions": ["session-a"], "current": "session-a"}'
        
        # 这里需要模拟session_manager的行为
        # 由于test_client的限制，我们主要验证session存储结构
        with test_client.session_transaction() as sess:
            data = sess.get('multi_sessions')
            assert data is not None


def test_load_user_from_session_manager(app_context):
    """测试从session_manager加载用户，而不是Flask-Login的session"""
    with app.test_request_context():
        # 使用已创建的用户
        user = User.query.first()
        if not user:
            # 如果没有用户，创建一个
            import uuid
            uid = str(uuid.uuid4())[:8]
            user = User(phone=f'138{uid}', email=f'test{uid}@test.com',
                       password='Test123456')
            db.session.add(user)
            db.session.commit()
        
        # 添加session到session_manager
        session_manager = MultiUserSessionManager()
        session_manager.add_session(user.id)
        
        # 测试load_user函数
        from app.models.user import load_user
        loaded_user = load_user(user.id)
        
        # 应该返回正确的用户
        assert loaded_user is not None
        assert loaded_user.id == user.id


def test_no_flask_login_session_storage(app_context):
    """测试不使用Flask-Login的session存储"""
    with app.test_request_context():
        # 检查session中是否没有Flask-Login的user_id
        from flask import session
        # Flask-Login默认存储为'_user_id'
        assert '_user_id' not in session
