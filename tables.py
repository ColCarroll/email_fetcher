from db_utils import DBHelper


class Table(DBHelper):
    def __init__(self):
        if not self.table_exists(self.name):
            self.create_table(self.name, self.schema)

    def max_id(self):
        return self.single_query("SELECT max(id) AS id FROM {}".format(self.name))['id']

    def insert(self, **kwargs):
        # remove primary key
        fields = [j for j, _ in self.schema[1:]]
        values = [kwargs[j] for j in fields]
        clause = " AND ".join(["{} = ?".format(field) for field in fields])
        query = """SELECT id FROM {} WHERE {}""".format(self.name, clause)
        result = self.single_query(query, *values)
        if result:
            return result['id']

        self.insert_row(self.name, [None] + [kwargs[j] for j in fields])
        return self.max_id()


class Messages(Table):
    name = 'messages'
    schema = [('id', 'INTEGER PRIMARY KEY'),
              ('uid', 'INTEGER'),
              ('subject', 'TEXT'),
              ('snippet', 'TEXT'),
              ('sent', 'INTEGER')]

    def get_all_uids(self):
        return [str(j['uid']) for j in self.query('SELECT uid FROM {}'.format(self.name))]


class Recipients(Table):
    name = 'recipients'
    schema = [('id', 'INTEGER PRIMARY KEY'),
              ('message_id', 'INTEGER'),
              ('email_address_id', 'INTEGER'),
              ('role', 'TEXT')]


class EmailAddresses(Table):
    name = 'email_addresses'
    schema = [('id', 'INTEGER PRIMARY KEY'),
              ('email_address', 'TEXT')]


class Aliases(Table):
    name = 'aliases'
    schema = [('id', 'INTEGER PRIMARY KEY'),
              ('email_address_id', 'INTEGER'),
              ('alias', 'TEXT')]
