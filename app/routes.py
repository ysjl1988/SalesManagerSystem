from flask import render_template, redirect, url_for, request, flash, session
from flask_login import current_user
from datetime import datetime
from app import app, db
from app.models.user import User
from app.forms import RegistrationForm, LoginForm, ChangePasswordForm
from app.decorators import admin_required, login_required_custom
from app.session_manager import get_session_manager

@app.route('/')
def index():
    # 获取session管理器
    session_manager = get_session_manager()
    
    # 获取当前用户（支持多用户模式）
    current_user_from_session = session_manager.get_current_user()
    
    # 统计当前浏览器登录的用户数
    session_count = session_manager.get_session_count()
    
    # 统计数据库中的用户总数（不包括已删除的）
    total_users = User.query_active().count()
    
    return render_template('index.html', 
                         user_count=total_users,
                         session_count=session_count,
                         current_user=current_user_from_session,
                         session_manager=session_manager)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        # 检查手机号是否已存在（只查询未删除的用户）
        if User.get_by_phone(form.phone.data):
            flash('该手机号已被注册', 'danger')
            return redirect(url_for('register'))
        # 检查邮箱是否已存在（只查询未删除的用户）
        if User.query_active().filter_by(email=form.email.data).first():
            flash('该邮箱已被注册', 'danger')
            return redirect(url_for('register'))
        # 创建新用户（默认为普通用户）
        user = User(
            phone=form.phone.data,
            email=form.email.data,
            password=form.password.data,
            role='USER'  # 明确指定为普通用户
        )
        db.session.add(user)
        db.session.commit()
        flash('注册成功，请登录', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # 只查询未删除的用户
        user = User.get_by_phone(form.phone.data)
        if user and user.verify_password(form.password.data):
            # 更新最后登录时间
            user.last_login_at = datetime.utcnow()
            db.session.commit()
            
            # 多用户模式：添加session（浏览器独立的session）
            session_manager = get_session_manager()
            session_manager.add_session(user.id)
            session.permanent = True
            
            # 检查是否需要强制修改密码
            if user.password_reset_required:
                flash(f'{user.phone} 登录成功，请先修改密码', 'warning')
                return redirect(url_for('force_change_password'))
            
            flash(f'{user.phone} 登录成功', 'success')
            return redirect(url_for('index'))
        else:
            flash('手机号或密码错误', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    """退出当前用户（多用户模式下只退出当前session）"""
    session_manager = get_session_manager()
    current_session = session_manager.get_current_session()
    
    if current_session:
        session_manager.remove_session(current_session.id)
        flash('已退出当前用户', 'success')
    
    # 如果还有其他session，切换到其他用户
    if session_manager.get_session_count() > 0:
        new_user = session_manager.get_current_user()
        if new_user:
            flash(f'已自动切换到 {new_user.phone}', 'info')
        return redirect(url_for('index'))
    
    # 没有session了，跳转到登录页
    flash('已退出所有用户', 'success')
    return redirect(url_for('login'))

@app.route('/user_management', methods=['GET'])
@admin_required
def user_management():
    # 获取搜索和分页参数
    phone = request.args.get('phone', '')
    email = request.args.get('email', '')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # 构建查询（只查询未删除的用户）
    query = User.query_active()
    
    if phone:
        query = query.filter(User.phone.like(f'%{phone}%'))
    if email:
        query = query.filter(User.email.like(f'%{email}%'))
    
    # 分页查询
    users = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('user_management.html', users=users)


@app.route('/delete_user/<int:user_id>', methods=['POST'])
@admin_required
def delete_user(user_id):
    """删除用户（逻辑删除）"""
    user = User.query.get_or_404(user_id)
    
    # 不能删除管理员
    if user.is_admin():
        flash('不能删除管理员', 'danger')
        return redirect(url_for('user_management'))
    
    # 逻辑删除（不是物理删除）
    user.is_deleted = True
    db.session.commit()
    flash(f'用户 {user.phone} 已删除', 'success')
    return redirect(url_for('user_management'))


# ==================== 多用户会话管理 ====================

@app.route('/switch_user/<session_id>')
def switch_user(session_id):
    """切换到指定用户session"""
    session_manager = get_session_manager()
    
    if session_manager.switch_session(session_id):
        user = session_manager.get_current_user()
        if user:
            flash(f'已切换到 {user.phone}', 'success')
    else:
        flash('切换失败，会话可能已过期', 'danger')
    
    return redirect(url_for('index'))


@app.route('/multi_user_manager')
def multi_user_manager():
    """多用户管理页面"""
    session_manager = get_session_manager()
    sessions = session_manager.get_all_sessions()
    
    return render_template('multi_user_manager.html', 
                         sessions=sessions,
                         current_session_id=session_manager.current)


@app.route('/logout_session/<session_id>')
def logout_session(session_id):
    """退出指定session"""
    session_manager = get_session_manager()
    session_manager.remove_session(session_id)
    flash('已退出指定用户', 'success')
    
    # 如果没有其他session了，跳转到登录页
    if session_manager.get_session_count() == 0:
        return redirect(url_for('login'))
    
    return redirect(url_for('multi_user_manager'))


@app.route('/logout_all')
def logout_all():
    """退出所有用户"""
    session_manager = get_session_manager()
    session_manager.remove_all_sessions()
    flash('已退出所有用户', 'success')
    return redirect(url_for('login'))


@app.route('/reset_password/<int:user_id>', methods=['POST'])
@admin_required
def reset_password(user_id):
    """重置用户密码为 111111"""
    user = User.query.get_or_404(user_id)
    
    # 不能重置管理员密码
    if user.is_admin():
        flash('不能重置管理员密码', 'danger')
        return redirect(url_for('user_management'))
    
    # 重置密码并设置需要强制修改密码标记
    user.password = '111111'
    user.password_reset_required = True
    db.session.commit()
    flash(f'用户 {user.phone} 的密码已重置为 111111，该用户下次登录需要修改密码', 'success')
    return redirect(url_for('user_management'))


@app.route('/force_change_password', methods=['GET', 'POST'])
def force_change_password():
    """强制修改密码页面（首次登录后需要修改密码）"""
    # 获取当前用户
    session_manager = get_session_manager()
    user = session_manager.get_current_user()
    
    if not user:
        return redirect(url_for('login'))
    
    # 如果用户不需要强制修改密码，重定向到首页
    if not user.password_reset_required:
        return redirect(url_for('index'))
    
    form = ChangePasswordForm()
    if form.validate_on_submit():
        # 更新密码
        user.password = form.new_password.data
        user.password_reset_required = False
        db.session.commit()
        flash('密码修改成功', 'success')
        return redirect(url_for('index'))
    
    return render_template('force_change_password.html', form=form)