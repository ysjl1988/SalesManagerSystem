import json
from datetime import datetime, timedelta
from flask import session, request
from app.models.session import UserSession
from app.models.user import User


class MultiUserSessionManager:
    """
    多用户会话管理器
    支持同一浏览器中多个用户同时保持登录态
    """
    
    # Cookie名称
    SESSION_COOKIE = 'multi_sessions'
    # Session有效期（天）
    SESSION_LIFETIME = 1
    
    def __init__(self):
        self._load_from_cookie()
    
    def _load_from_cookie(self):
        """从cookie加载session信息"""
        cookie_data = session.get(self.SESSION_COOKIE, '{}')
        try:
            data = json.loads(cookie_data) if isinstance(cookie_data, str) else cookie_data
        except:
            data = {}
        
        self.sessions = data.get('sessions', [])  # 所有session ID列表
        self.current = data.get('current')  # 当前激活的session ID
    
    def _save_to_cookie(self):
        """保存session信息到cookie"""
        data = {
            'sessions': self.sessions,
            'current': self.current
        }
        session[self.SESSION_COOKIE] = json.dumps(data)
        session.permanent = True
    
    def add_session(self, user_id):
        """
        添加新用户session
        如果用户已存在session，则复用
        """
        # 检查该用户是否已有session
        for sid in self.sessions:
            user_session = UserSession.get_valid_session(sid)
            if user_session and user_session.user_id == user_id:
                # 复用已有session，只更新current
                self.current = sid
                user_session.touch()
                self._save_to_cookie()
                return sid
        
        # 创建新session
        expires_at = datetime.utcnow() + timedelta(days=self.SESSION_LIFETIME)
        user_session = UserSession.create(user_id=user_id, expires_at=expires_at)
        
        self.sessions.append(user_session.id)
        self.current = user_session.id
        self._save_to_cookie()
        
        return user_session.id
    
    def switch_session(self, session_id):
        """切换到指定session"""
        if session_id not in self.sessions:
            return False
        
        # 验证session是否有效
        user_session = UserSession.get_valid_session(session_id)
        if not user_session:
            # 移除无效的session
            self.remove_session(session_id)
            return False
        
        self.current = session_id
        user_session.touch()
        self._save_to_cookie()
        return True
    
    def get_current_session(self):
        """获取当前激活的session"""
        if not self.current:
            return None
        
        user_session = UserSession.get_valid_session(self.current)
        if not user_session:
            # 当前session无效，尝试切换到其他session
            self._cleanup_invalid_sessions()
            if self.sessions:
                self.current = self.sessions[0]
                self._save_to_cookie()
                return UserSession.get_valid_session(self.current)
            return None
        
        user_session.touch()
        return user_session
    
    def get_current_user(self):
        """获取当前用户"""
        user_session = self.get_current_session()
        if user_session:
            return user_session.user
        return None
    
    def get_all_sessions(self):
        """获取所有有效的session"""
        self._cleanup_invalid_sessions()
        return UserSession.get_user_sessions(self.sessions)
    
    def remove_session(self, session_id):
        """移除指定session"""
        if session_id in self.sessions:
            self.sessions.remove(session_id)
            UserSession.delete_session(session_id)
            
            # 如果移除的是当前session，切换到其他session
            if self.current == session_id:
                if self.sessions:
                    self.current = self.sessions[0]
                else:
                    self.current = None
            
            self._save_to_cookie()
            return True
        return False
    
    def remove_all_sessions(self):
        """移除所有session（退出所有用户）"""
        for sid in self.sessions:
            UserSession.delete_session(sid)
        
        self.sessions = []
        self.current = None
        self._save_to_cookie()
    
    def _cleanup_invalid_sessions(self):
        """清理无效的session"""
        valid_sessions = []
        for sid in self.sessions:
            if UserSession.get_valid_session(sid):
                valid_sessions.append(sid)
        
        self.sessions = valid_sessions
        
        # 如果当前session无效，切换到第一个有效session
        if self.current and self.current not in valid_sessions:
            self.current = valid_sessions[0] if valid_sessions else None
        
        self._save_to_cookie()
    
    def get_session_count(self):
        """获取session数量"""
        self._cleanup_invalid_sessions()
        return len(self.sessions)


def get_session_manager():
    """获取session管理器实例"""
    return MultiUserSessionManager()
