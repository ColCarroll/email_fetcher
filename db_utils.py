import sqlite3
from contextlib import contextmanager


from util import DB


def format_schema(schema):
    return ',\n'.join([' '.join(x) for x in schema])


def format_row(row):
    return '({})'.format(",".join(['?' for _ in row]))


class DBHelper(object):
    database = DB

    @contextmanager
    def connector(self):
        try:
            conn = sqlite3.connect(self.database)
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            yield cur
        finally:
            conn.commit()
            cur.close()
            conn.close()

    def query(self, query, *args, **kwargs):
        with self.connector() as cur:
            cur.execute(query, args)
            for row in cur:
                yield row

    def execute(self, query, *args, **kwargs):
        with self.connector() as cur:
            cur.execute(query, args)

    def single_query(self, query, *args):
        for result in self.query(query, *args):
            return result

    def table_exists(self, table_name):
        if self.single_query(
                "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
                table_name):
            return True
        return False

    def create_table(self, table_name, schema):
        self.execute('CREATE TABLE {} ({})'.format(table_name, format_schema(schema)))

    def drop_table(self, table_name):
        self.execute('DROP TABLE IF EXISTS {}'.format(table_name))

    def insert_row(self, table, row):
        query = "INSERT INTO {} values {}".format(
                table, format_row(row))
        self.execute(query, *row)
