from app import app, db
from app.models.user import User

def create_test_users():
    # 创建20条测试用户数据
    if User.query.count() < 20:
        for i in range(1, 21):
            phone = f'138000000{i:02d}'
            email = f'user{i}@example.com'
            user = User(
                phone=phone,
                email=email,
                password='Zk123456'
            )
            db.session.add(user)
        db.session.commit()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_test_users()
    app.run(debug=True)