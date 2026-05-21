from functools import wraps
from flask import request, jsonify
from config import Config


def require_api_key(f):
    """Decorator that enforces API key auth when API_KEY env var is set."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if Config.API_KEY is None:
            return f(*args, **kwargs)

        provided = (
            request.headers.get("X-API-Key")
            or request.args.get("api_key")
        )
        if not provided or provided != Config.API_KEY:
            return jsonify({"error": "Unauthorized. Valid X-API-Key header required."}), 401

        return f(*args, **kwargs)
    return decorated
