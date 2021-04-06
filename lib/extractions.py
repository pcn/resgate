# Code to record rules and edit them.
# This is just the persistence and editing of rules.

import json

import jmespath
import sqlite3
import logging

import utils

# XXX replace this with a configuration thing at some point
PLASTER_DB = './plaster/data.db'

def get_hook_extractor(hook_id):
    """Loads the extractor associated with this webhook.
    """
    # This is going to use a half-assed hack, but I'm just going to use this
    # queue system as a data store
    # Returns a dictionary with 2 keys: extractor and example
    cursor = utils.open_db()
    results = cursor.execute('select * from extractions where hook_id=?', (hook_id,))
    res = [ dict(item) for item in results.fetchall() ]
    if len(res) == 0:
        return {
            'extractor': "",
            'example': "" }

    return {'extractor': res[0]['jmespath_data'], 'example': res[0]['example_message']}


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
