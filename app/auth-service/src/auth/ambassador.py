from aiohttp import web


def get_headers(_, session):
    return {
        'Authorization': f"Bearer {session['x-auth-token']}"
    }


async def on_auth_fail(req: web.Request, rest_url: str):
    storage = req.app.storage
    key = storage.create_state(rest_url)
    raise web.HTTPFound(f'{req.scheme}://{req.host}/auth/login?state={key}')
