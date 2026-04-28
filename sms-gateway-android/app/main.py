from starlite import Starlite
from app.sms_routes import sms_router
from app import events, routes

def create_app() -> Starlite:
    app = Starlite(
        route_handlers=[routes.router, sms_router],
        on_startup=[events.create_redis_conn],
        on_shutdown=[events.destroy_redis_conn],
    )
    return app

app = create_app()
