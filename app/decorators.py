from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user
from app.session_manager import get_session_manager


def login_required_custom(f):
    """
    自定义登录验证装饰器（使用多session管理）
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        session_manager = get_session_manager()
        user = session_manager.get_current_user()
        
        if not user:
            flash('请先登录', 'warning')
            return redirect(url_for('login'))
        
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """
    要求管理员权限的装饰器（使用多session管理）
    
    使用方式：
        @app.route('/admin_only')
        @admin_required
        def admin_only():
            return '管理员页面'
    """
    @wraps(f)
    @login_required_custom
    def decorated_function(*args, **kwargs):
        session_manager = get_session_manager()
        user = session_manager.get_current_user()
        
        if not user or not user.is_admin():
            flash('您没有权限访问此页面', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function
