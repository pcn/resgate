# Code to record rules and edit them.
# This is just the persistence and editing of rules.

import json

import jmespath
import sqlite3
import logging

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
    if len(res) == 0:
        return {
            'extractor': "",
            'example': "" }

    return {'extractor': res[0]['jmespath_data'], 'example': res[0]['example_message']}


def get_webhook(hook_id):
    """Return a dict as per the row that we're getting out of the webhooks table"""
    db = sqlite3.connect(PLASTER_DB)
    db.row_factory = sqlite3.Row
    cursor = db.cursor()
    results = cursor.execute('select * from webhooks where id=?', (hook_id,))
    res = results.fetchone()
    if res:
        return dict(res)
    return {}


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
        use_hook_id = dict(cursor.execute('select id from webhooks order by id desc limit 1;').fetchone())['id']
    else:
        cursor.execute('UPDATE webhooks set name=?, path=?, queue_name=? WHERE id=?',
                       (name, path, queue_name, hook_id))
        use_hook_id = hook_id
    logging.debug(f"use_hook_id = {use_hook_id}")
    return get_webhook(use_hook_id)


def get_extractor_by_hook_id(hook_id):
    db = sqlite3.connect(PLASTER_DB)
    db.row_factory = sqlite3.Row
    cursor = db.cursor()
    results = cursor.execute('select * from extractions where hook_id=?', (hook_id,))
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
    ON CONFLICT(hook_id) DO UPDATE SET
      name=excluded.name,
      jmespath_data=excluded.jmespath_data,
      example_message=excluded.example_message
    WHERE hook_id=?''', (name, hook_id, extractor_text, example_message, hook_id))
    return get_extractor_by_hook_id(hook_id)


def remove_commented_lines(text):
    """Removes the commented lines"""
    lines = text.split('\n')
    cleaned_text = "\n".join([l for l in lines if not l.startswith('#')])
    print(f"Cleaned text is {cleaned_text}")
    return cleaned_text



def apply_extractor_to_message(message, extractor):
    """Remove comment lines from the input message and extractor,
    then Apply a jmespath extractor the provided message, and return the resulting mapping"""
    msg_data = json.loads(remove_commented_lines(message))
    uncommented_extractor = remove_commented_lines(extractor)
    return jmespath.search(uncommented_extractor, msg_data)
