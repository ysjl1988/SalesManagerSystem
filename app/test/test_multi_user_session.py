"""
多用户会话管理单元测试
"""
import pytest
import json
from datetime import datetime, timedelta
from app import app, db
from app.models.user import User
from app.models.session import UserSession
from app.session_manager import MultiUserSessionManager, get_session_manager


@pytest.fixture(scope='module')
def app_context():
    """测试配置"""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SECRET_KEY'] = 'test-secret-key'
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.app_context() as context:
        db.create_all()
        yield context
        db.drop_all()


@pytest.fixture
def database_session(app_context):
    """数据库会话"""
    yield db.session


@pytest.fixture(scope='function')
def test_users(database_session):
    """创建测试用户（使用唯一手机号和邮箱避免冲突）"""
    import uuid
    
    # 使用UUID确保唯一性
    unique_id = str(uuid.uuid4())[:8]
    
    admin = User(
        phone=f'139{unique_id}',
        email=f'admin{unique_id}@test.com',
        password='Zk123456',
        role='ADMIN'
    )
    user1 = User(
        phone=f'138{unique_id}1',
        email=f'user1{unique_id}@test.com',
        password='Test123456',
        role='USER'
    )
    user2 = User(
        phone=f'138{unique_id}2',
        email=f'user2{unique_id}@test.com',
        password='Test123456',
        role='USER'
    )
    
    database_session.add_all([admin, user1, user2])
    database_session.commit()
    
    return {'admin': admin, 'user1': user1, 'user2': user2}


class TestUserSession:
    """UserSession 模型测试"""
    
    def test_create_session(self, database_session, test_users):
        """测试创建session"""
        session = UserSession.create(user_id=test_users['user1'].id)
        
        assert session.id is not None
        assert len(session.id) == 36  # UUID格式
        assert session.user_id == test_users['user1'].id
        assert session.is_active is True
        assert session.created_at is not None
    
    def test_session_expiration(self, database_session, test_users):
        """测试session过期"""
        # 创建一个已过期的session
        expired_time = datetime.utcnow() - timedelta(hours=1)
        session = UserSession(
            user_id=test_users['user1'].id,
            expires_at=expired_time
        )
        db.session.add(session)
        db.session.commit()
        
        # 验证session已过期
        assert session.is_expired() is True
        
        # 通过get_valid_session获取应该返回None
        result = UserSession.get_valid_session(session.id)
        assert result is None
    
    def test_session_not_expired(self, database_session, test_users):
        """测试未过期的session"""
        future_time = datetime.utcnow() + timedelta(hours=1)
        session = UserSession(
            user_id=test_users['user1'].id,
            expires_at=future_time
        )
        db.session.add(session)
        db.session.commit()
        
        # 验证session未过期
        assert session.is_expired() is False
        
        # 通过get_valid_session获取应该返回session
        result = UserSession.get_valid_session(session.id)
        assert result is not None
        assert result.id == session.id
    
    def test_session_touch(self, database_session, test_users):
        """测试更新session最后活动时间"""
        session = UserSession.create(user_id=test_users['user1'].id)
        old_time = session.last_active
        
        # 等待一小段时间
        import time
        time.sleep(0.1)
        
        session.touch()
        db.session.commit()
        
        assert session.last_active > old_time
    
    def test_delete_session(self, database_session, test_users):
        """测试删除session（标记为无效）"""
        session = UserSession.create(user_id=test_users['user1'].id)
        session_id = session.id
        
        # 删除session
        result = UserSession.delete_session(session_id)
        assert result is True
        
        # 验证session已标记为无效
        session = UserSession.query.get(session_id)
        assert session.is_active is False


