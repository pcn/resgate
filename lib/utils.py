import sqlite3

PLASTER_DB = './plaster/data.db'

def remove_commented_lines(text):
    """Removes the commented lines"""
    lines = text.split('\n')
    cleaned_text = "\n".join([l for l in lines if not l.startswith('#')])
    print(f"Cleaned text is {cleaned_text}")
    return cleaned_text


def open_db(cursor=True, db_path=PLASTER_DB):
    """returns a tuple of a
    db object and a cursor with the row_factory
    set to returning rows, so queries come back
    as dictionaries of colum_name: column_data
    """
    db = sqlite3.connect(db_path)
    db.row_factory = sqlite3.Row
    db.isolation_level = None
    if cursor:
        return db.cursor()
    return db
