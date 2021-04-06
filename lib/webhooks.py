# Code to record rules and edit them.
# This is just the persistence and editing of rules.

import json

import jmespath
import sqlite3
import logging

import utils

# XXX replace this with a configuration thing at some point
PLASTER_DB = './plaster/data.db'

def get_all_webhooks():
    """Loads locally recorded rule groups and returns them, one
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


def get_hook_extractor(hook_id=0, name="", path=""):
    """Loads the entry point extractor associated with this webhook.
    """
    cursor = utils.open_db()
    if hook_id != 0:
        result = cursor.execute('select * from webhooks where hook_id=?', (hook_id,))
    elif name != "":
        result = cursor.execute('select * from wwebhooks where name=?', (name,))
    elif path != "":
        result = cursor.execute('select * from webhooks where path=?', (path,))
    else:
        logging.error("Neither a hook id nor a name nor a path was provided")
    res = result.fetchone()
    # The below is for the front-end. Is this a bad idea?
    if not res:
        return {
            'extractor': "",
            'example_message': "" }

    return {'extractor': res[0]['jmespath_data'], 'example_message': res[0]['example_message']}


# XXX: Here or extractors?
def extract_hook(inbound_data, hook_id=0, hook_name="", hook_path="", ):
    """Inbound data is a dictionary containing data deserialized from the request or a test
    which the jmespath expression will be used to extract.
    """
    hook_extractor = get_hook_extractor(hook_id, hook_name, hook_path)
    try:
        pth = jmespath.compile(utils.remove_commented_lines(hook_extractor['extractor']))
        return pth.search(json.loads(inbound_data))
    except jmespath.exceptions.EmptyExpressionError:
        logging.error("The extractor for the hook was empty")
        return {}


def get_webhook(hook_id=0, path=""):
    """Return a dict as per the row that we're getting out of the webhooks table"""
    cursor = utils.open_db()
    if hook_id != 0:
        result = cursor.execute('select * from webhooks where id=?', (hook_id,))
    elif path != "":
        result = cursor.execute('select * from webhooks where path=?', (path,))
    else:
        logging.error("Neither a hook id nor a path was provided")
    res = result.fetchone()
    if res:
        return dict(res)
    logging.warning(f"No webhook returned in a query of {hook_id}, {path}")
    return {}


def get_webhook(hook_id=0, path='/'):
    """Return a dict as per the row that we're getting out of the webhooks table"""
    db = sqlite3.connect(PLASTER_DB)
    db.row_factory = sqlite3.Row
    cursor = db.cursor()
    if hook_id != 0:
        results = cursor.execute('select * from webhooks where id=?', (hook_id,))
    elif path != '/':
        results = cursor.execute('select * from webhooks where path=?', (path,))

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
