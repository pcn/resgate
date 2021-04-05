from aiohttp import web

routes = web.RouteTableDef()

app = web.Application()
# It'd probably be better to namespace this in a v1 file or such?
@routes.post("/v1/webhook/{hook}")
async def v1_webhook(request):
    """
    A webhook that will accept a message
    """
    hook = request.match_info.get('hook')
    return web.Response(text=f"This could be a webhook! for the hook {hook}")
