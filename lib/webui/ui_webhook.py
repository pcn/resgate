import json.decoder
import logging
import json
import pprint

from pywebio.input import input, textarea, select, TEXT, input_group, actions
from pywebio.output import popup, put_text, put_code, put_row

from jmespath import exceptions as jmesex

import extractions
import rules

DEFAULT_HOOK = {
    "name": "Enter a new name",
    "path": "Enter the path for this hook",
    "queue_name": "Enter the queue name",
}

DEFAULT_EXTRACTOR = {
    "example": "# New hook example as json - lines beginning with a '#' will be ignored and preserved",
    "extractor": "# New hook extractor: write some jmespath - lines beginning with a '#' will be ignored and preserved",
}


def test_extractor(uex_data):
    # The signature according to https://pywebio.readthedocs.io/en/latest/input.html?highlight=actions#pywebio.input.input_group
    # only supports one invalid thing at a time.
    failures = list()

    with popup("Applying the example to the extractor"):
        try:
            if uex_data["name"] == DEFAULT_HOOK["name"]:
                put_text("You need to provide a unique name for this hook")
                failures.append(["name", "Name is not changed from the default"])
            if uex_data["path"] == DEFAULT_HOOK["path"]:
                put_text("You need to provide a unique path for this hook")
                failures.append(
                    [
                        "path",
                        "The path for the webhook is not changed from the default",
                    ]
                )
            if uex_data["queue_name"] == DEFAULT_HOOK["queue_name"]:
                put_text("You need to provide a unique queue_name for this hook")
                failures.append(
                    [
                        "queue_name",
                        "The queue_name for the webhook is not changed from the default",
                    ]
                )
            put_text(
                extractions.apply_extractor_to_message(
                    uex_data["example"], uex_data["extractor"]
                )
            )
        except json.decoder.JSONDecodeError as e:
            put_text(f"The json didn't validate! The error returned is {str(e)}")
            failures.append(["example", "The example json didn't check out"])
        except (
            jmesex.IncompleteExpressionError,
            jmesex.EmptyExpressionError,
            jmesex.ParseError,
        ) as e:
            put_text(
                f"The jmespath expression didn't validate! The error returned is {str(e)}"
            )
            failures.append(["extractor", "The jmespath expression didn't check out"])
    if failures:
        return (failures[0][0], failures[0][1])
    if uex_data["action"].lower() == "test":
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

    selected_hook_id = select(
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
    logging.info(f"selected_hook: {selected_hook_id}")

    my_hook = dict()
    my_extractor = dict()
    my_hook.update(DEFAULT_HOOK)
    my_extractor.update(DEFAULT_EXTRACTOR)
    if selected_hook_id != 0:
        my_hook = extractions.get_webhook(selected_hook_id)
        my_extractor = extractions.get_hook_extractor(selected_hook_id)

    # TODO: update validator to avoid default hook 0 names
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
                selected_hook_id, uex["name"], uex["path"], uex["queue_name"]
            )
            extractor_info = extractions.save_extractor(
                uex["name"], webhook_info["id"], uex["extractor"], uex["example"]
            )
            put_row(put_text("Webhook"))
            put_row(put_code(pprint.pformat(webhook_info, indent=1)))
            put_row(put_text("Extractor"))
            put_row(put_code(pprint.pformat(extractor_info, indent=1)))
            # Use webhook_info's ID to add/update the extractor
