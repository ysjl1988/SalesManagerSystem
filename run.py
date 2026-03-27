from app import app, db
from app.db_init import init_database, check_database


if __name__ == '__main__':
    # 启动前自动初始化数据库
    print("[DB] Checking database...")
    init_database()
    
    if check_database():
        print("[DB] Database OK, starting app...\n")
        app.run(debug=True)
    else:
        print("[DB] Database check failed")
