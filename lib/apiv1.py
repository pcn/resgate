import logging

from aiohttp import web

import webhooks
import rules
import extractions

routes = web.RouteTableDef()

app = web.Application()
# It'd probably be better to namespace this in a v1 file or such?
@routes.post("/webhook/{hook_path}")
async def v1_webhook(request):
    """
    A webhook that will accept a message
    """
    hook_path = request.match_info.get('hook_path')
    logging.debug(f"The hook path is {hook_path}")
    hook_result = webhooks.get_webhook(path=hook_path)
    logging.debug(f"The hook fetching result is {hook_result}")
    # Extract hook data
    extracted_data = extractions.extract_data_from_inbound_hook(await request.json(), hook_id=hook_result['id'])
    # This probably needs to be transformed somehow
    # pass that into this
    logging.info(f'The extracted_data is {extracted_data}')
    rule_result = rules.evaluate_rule(name=hook_result['entry_rule_name'], starting_data=extracted_data)

    return web.Response(text=f"This could be a webhook! for {hook_path} {extracted_data} rule_result: {rule_result}")

app.router.add_routes(routes)
