from commonthread.settings import JWT_SECRET_KEY,JWT_REFRESH_SECRET_KEY
import datetime
import jwt

def generate_access_token(user_id):
    payload = {
        'sub': user_id,
        'exp': datetime.datetime.now() + datetime.timedelta(hours = 2),
        'iat': datetime.datetime.now()
    }
    return jwt.encode(payload,JWT_SECRET_KEY,algorithm = 'HS256')

def generate_refresh_token(user_id):
    payload = {
        'sub': user_id,
        'exp': datetime.datetime.now() + datetime.timedelta(days=7),
        'iat': datetime.datetime.now()
    }
    return jwt.encode(payload,JWT_REFRESH_SECRET_KEY,algoritm ='HS256')

def decode_refresh_token(token):
    return jwt.decode(token,JWT_REFRESH_SECRET_KEY,algoritm ='HS256')