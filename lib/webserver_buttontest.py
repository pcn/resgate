import logging
from functools import partial

from aiohttp import web
import arrow

import extractions
import rules

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)

app = web.Application()
routes = web.RouteTableDef()

from test_support import support
app.add_subapp('/test_support', support.app)

from webui import tool
app.add_subapp('/ui', tool.app)


@routes.get("/")
async def hello_world(request):
    """
    Just a test endpoint
    """
    return web.Response(text="Hello, world!")


# It'd probablyb e better to namespace this in a v1 file or such?
@routes.post("/v1/webhook/{hook}")
async def v1_webhook(request):
    """
    A webhook that will accept a message
    """
    hook = request.match_info.get('hook')
    return web.Response(text=f"This could be a webhook! for the hook {hook}")




def run_server():
    web.run_app(app)


app.add_routes(routes)

if __name__ == '__main__':
    run_server()
