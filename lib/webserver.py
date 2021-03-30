import logging
from functools import partial

from aiohttp import web
from pywebio.platform.aiohttp import static_routes, webio_handler
from pywebio.input import input, textarea, select, TEXT, input_group, actions
from pywebio.output import popup, put_text, put_table, put_buttons, put_html, close_popup, put_code
import arrow

import extractions
import rules


routes = web.RouteTableDef()

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



def edit_rules():
    """Edit rules

    Edit the rules that process inbound events"""
    my_rules = rules.get_rule_groups()

    selected_rule = select(label="Existing rules",
           options = [
               {'label': rule['name'], 'value': rule['id']}
               for rule in my_rules ])
    # Rules have unique IDs from the database:
    logging.info(f"selected_rule: {selected_rule}")
    use_rule = [ r for r in my_rules if r['id'] == int(selected_rule) ][0]
    updated_rule = textarea('Edit a rule', rows=10, code={
        'mode': "python",  # code language
        'theme': 'darcula',  # Codemirror theme. Visit https://codemirror.net/demo/theme.html#cobalt to get more themes
    }, value=f'''\n# Write some datalog to name this - rule_name is special, and for this purpose\nrule_name({use_rule['id']}, "{use_rule['name']}")''')
    put_text(f'The rule added is: {updated_rule}')


def edit_webhook():
    """Edit webhook

    This should be changed to work with a programatticaly named
    webhook that has a randmoly named inbound address. For now, we
    name it I guess

    """
    my_hooks = extractions.get_all_webhooks()
    my_hooks.append({
        'id': 0,
        'name': 'Your new webhook could go here!',
        'path': 'Enter the path that this will be matched on',
        'queue_name': 'base name for the queue'})

    print(my_hooks)
    selected_hook = select(label="Existing webhooks",
           options = [
               {'label': hook.get('name', 'No hook name found'), 'value': hook.get('id', 0)}
               for hook in my_hooks ])
    # Rules have unique IDs from the database:
    logging.info(f"selected_hook: {selected_hook}")

    def test_extraction(something):
        put_text(dir())

    if selected_hook == 0:
        my_extractor = {
            'example': "# New hook example as json - lines beginning with a '#' will be ignored and preserved",
            'extractor': "# New hook extractor: write some jmespath - lines beginning with a '#' will be ignored and preserved",
            }
    else:
        # XXX this doesn't get the hook text from the db, nor does it save it yet
        if selected_hook != 0:
            my_hook = extractions.get_webhook(selected_hook)
        my_extractor = extractions.get_hook_extractor(selected_hook)
    updated_extractor = input_group( "Hook data and hook extractor", [
        input('name', type=TEXT, name='name', value=my_hook['name'], required=True),  # Need to get a way to carry around the IDs
        input('path', type=TEXT, name='path', value=my_hook['path'], required=True),  # Need to get a way to carry around the IDs
        input('queue_name', type=TEXT, name='queue_name', value=my_hook['queue_name'], required=True),  # Need to get a way to carry around the IDs
        textarea('Example message', name='example', rows=10, code={
            'mode': "python",  # code language
            'theme': 'darcula',  # Codemirror theme. Visit https://codemirror.net/demo/theme.html#cobalt to get more themes
        }, value=my_extractor['example']),
        textarea('Edit an extraction rule', name='extractor', rows=10, code={
            'mode': "python",  # code language
            'theme': 'darcula',  # Codemirror theme. Visit https://codemirror.net/demo/theme.html#cobalt to get more themes
        }, value=my_extractor['extractor']),
        actions('actions', [
            {'label': 'test', 'value':'test'},
            {'label': 'save', 'value':'save'},
        ], name='action', help_text='Save or test')
    ]) # I suspect that this is going to just test the existing data, not somethign that was just typed in, which is really the way
    # Pretty much can't be none, but let's follow the example from
    # https://pywebio.readthedocs.io/en/latest/input.html#pywebio.input.actions
    if updated_extractor is not None:
        uex = dict(updated_extractor)
        if uex['action'] == 'test':
            # Have to make the test into a callback
            put_text(extractions.apply_extractor_to_message(
                uex['example'],
                uex['extractor']))
        if uex['action'] == 'save':
            # print(f"TRYING TO SAVE {updated_extractor['name']}, {updated_extractor['path']}, {updated_extractor['queue_name']}")
            print(f"TRYING TO SAVE {updated_extractor}")

            webhook_info = extractions.save_webhook(
                selected_hook,
                uex['name'],
                uex['path'],
                uex['queue_name'])
            extractor_info = extractions.save_extractor(
                uex['name'],
                webhook_info['id'],
                uex['extractor'],
                uex['example'])
            put_text(f'{webhook_info} {extractor_info}')
            # Use webhook_info's ID to add/update the extractor


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


def run_server():
    web.run_app(app)


app = web.Application()
logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
app.add_routes(routes)
app.add_routes([web.get('/tool', webio_handler({'edit_rules': edit_rules, 'edit_webhook': edit_webhook}))])
