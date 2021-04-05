import json.decoder
import logging
import json
import pprint

from pywebio.input import input, textarea, select, TEXT, input_group, actions
from pywebio.output import popup, put_text, put_code, put_row

from jmespath import exceptions as jmesex

import extractions
import rules


DEFAULT_RULE = {
    "id": 0,
    "name": "Enter a new name",
    "rule": """# New rule example - lines beginning with a '#' will be ignored and preserved
rule_name("Put your shiny new rule name here")
""",
}


# I'm going to want to test rules, but I'm considering
# conditional inclusion, so I'm not sure how to make this work?
# probably via testing with a particular webhook and its
# test data. But them I'm going to want additional test data
# since the default test data is not going to be able to
# accommodate multiple different services.
def test_rules(rules_data):
    pass


def edit_rules():
    """Edit rules

    Edit the rules that process inbound events"""
    my_rules = rules.get_all_rules()
    my_rules.append(DEFAULT_RULE)

    selected_rule_id = select(
        label="Existing rules",
        options=[{"label": rule["name"], "value": rule["id"]} for rule in my_rules],
    )
    # Rules have unique IDs from the database:
    logging.info(f"selected_rule: {selected_rule_id}")
    use_rule = [r for r in my_rules if r["id"] == int(selected_rule_id)][0]
    updated_rule = input_group(
        "Rule editing",
        [
            input(
                "name", type=TEXT, name="name", value=use_rule["name"], required=True
            ),  # Need ttextarea(
            textarea(
                "Rule names",
                name="rule",
                rows=10,
                code={
                    "mode": "python",  # code language
                    "theme": "darcula",  # Codemirror theme. Visit https://codemirror.net/demo/theme.html#cobalt to get more themes
                },
                value=f"""{use_rule['rule']}\n""",
            ),
            actions(
                "actions",
                [
                    # {"label": "test", "value": "test"},
                    {"label": "save", "value": "save"},
                ],
                name="action",
                help_text="Save",
            ),
        ],
    )
    if updated_rule is not None:
        rl = dict(updated_rule)
        if rl["action"] == "save":
            rule_info = rules.save_rule(
                rl["name"], rl["rule"], selected_rule_id
            )
            put_row(put_text("Rule"))
            put_row(put_code(pprint.pformat(rule_info, indent=1)))
            # Use webhook_info's ID to add/update the extractor

    put_text(f"The rule added is: {updated_rule}")
