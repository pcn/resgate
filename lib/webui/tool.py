from json.decoder import JSONDecodeError
import logging
from functools import partial
import json

from aiohttp import web
from pywebio.platform.aiohttp import static_routes, webio_handler
from pywebio.input import input, textarea, select, TEXT, input_group, actions
from pywebio.output import (
    popup,
    put_text,
    put_table,
    put_buttons,
    put_html,
    close_popup,
    put_code,
)
import arrow

from jmespath import exceptions as jmesex

import extractions
import rules


routes = web.RouteTableDef()


def edit_rules():
    """Edit rules

    Edit the rules that process inbound events"""
    my_rules = rules.get_rule_groups()

    selected_rule = select(
        label="Existing rules",
        options=[{"label": rule["name"], "value": rule["id"]} for rule in my_rules],
    )
    # Rules have unique IDs from the database:
    logging.info(f"selected_rule: {selected_rule}")
    use_rule = [r for r in my_rules if r["id"] == int(selected_rule)][0]
    updated_rule = textarea(
        "Edit a rule",
        rows=10,
        code={
            "mode": "python",  # code language
            "theme": "darcula",  # Codemirror theme. Visit https://codemirror.net/demo/theme.html#cobalt to get more themes
        },
        value=f"""\n# Write some datalog to name this - rule_name is special, and for this purpose\nrule_name({use_rule['id']}, "{use_rule['name']}")""",
    )
    put_text(f"The rule added is: {updated_rule}")


def test_extractor(uex_data):
    # put_text(f"data is {uex_data}")
    # The signature according to https://pywebio.readthedocs.io/en/latest/input.html?highlight=actions#pywebio.input.input_group
    # only supports one invalid thing at a time.
    if uex_data["action"].lower() == "test":
        with popup("Applying the example to the extractor"):
            try:
                put_text(
                    extractions.apply_extractor_to_message(
                        uex_data["example"], uex_data["extractor"]
                    )
                )
            except (
                json.decoder.JSONDecodeError,
                jmesex.IncompleteExpressionError,
            ) as e:
                put_text(f"That didn't validate! The error returned is {str(e)}")
        # return [(k, "Test was run") for k, v in uex_data.items()][0]
        return ("actions", "test was run")
    return None


def edit_webhook():
    """Edit webhook and its extractor

    This should be changed to work with a programattically named
    webhook that has a randmoly named inbound address. For now, we
    name it I guess

    """
    my_hooks = extractions.get_all_webhooks()
    my_hooks.append(
        {
            "id": 0,
            "name": "Your new webhook could go here!",
            "path": "Enter the path that this will be matched on",
            "queue_name": "base name for the queue",
        }
    )

    print(my_hooks)
    selected_hook = select(
        label="Existing webhooks",
        options=[
            {
                "label": hook.get("name", "No hook name found"),
                "value": hook.get("id", 0),
            }
            for hook in my_hooks
        ],
    )
    # Rules have unique IDs from the database:
    logging.info(f"selected_hook: {selected_hook}")

    if selected_hook == 0:
        my_extractor = {
            "example": "# New hook example as json - lines beginning with a '#' will be ignored and preserved",
            "extractor": "# New hook extractor: write some jmespath - lines beginning with a '#' will be ignored and preserved",
        }
    else:
        # XXX this doesn't get the hook text from the db, nor does it save it yet
        if selected_hook != 0:
            my_hook = extractions.get_webhook(selected_hook)
        my_extractor = extractions.get_hook_extractor(selected_hook)

        # extractions.apply_extractor_to_message
    updated_extractor = input_group(
        "Hook data and hook extractor",
        [
            input(
                "name", type=TEXT, name="name", value=my_hook["name"], required=True
            ),  # Need to get a way to carry around the IDs
            input(
                "path", type=TEXT, name="path", value=my_hook["path"], required=True
            ),  # Need to get a way to carry around the IDs
            input(
                "queue_name",
                type=TEXT,
                name="queue_name",
                value=my_hook["queue_name"],
                required=True,
            ),  # Need to get a way to carry around the IDs
            textarea(
                "Example message",
                name="example",
                rows=10,
                code={
                    "mode": "python",  # code language
                    "theme": "darcula",  # Codemirror theme. Visit https://codemirror.net/demo/theme.html#cobalt to get more themes
                },
                value=my_extractor["example"],
            ),
            textarea(
                "Edit an extraction rule",
                name="extractor",
                rows=10,
                code={
                    "mode": "python",  # code language
                    "theme": "darcula",  # Codemirror theme. Visit https://codemirror.net/demo/theme.html#cobalt to get more themes
                },
                value=my_extractor["extractor"],
            ),
            actions(
                "actions",
                [
                    {"label": "test", "value": "test"},
                    {"label": "save", "value": "save"},
                ],
                name="action",
                help_text="Save or test",
            ),
        ],
        validate=test_extractor,
    )
    # Pretty much can't be none, but let's follow the example from
    # https://pywebio.readthedocs.io/en/latest/input.html#pywebio.input.actions
    if updated_extractor is not None:
        uex = dict(updated_extractor)
        if uex["action"] == "save":
            webhook_info = extractions.save_webhook(
                selected_hook, uex["name"], uex["path"], uex["queue_name"]
            )
            extractor_info = extractions.save_extractor(
                uex["name"], webhook_info["id"], uex["extractor"], uex["example"]
            )
            put_text(f"{webhook_info} {extractor_info}")
            # Use webhook_info's ID to add/update the extractor


def button_stuff():
    """Without the complexity of doing anything else, try to enable popup buttons.

    Do it"""
    my_hooks = extractions.get_all_webhooks()
    selected_hook_dict = [h for h in my_hooks if h["name"] == "good"][0]
    selected_hook_id = selected_hook_dict["id"]

    # XXX this doesn't get the hook text from the db, nor does it save it yet
    my_hook = extractions.get_webhook(selected_hook_id)
    my_extractor = extractions.get_hook_extractor(selected_hook_id)

    updated_extractor = input_group(
        "Hook data and hook extractor",
        [
            textarea(
                "Example message",
                name="example",
                rows=10,
                code={
                    "mode": "python",  # code language
                    "theme": "darcula",  # Codemirror theme. Visit https://codemirror.net/demo/theme.html#cobalt to get more themes
                },
                value=my_extractor["example"],
            ),
            textarea(
                "Edit an extraction rule",
                name="extractor",
                rows=10,
                code={
                    "mode": "python",  # code language
                    "theme": "darcula",  # Codemirror theme. Visit https://codemirror.net/demo/theme.html#cobalt to get more themes
                },
                value=my_extractor["extractor"],
            ),
            actions(
                "actions",
                [
                    {"label": "test", "value": "test"},
                    {"label": "save", "value": "save"},
                ],
                name="action",
                help_text="Run tests until you get the output you expect, then save",
            ),
        ],
        validate=test_extractor,
    )  # I suspect that this is going to just test the existing data, not somethign that was just typed in, which is really the way
    put_text(updated_extractor)


app = web.Application()
app.add_routes(
    [
        web.get(
            "/tool",
            webio_handler(
                {
                    "edit_rules": edit_rules,
                    "edit_webhook": edit_webhook,
                    "button_stuff": button_stuff,
                }
            ),
        )
    ]
)
