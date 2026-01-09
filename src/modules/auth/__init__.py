from auth.api import routes as _auth_routes
from auth.api.routes import router as auth_router
from auth.containers.auth import AuthContainer

auth_routes = [_auth_routes]

__all__ = ["auth_router", "AuthContainer", "auth_routes"]
