import logging
from aiohttp import web, hdrs


from .utils import GetAdditionalHeaders, OnAuthFail
from . import ambassador, istio, nginx, traefik

routes = web.RouteTableDef()


async def auth(req: web.Request, *, get_headers: GetAdditionalHeaders, on_fail: OnAuthFail):
    headers = ', '.join(f'{k}: {v}' for k, v in req.headers.items())
    logging.info(headers)

    storage = req.app.storage
    session_id = req.cookies.get('session_id')
    session = storage.get_session(session_id)

    if not session:
        response = await on_fail(req, req.match_info.get('req_url'))
        return response

    additional = get_headers(req, session)
    headers = {
        **session,
        **additional
    }

    return web.Response(headers=headers)


@routes.route(hdrs.METH_ANY, '/.well-known/jwks.json')
async def jwks(req: web.Request):
    key = req.app.public_key
    return web.json_response({
        'keys': [key.as_dict(add_kid=True)]
    })


@routes.route(hdrs.METH_ANY, '/auth/ambassador{req_url:/?.*}')
async def ambassador_auth(req: web.Request):
    response = await auth(req, get_headers=ambassador.get_headers, on_fail=ambassador.on_auth_fail)
    return response


@routes.route(hdrs.METH_ANY, '/auth/istio{req_url:/?.*}')
async def istio_auth(req: web.Request):
    response = await auth(req, get_headers=istio.get_headers, on_fail=istio.on_auth_fail)
    return response


@routes.route(hdrs.METH_ANY, '/auth/nginx{req_url:/?.*}')
async def nginx_auth(req: web.Request):
    response = await auth(req, get_headers=nginx.get_headers, on_fail=nginx.on_auth_fail)
    return response


@routes.route(hdrs.METH_ANY, '/auth/traefik{req_url:/?.*}')
async def traefik_auth(req: web.Request):
    response = await auth(req, get_headers=traefik.get_headers, on_fail=traefik.on_auth_fail)
    return response
