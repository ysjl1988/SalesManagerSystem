from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

# 根据环境选择数据库文件
env = os.environ.get('FLASK_ENV', 'development')
if env == 'production':
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///salesmanager.db'
elif env == 'testing':
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///salesmanager.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(days=1)

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# 初始化迁移工具
migrate = Migrate(app, db)

# 全局上下文处理器 - 提供session管理器给所有模板
@app.context_processor
def inject_session_manager():
    from app.session_manager import get_session_manager
    return dict(session_manager=get_session_manager())

from app import routes
