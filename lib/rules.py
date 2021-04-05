# Code to record rules and edit them.
# This is just the persistence and editing of rules.

import logging
import sqlite3
from datalog import easy, reader

import utils

def get_all_rules():
    """Loads locally recored rule groups and returns them, one
    per dict entry"""
    # This is going to use a half-assed hack, but I'm just going to use this
    # queue system as a data store
    # Returns a list of dictionaries
    cursor = utils.open_db()
    results = cursor.execute('select * from rules')
    res = [ dict(item) for item in results.fetchall() ]
    return res


def get_rule(id_=0, name=""):
    """Returns the rule identified with this name"""
    cursor = utils.open_db()
    logging.warning(f"name is {name}")
    results = cursor.execute('select * from rules where name=?', (name,))
    return dict(results.fetchone())


# TODO: when editing an existing group, the group name should be separated out, but we should
# confirm that there is only one rule_name in there.
# TODO: is it OK to break out rules individually? Is it helpful? Maybe just one bit text  field?

# XXX in the middle of figuring out how to handle this so that the id determines this?
# Or maybe some ruiles get hook id, etc
def save_rule(name, rule_text, id_):
    cursor = utils.open_db()
    if id_ == 0:
        cursor.execute('''
    INSERT into rules (name, rule)
    VALUES (?, ?)
    ON CONFLICT(name) DO UPDATE SET
    name=excluded.name,
    rule=excluded.rule
    WHERE name=?''', (name, rule_text, name))
    return get_rule(name=name)



def evaluate_rule(id_=0, name="", starting_data={}):
    """With starting_facts, which is data from a webhook, turn that
    into appropriate declarations (it should be a dictionary of
    mappings of {key: value}, so each of these should be a single item
    where the key is something like "webhook(key, value)" or
    something.

    After that, the loaded rule needs to be added.

    TODO: If the end result is an "include" instruction, then a stack of included instructions
    will be loaded, and re-evaluated with the additional rules.

    """
    rule = get_rule(id_=id_, name=name)
    # Create the initial db
    starting_facts_db = reader.read("".join(
        [f"starting({k}, {v})." for k, v in starting_data.items()]))
    rule_text = utils.remove_commented_lines(rule['text'])
    input_ = reader.read(rule_text)
    state = easy.select(starting_facts_db, rule_text)
    print(rules)
