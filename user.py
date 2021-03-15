from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash

from flask_login import LoginManager, UserMixin, current_user
from flask_login import logout_user, login_user, login_required


USERS = [
    {
        "id": '1',
        "name": 'ji',
        "password": generate_password_hash('ji')
    },
    {
        "id": '2',
        "name": 'long',
        "password": generate_password_hash('ji')
    },
    {
        "id": '3',
        "name": 'lv',
        "password": generate_password_hash('ji')
    },
    {
        "id": '888',
        "name": '--',
        "password": generate_password_hash('==')
    },
    {
        "id": '4',
        "name": 'sun',
        "password": generate_password_hash('ji')  
    },
    {
        "id": '5',
        "name": 'da',
        "password": generate_password_hash('ji')  
    },
    {
        "id": '5',
        "name": 'jiang',
        "password": generate_password_hash('ji')  
    }
]

def create_user(user_name, password):
    """创建一个用户"""
    user = {
        "name": user_name,
        "password": generate_password_hash(password),
        "id": uuid.uuid4()
    }
    USERS.append(user)

def get_user(user_name):
    """根据用户名获得用户记录"""
    for user in USERS:
        if user.get("name") == user_name:
            return user
    return None

def get_user_by_id(uid):
    """根据用户id获得用户记录"""
    for user in USERS:
        if user.get("id") == uid:
            return user
    return None

def get_name_by_id(uid):
    for user in USERS:
        if user.get("id") == uid:
            return user.get("name")

class User(UserMixin):
    """用户类"""
    def __init__(self, user):
        self.username = user.get("name")
        self.password_hash = user.get("password")
        self.id = user.get("id")

    def verify_password(self, password):
        """密码验证"""
        if self.password_hash is None:
            return False
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        """获取用户ID"""
        return self.id

    @staticmethod
    def get(user_id):
        """根据用户ID获取用户实体，为 login_user 方法提供支持"""
        if not user_id:
            return None
        for user in USERS:
            if user.get('id') == user_id:
                return User(user)
        return None
