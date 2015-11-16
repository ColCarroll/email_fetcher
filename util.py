import json
import os

DIR = os.path.dirname(os.path.abspath(__file__))
CREDS = os.path.join(DIR, '.creds.json')
DB_DIR = os.path.join(DIR, 'database')
DB = os.path.join(DB_DIR, 'emails.db')

if not os.path.exists(DB_DIR):
    os.mkdir(DB_DIR)


def get_creds():
    if not os.path.exists(CREDS):
        raise IOError('Must supply gmail credentials at {}'.format(CREDS))
    with open(CREDS) as buff:
        credentials = json.load(buff)
    return credentials
