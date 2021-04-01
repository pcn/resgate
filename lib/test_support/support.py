import logging


from aiohttp import web
import arrow

routes = web.RouteTableDef()
app = web.Application()

# Todo: move this to only getting invoked when testing
@routes.post("/testv1/{verity}/{dt_str}")
async def bool_until(request):
    """Returns the 'verity' string of 'true' or 'false' (strings to match json truth literals)
    until the time specified, when it'll return the opposiite.

    Times are all going to be utc, which is what it is

    This should be moved into a separate testing module, I think.
    """
    verity = request.match_info.get('verity')
    dt_str = request.match_info.get('dt_str')
    dt_fmt = "%Y-%m-%d_%H:%M:%S"
    try:
        until_dt = arrow.Arrow.strptime(dt_str, dt_fmt)
        logging.debug(until_dt)
    except Exception as e:
        # Note: this is not a good default value, but if it works
        # for now, come back to this later
        until_dt = arrow.Arrow.utcnow()
        logging.debug("I have no idea what exception to expect here")
    now_dt = arrow.Arrow.utcnow()
    if verity.lower() == "true":
        before = True
    elif verity.lower() == "false":
        before = False
    else:
        # xxx log error
        return web.Response(text=None)

    if until_dt < now_dt:
        logging.debug("until is before now, returning the opposite")
        return web.Response(text=str(not before).lower())
    logging.debug(f"until is after now, returning the verity {verity}")
    return web.Response(text=str(before).lower())


app.add_routes(routes)
