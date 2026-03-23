from flask import render_template, redirect, url_for, request, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime
from app import app, db
from app.models.user import User
from app.forms import RegistrationForm, LoginForm

@app.route('/')
def index():
    user_count = 0
    if current_user.is_authenticated:
        user_count = User.query.count()
    return render_template('index.html', user_count=user_count)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        # 检查手机号是否已存在
        if User.query.filter_by(phone=form.phone.data).first():
            flash('该手机号已被注册', 'danger')
            return redirect(url_for('register'))
        # 检查邮箱是否已存在
        if User.query.filter_by(email=form.email.data).first():
            flash('该邮箱已被注册', 'danger')
            return redirect(url_for('register'))
        # 创建新用户
        user = User(
            phone=form.phone.data,
            email=form.email.data,
            password=form.password.data
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
        user = User.query.filter_by(phone=form.phone.data).first()
        if user and user.verify_password(form.password.data):
            login_user(user)
            # 更新最后登录时间
            user.last_login_at = datetime.utcnow()
            db.session.commit()
            session.permanent = True
            flash('登录成功', 'success')
            return redirect(url_for('index'))
        else:
            flash('手机号或密码错误', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('已退出登录', 'success')
    return redirect(url_for('index'))

@app.route('/user_management', methods=['GET'])
@login_required
def user_management():
    # 获取搜索和分页参数
    phone = request.args.get('phone', '')
    email = request.args.get('email', '')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # 构建查询
    query = User.query
    
    if phone:
        query = query.filter(User.phone.like(f'%{phone}%'))
    if email:
        query = query.filter(User.email.like(f'%{email}%'))
    
    # 分页查询
    users = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('user_management.html', users=users)