class TestMultiUserSessionManager:
    """MultiUserSessionManager 测试"""
    
    def test_add_single_session(self, database_session, test_users):
        """测试添加单个session"""
        with app.test_request_context():
            manager = MultiUserSessionManager()
            session_id = manager.add_session(test_users['user1'].id)
            
            assert session_id is not None
            assert session_id in manager.sessions
            assert manager.current == session_id
            assert manager.get_session_count() == 1
    
    def test_add_multiple_sessions(self, database_session, test_users):
        """测试添加多个session"""
        with app.test_request_context():
            manager = MultiUserSessionManager()
            
            # 添加第一个用户
            session1 = manager.add_session(test_users['user1'].id)
            assert manager.get_session_count() == 1
            
            # 添加第二个用户
            session2 = manager.add_session(test_users['user2'].id)
            assert manager.get_session_count() == 2
            
            # 验证两个session都存在
            assert session1 in manager.sessions
            assert session2 in manager.sessions
            # 当前应该是第二个用户
            assert manager.current == session2
    
    def test_switch_session(self, database_session, test_users):
        """测试切换session"""
        with app.test_request_context():
            manager = MultiUserSessionManager()
            
            session1 = manager.add_session(test_users['user1'].id)
            session2 = manager.add_session(test_users['user2'].id)
            
            # 当前是session2
            assert manager.current == session2
            
            # 切换到session1
            result = manager.switch_session(session1)
            assert result is True
            assert manager.current == session1
            
            # 获取当前用户验证
            current_user = manager.get_current_user()
            assert current_user.id == test_users['user1'].id
    
    def test_switch_invalid_session(self, database_session, test_users):
        """测试切换到无效的session"""
        with app.test_request_context():
            manager = MultiUserSessionManager()
            manager.add_session(test_users['user1'].id)
            
            # 尝试切换到不存在的session
            result = manager.switch_session('non-existent-id')
            assert result is False
    
    def test_remove_session(self, database_session, test_users):
        """测试移除session"""
        with app.test_request_context():
            manager = MultiUserSessionManager()
            
            session1 = manager.add_session(test_users['user1'].id)
            session2 = manager.add_session(test_users['user2'].id)
            
            assert manager.get_session_count() == 2
            
            # 移除session1
            result = manager.remove_session(session1)
            assert result is True
            assert manager.get_session_count() == 1
            assert session1 not in manager.sessions
            
            # 当前应该自动切换到session2
            assert manager.current == session2
    
    def test_remove_current_session(self, database_session, test_users):
        """测试移除当前session"""
        with app.test_request_context():
            manager = MultiUserSessionManager()
            
            session1 = manager.add_session(test_users['user1'].id)
            session2 = manager.add_session(test_users['user2'].id)
            
            # 当前是session2
            assert manager.current == session2
            
            # 移除当前session
            manager.remove_session(session2)
            
            # 应该自动切换到session1
            assert manager.current == session1
    
    def test_remove_all_sessions(self, database_session, test_users):
        """测试移除所有session"""
        with app.test_request_context():
            manager = MultiUserSessionManager()
            
            manager.add_session(test_users['user1'].id)
            manager.add_session(test_users['user2'].id)
            
            assert manager.get_session_count() == 2
            
            # 移除所有session
            manager.remove_all_sessions()
            
            assert manager.get_session_count() == 0
            assert manager.current is None
            assert len(manager.sessions) == 0
    
    def test_reuse_existing_session(self, database_session, test_users):
        """测试复用已存在的session"""
        with app.test_request_context():
            manager = MultiUserSessionManager()
            
            # 第一次添加用户
            session1 = manager.add_session(test_users['user1'].id)
            
            # 再次添加同一个用户，应该复用session
            session2 = manager.add_session(test_users['user1'].id)
            
            # 应该是同一个session
            assert session1 == session2
            # session数量应该还是1
            assert manager.get_session_count() == 1
    
    def test_get_all_sessions(self, database_session, test_users):
        """测试获取所有有效session"""
        with app.test_request_context():
            manager = MultiUserSessionManager()
            
            manager.add_session(test_users['user1'].id)
            manager.add_session(test_users['user2'].id)
            
            sessions = manager.get_all_sessions()
            assert len(sessions) == 2
            
            # 验证都是UserSession对象
            for s in sessions:
                assert isinstance(s, UserSession)
    
    def test_cleanup_expired_sessions(self, database_session, test_users):
        """测试清理过期session"""
        with app.test_request_context():
            manager = MultiUserSessionManager()
            
            # 添加正常session
            session1 = manager.add_session(test_users['user1'].id)
            
            # 手动添加一个过期session
            expired_session = UserSession(
                user_id=test_users['user2'].id,
                expires_at=datetime.utcnow() - timedelta(hours=1)
            )
            db.session.add(expired_session)
            db.session.commit()
            
            manager.sessions.append(expired_session.id)
            manager._save_to_cookie()
            
            # 清理后应该只剩1个
            assert manager.get_session_count() == 1


def test_get_session_manager():
    """测试获取session管理器"""
    with app.test_request_context():
        manager1 = get_session_manager()
        manager2 = get_session_manager()
        
        # 每次调用应该返回新实例（从cookie加载）
        assert isinstance(manager1, MultiUserSessionManager)
        assert isinstance(manager2, MultiUserSessionManager)
