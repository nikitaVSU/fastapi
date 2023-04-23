from typing import Optional
import jwt
import datetime
import psycopg2

SECRET_KEY = "mysecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Конфигурация подключения к базе данных
conn = psycopg2.connect(
    host="localhost",
    database="mydatabase",
    user="myusername",
    password="mypassword",
)

# Функция аутентификации пользователя
def authenticate(username: str, password: str) -> Optional[str]:
    cur = conn.cursor()
    cur.execute(
        "SELECT id, username, password_hash FROM users WHERE username = %s", (username,)
    )
    user = cur.fetchone()
    if user and password == user[2]:
        user_id = user[0]
        token = create_access_token({"sub": user_id})
        return token

# Функция создания JWT токена
def create_access_token(data: dict, expires_delta: Optional[datetime.timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.datetime.utcnow() + expires_delta
    else:
        expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Функция проверки прав доступа пользователя
def is_authorized(token: str) -> bool:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is not None:
            cur = conn.cursor()
            cur.execute(
                "SELECT id FROM users WHERE id = %s", (user_id,)
            )
            user = cur.fetchone()
            if user:
                return True
    except:
        return False

    return False
