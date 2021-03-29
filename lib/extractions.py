# Code to record rules and edit them.
# This is just the persistence and editing of rules.

import sqlite3

# XXX replace this with a configuration thing at some point
PLASTER_DB = './plaster/data.db'

def get_all_webhooks():
    """Loads locally recored rule groups and returns them, one
    per dict entry"""
    # This is going to use a half-assed hack, but I'm just going to use this
    # queue system as a data store
    # Returns a list of dictionaries
    db = sqlite3.connect(PLASTER_DB)
    db.row_factory = sqlite3.Row
    cursor = db.cursor()
    results = cursor.execute('select * from webhooks')
    res = [ dict(item) for item in results.fetchall() ]
    print(res)
    return res


def get_hook_extractor(hook_id):
    """Loads the extractor associated with this webhook.
    """
    # This is going to use a half-assed hack, but I'm just going to use this
    # queue system as a data store
    # Returns a dictionary with 2 keys: extractor and example
    db = sqlite3.connect(PLASTER_DB)
    db.row_factory = sqlite3.Row
    cursor = db.cursor()
    results = cursor.execute('select * from extractions where hook_id=?', (hook_id,))
    res = [ dict(item) for item in results.fetchall() ]
    return {'extractor': res[0]['jmespath_data'], 'example': res[0]['example_message']}


def get_webhook(hook_id):
    """Return a dict as per the row that we're getting out of the webhooks table"""
    db = sqlite3.connect(PLASTER_DB)
    db.row_factory = sqlite3.Row
    cursor = db.cursor()
    results = cursor.execute('select * from webhooks where id=?', (hook_id,))
    res = results.fetchone()
    return dict(res)


# TODO: when editing an existing group, the group name should be separated out, but we should
# confirm that there is only one rule_name in there.
# TODO: is it OK to break out rules individually? Is it helpful? Maybe just one bit text  field?
def save_webhook(hook_id, name, path, queue_name):
    db = sqlite3.connect(PLASTER_DB)
    db.row_factory = sqlite3.Row
    db.isolation_level = None
    cursor = db.cursor()

    if hook_id == 0:  # new row
        cursor.execute('INSERT into webhooks (name, path, queue_name) values (?, ?, ?)',
                       (name, path, queue_name))
    else:
        cursor.execute('update webhooks (name, path, queue_name) values (?, ?, ?) where id=?',
                       (name, path, queue_name, hook_id))
    print(f"The last row id is {cursor.lastrowid}")
    return get_webhook(cursor.lastrowid)


def get_extractor_by_id(ext_id):
    db = sqlite3.connect(PLASTER_DB)
    db.row_factory = sqlite3.Row
    cursor = db.cursor()
    results = cursor.execute('select * from extractors where id=?', (ext_id,))
    res = results.fetchone()
    return dict(res)



def save_extractor(name, hook_id, extractor_text, example_message):
    db = sqlite3.connect(PLASTER_DB)
    db.row_factory = sqlite3.Row
    db.isolation_level = None

    cursor = db.cursor()
    cursor.execute('''
    INSERT into extractions (name, hook_id, jmespath_data, example_message)
    VALUES (?, ?, ?, ?)
    ON CONFLICT(hook_id) DO UPDATE SET',
      name=excluded.name,
      jmespath_data=excluded.jmespath_data,
      example_message=excluded.example_message
    WHERE hook_id=?''' (name, hook_id, extractor_text, example_message, hook_id))
    return get_extractor_by_id(cursor.lastrowid)
