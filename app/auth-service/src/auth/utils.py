from typing import Callable, Awaitable, Dict
from aiohttp import web


GetAdditionalHeaders = Callable[[web.Request, Dict], Dict[str, str]]
OnAuthFail = Callable[[web.Request, str], Awaitable[web.Response]]
