import sqlite3

import click
from flask import current_app, g

# g is a special object unique to every request. It is used to store data that might be accessed by multiple 
# functions during the request.

def get_db():
    if 'db' not in g:
        # sqlite3.connect() establishes connection to the file pointed at by the DATABASE configuration key.
        # sqlite3.Row tells the connection to return rows that behave like dicts. This allows accessing the columns by name
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory - sqlite3.Row
    
    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


# Added Python functions that will run the SQL commands to the db.py file
def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

# Defines command line command to call init_db function
@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

