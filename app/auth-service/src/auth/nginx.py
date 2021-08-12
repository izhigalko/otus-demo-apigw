from aiohttp import web


def get_headers(*_):
    return dict()


async def on_auth_fail(*_):
    raise web.HTTPUnauthorized()
