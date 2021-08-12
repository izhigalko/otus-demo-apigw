from aiohttp import web


def get_headers(*_):
    return dict()


async def on_auth_fail(req: web.Request, rest_url: str):
    storage = req.app.storage
    redirect_uri = req.headers.get('X-Forwarded-Uri') or req.headers.get('x-forwarded-uri')
    key = storage.create_state(redirect_uri)
    host = req.headers.get('X-Forwarded-Host') or req.headers.get('x-forwarded-host')
    raise web.HTTPFound(f'{req.scheme}://{host}/auth/login?state={key}')
