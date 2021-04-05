import json.decoder
import logging
import json
import pprint

from aiohttp import web
from pywebio.platform.aiohttp import webio_handler

from jmespath import exceptions as jmesex

import webui.ui_webhook as webhook
import webui.ui_rules as webrules
import extractions
import rules


routes = web.RouteTableDef()


app = web.Application()
app.add_routes(
    [
        web.get(
            "/tool",
            webio_handler(
                {
                    "edit_rules": webrules.edit_rules,
                    "edit_webhook": webhook.edit_webhook,
                }
            ),
        )
    ]
)
