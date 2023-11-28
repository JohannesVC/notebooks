import os
from functools import wraps
from flask import request, jsonify
import jwt
import logging

JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

def custom_jwt_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')

        if not auth_header or 'Bearer ' not in auth_header:
            logging.warning("Bad request: header does not contain authorization token")
            return jsonify({"message": "Bad request: header does not contain authorization token"}), 400

        token = auth_header.split(' ')[1]
        
        try:
            jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        except jwt.ExpiredSignatureError:
            logging.warning("Token has expired")
            return jsonify({"message": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            logging.warning("Invalid token")
            return jsonify({"message": "Invalid token"}), 401

        return f(*args, **kwargs)

    return decorated

def header():
    auth_header = request.headers.get('Authorization')
    token = auth_header.split(' ')[1]
    return jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])

def user_id_in_token():
    return header()['_id']

def fund_link_in_token():
    return header()['fund_link']

def company_link_in_token():
    return header()['company_link']

def user_type_in_token():
    return header()['type']

def username_in_token():
    return header()['name']