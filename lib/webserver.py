import logging
from functools import partial

from aiohttp import web
import arrow

import extractions
import rules
import api

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)

app = web.Application()
routes = web.RouteTableDef()

from test_support import support
app.add_subapp('/test_support', support.app)

from webui import tool
app.add_subapp('/ui', tool.app)


from apiv1 import app as appv1
app.add_subapp('/v1', appv1)


@routes.get("/")
async def hello_world(request):
    """
    Just a test endpoint
    """
    return web.Response(text="Hello, world!")




def run_server():
    web.run_app(app)


app.add_routes(routes)

if __name__ == '__main__':
    run_server()
