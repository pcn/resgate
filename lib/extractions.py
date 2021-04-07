# Code to record rules and edit them.
# This is just the persistence and editing of rules.

import json

import jmespath
import sqlite3
import logging

import utils

# XXX replace this with a configuration thing at some point
PLASTER_DB = './plaster/data.db'

def get_hook_extractor(hook_id=0, name=""):
    """Loads the entry point extractor associated with this webhook.
    """
    cursor = utils.open_db()
    if hook_id != 0:
        result = cursor.execute('select * from extractions where hook_id=?', (hook_id,))
    elif name != "":
        result = cursor.execute('select * from extractions where name=?', (name,))
    else:
        logging.error("Neither a hook id nor a name nor a path was provided")
    res = dict(result.fetchone())
    # The below is for the front-end. Is this a bad idea?
    if not res:
        return {
            'extractor': "",
            'example_message': "" }
    logging.debug(f"res is {res}")
    return {'extractor': res['jmespath_data'], 'example_message': res['example_message']}


def get_extractor_by_hook_id(hook_id):
    cursor = utils.open_db()
    results = cursor.execute('select * from extractions where hook_id=?', (hook_id,))
    res = results.fetchone()
    return dict(res)


def save_extractor(name, hook_id, extractor_text, example_message):
    cursor = utils.open_db()
    cursor.execute('''
    INSERT into extractions (name, hook_id, jmespath_data, example_message)
    VALUES (?, ?, ?, ?)
    ON CONFLICT(hook_id) DO UPDATE SET
      name=excluded.name,
      jmespath_data=excluded.jmespath_data,
      example_message=excluded.example_message
    WHERE hook_id=?''', (name, hook_id, extractor_text, example_message, hook_id))
    return get_extractor_by_hook_id(hook_id)


# XXX: Here or webhooks?
def apply_extractor_to_message(message, extractor):
    """Remove comment lines from the input message and extractor,
    then Apply a jmespath extractor the provided message, and return the resulting mapping"""
    msg_data = json.loads(utils.remove_commented_lines(message))
    uncommented_extractor = utils.remove_commented_lines(extractor)
    return jmespath.search(uncommented_extractor, msg_data)


# XXX: Here or extractors?
def extract_data_from_inbound_hook(inbound_data, hook_id=0, hook_name="", hook_path="", ):
    """Inbound data is a dictionary containing data deserialized from the request or a test
    which the jmespath expression will be used to extract.
    """
    hook_extractor = get_hook_extractor(hook_id, hook_name)
    try:
        pth = jmespath.compile(utils.remove_commented_lines(hook_extractor['extractor']))
        return pth.search(inbound_data)
    except jmespath.exceptions.EmptyExpressionError:
        logging.error("The extractor for the hook was empty")
        return
