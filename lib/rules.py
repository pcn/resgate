# Code to record rules and edit them.
# This is just the persistence and editing of rules.

import sqlite3

# XXX replace this with a configuration thing at some point
PLASTER_DIR = './plaster/data.db'

def get_rule_groups():
    """Loads locally recored rule groups and returns them, one
    per dict entry"""
    # This is going to use a half-assed hack, but I'm just going to use this
    # queue system as a data store
    # Returns a list of dictionaries
    db = sqlite3.connect(PLASTER_DIR)
    db.row_factory = sqlite3.Row
    cursor = db.cursor()
    results = cursor.execute('select * from rule_groups')
    res = [ dict(item) for item in results.fetchall() ]
    return res


# TODO: when editing an existing group, the group name should be separated out, but we should
# confirm that there is only one rule_name in there.
# TODO: is it OK to break out rules individually? Is it helpful? Maybe just one bit text  field?
def save_rule_group():
    pass


def save_rule():
    pass


def new_rule():
    pass
