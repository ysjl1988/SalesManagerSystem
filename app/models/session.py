from app import db
from datetime import datetime
import uuid


class UserSession(db.Model):
    """多用户会话模型 - 支持同一浏览器多个用户同时登录"""
    __tablename__ = 'user_session'
    
    id = db.Column(db.String(36), primary_key=True)  # UUID
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_active = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=True)  # 独立过期时间
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    
    # 关联用户
    user = db.relationship('User', backref='sessions')
    
    def __init__(self, user_id, expires_at=None):
        self.id = str(uuid.uuid4())
        self.user_id = user_id
        self.expires_at = expires_at
    
    def touch(self):
        """更新最后活动时间"""
        self.last_active = datetime.utcnow()
    
    def is_expired(self):
        """检查session是否过期"""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at
    
    @classmethod
    def create(cls, user_id, expires_at=None):
        """创建新session"""
        session = cls(user_id=user_id, expires_at=expires_at)
        db.session.add(session)
        db.session.commit()
        return session
    
    @classmethod
    def get_valid_session(cls, session_id):
        """获取有效的session（未过期、未删除）"""
        session = cls.query.filter_by(id=session_id, is_active=True).first()
        if session and session.is_expired():
            # 标记过期session为无效
            session.is_active = False
            db.session.commit()
            return None
        return session
    
    @classmethod
    def delete_session(cls, session_id):
        """删除指定session"""
        session = cls.query.get(session_id)
        if session:
            session.is_active = False
            db.session.commit()
            return True
        return False
    
    @classmethod
    def get_user_sessions(cls, session_ids):
        """根据ID列表获取所有有效的session"""
        if not session_ids:
            return []
        
        sessions = []
        for sid in session_ids:
            session = cls.get_valid_session(sid)
            if session:
                sessions.append(session)
        
        return sessions
