import aiohttp_jinja2
from aiohttp import web, hdrs

routes = web.RouteTableDef()


@routes.route(hdrs.METH_GET, '/logout')
async def login(req: web.Request):
    storage = req.app.storage
    session_id = req.cookies.get('session_id')
    storage.remove_session(session_id)
    return web.Response(text='Cya')


@routes.route(hdrs.METH_GET, '/login')
async def login(req: web.Request):
    state_key = req.query.get('state')
    return aiohttp_jinja2.render_template('login.html', req, dict(state_key=state_key))


@routes.route(hdrs.METH_POST, '/login')
async def login(req: web.Request):
    storage = req.app.storage
    data = await req.post()
    username = data.get('username')
    state_key = data.get('state')

    session_id = storage.create_session(username=username)
    state = storage.pop_state(state_key)

    if state:
        response = web.HTTPFound(state['req_url'])
    else:
        response = web.Response(status=200, text='Logged in')

    response.set_cookie('session_id', session_id)
    return response
