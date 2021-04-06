import logging

from aiohttp import web

import webhooks
import rules

routes = web.RouteTableDef()

app = web.Application()
# It'd probably be better to namespace this in a v1 file or such?
@routes.post("/webhook/{hook_path}")
async def v1_webhook(request):
    """
    A webhook that will accept a message
    """
    hook_path = request.match_info.get('hook_path')
    result = webhooks.get_webhook(path=hook_path)
    # Extract hook data
    hook_data = webhooks.extract_hook(await request.json(), hook_path=hook_path)
    # This probably needs to be transformed somehow
    # pass that into this
    logging.info(f'The result is {result}')
    result = rules.evaluate_rule(name=result['entry_rule_name'], starting_data=hook_data)

    return web.Response(text=f"This could be a webhook! for the hook {result}")

app.router.add_routes(routes)
