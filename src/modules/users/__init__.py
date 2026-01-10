from users.api import routes as _users_routes
from users.api.routes import router as users_router
from users.containers.users import UsersContainer

users_routes = [_users_routes]

__all__ = ["users_router", "UsersContainer", "users_routes"]
