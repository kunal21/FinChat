from flask import Blueprint

# each sub‑module defines blueprint objects; import them so they register
from .auth import bp as auth_bp
from .users import bp as users_bp
from .assets import bp as assets_bp
from .items import bp as items_bp
from .accounts import bp as accounts_bp
from .institutions import bp as institutions_bp
from .link_events import bp as link_events_bp
from .link_tokens import bp as link_tokens_bp
from .services import bp as services_bp
from .unhandled import bp as unhandled_bp
from .messages import bp as messages_bp

blueprints: list[Blueprint] = [
    auth_bp,
    users_bp,
    assets_bp,
    items_bp,
    accounts_bp,
    institutions_bp,
    link_events_bp,
    link_tokens_bp,
    services_bp,
    unhandled_bp,
    messages_bp,
]
