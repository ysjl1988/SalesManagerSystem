"""
数据库自动初始化模块
确保数据库表存在并初始化必要数据
"""
from app import app, db
from app.models.user import User
from app.models.session import UserSession


def init_database():
    """
    自动初始化数据库
    - 创建所有缺失的表
    - 初始化管理员账号（如果不存在）
    """
    with app.app_context():
        # 检查并创建所有表
        db.create_all()
        print("[DB] Tables checked")
        
        # 检查管理员账号
        admin = User.query.filter_by(phone='13564612895').first()
        if not admin:
            admin = User(
                phone='13564612895',
                email='admin@gmail.com',
                password='Zk123456',
                role='ADMIN'
            )
            db.session.add(admin)
            db.session.commit()
            print("[DB] Admin created: 13564612895 / Zk123456")
        else:
            print("[DB] Admin exists")
        
        # 统计信息
        user_count = User.query.filter_by(is_deleted=False).count()
        session_count = UserSession.query.filter_by(is_active=True).count()
        print(f"[DB] Users: {user_count}, Sessions: {session_count}")


def check_database():
    """检查数据库状态，返回是否健康"""
    try:
        with app.app_context():
            # 尝试查询用户表
            User.query.first()
            return True
    except Exception as e:
        print(f"[DB] Check failed: {e}")
        return False


if __name__ == '__main__':
    init_database()
