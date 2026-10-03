from functools import wraps
from flask import request, jsonify
import jwt
from config import Config

def create_token(user):
    return jwt.encode(
        {"user_id": user.id, "role": user.role},
        Config.SECRET_KEY,
        algorithm="HS256"
    )

def token_required(roles=None):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            header = request.headers.get("Authorization", "")
            if not header.startswith("Bearer "):
                return jsonify({"message": "Authentication required"}), 401
            try:
                payload = jwt.decode(
                    header.split(" ", 1)[1],
                    Config.SECRET_KEY,
                    algorithms=["HS256"]
                )
            except jwt.InvalidTokenError:
                return jsonify({"message": "Invalid or expired token"}), 401

            if roles and payload.get("role") not in roles:
                return jsonify({"message": "Access denied"}), 403

            request.current_user = payload
            return fn(*args, **kwargs)
        return wrapper
    return decorator
