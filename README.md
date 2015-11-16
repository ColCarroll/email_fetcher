Email Fetcher
=============
1. Runs on python3.5
2. `virtualenv -p /usr/bin/python3 venv && source venv/bin/activate`
3. `pip install -r requirements.txt`
3. Generate an app password [here](https://security.google.com/settings/security/apppasswords)
4. Create a file in the top directory: `.creds.json`.  It should look like this:
{"user": "your_email@gmail.com", "password": "16 digit password generated above"}
5. `python get_data.py`
6.  After a while, you'll have an sqlite3 database in `database/emails.db`.
