from app import db, login_manager
from flask_login import UserMixin
from passlib.hash import pbkdf2_sha256
from datetime import datetime


@login_manager.user_loader
def load_user(user_id):
    """
    加载用户 - 支持多用户session管理
    优先从多session管理器获取当前用户
    """
    # 导入session管理器（避免循环导入）
    from flask import session as flask_session
    
    # 检查是否有多session
    multi_sessions = flask_session.get('multi_sessions')
    if multi_sessions:
        try:
            import json
            data = json.loads(multi_sessions) if isinstance(multi_sessions, str) else multi_sessions
            current_session_id = data.get('current')
            if current_session_id:
                # 从UserSession获取用户
                from app.models.session import UserSession
                user_session = UserSession.query.filter_by(
                    id=current_session_id, 
                    is_active=True
                ).first()
                if user_session and user_session.user:
                    return user_session.user
        except:
            pass
    
    # 回退到默认方式
    return User.query_active().filter_by(id=int(user_id)).first()


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    registered_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_login_at = db.Column(db.DateTime, nullable=True)
    
    # 角色与权限字段
    role = db.Column(db.String(20), nullable=False, default='USER')  # ADMIN/USER
    password_reset_required = db.Column(db.Boolean, nullable=False, default=False)  # 是否需要强制修改密码
    is_deleted = db.Column(db.Boolean, nullable=False, default=False)  # 逻辑删除标记
    
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    
    @password.setter
    def password(self, password):
        self.password_hash = pbkdf2_sha256.hash(password)
    
    def verify_password(self, password):
        return pbkdf2_sha256.verify(password, self.password_hash)
    
    def is_admin(self):
        """判断用户是否为管理员"""
        return self.role == 'ADMIN'
    
    @classmethod
    def query_active(cls):
        """查询未删除的用户（逻辑删除过滤）"""
        return cls.query.filter_by(is_deleted=False)
    
    @classmethod
    def get_by_phone(cls, phone):
        """根据手机号获取未删除的用户"""
        return cls.query_active().filter_by(phone=phone).first()
