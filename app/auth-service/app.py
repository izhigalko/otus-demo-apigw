import logging
import os
import aiohttp_jinja2
import jinja2
from aiohttp import web

from src import auth, forms, jwt, storage


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    templates_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'src/templates')

    app = web.Application(debug=True)
    jwt.setup_jwk(app)
    storage.setup_storage(app, app.private_key)

    app.add_routes(auth.routes)
    app.add_routes(forms.routes)

    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader(templates_dir))

    web.run_app(app, port=8080)
