from db_utils import DBHelper


class Table(DBHelper):
    def __init__(self):
        if not self.table_exists(self.name):
            self.create_table(self.name, self.schema())


class Messages(Table):
    name = 'messages'

    def schema(self):
        return [
            ('id', 'INTEGER PRIMARY KEY'),
            ('subject', 'TEXT'),
            ('snippet', 'TEXT'),
            ('sent', 'INTEGER')]

    def insert(self, **kwargs):
        query = """
        SELECT id FROM {0}
        WHERE subject = ? AND sent = ?""".format(self.name)
        result = self.single_query(query, kwargs['subject'], kwargs['sent'])
        if result:
            return result['id']
        self.insert_row(self.name, [None, kwargs['subject'], kwargs['snippet'], kwargs['sent']])
        return self.single_query("SELECT max(id) AS id FROM {}".format(self.name))['id']


class Recipients(Table):
    name = 'recipients'

    def schema(self):
        return [
            ('id', 'INTEGER PRIMARY KEY'),
            ('message_id', 'INTEGER'),
            ('email_address_id', 'INTEGER'),
            ('role', 'TEXT')]

    def insert(self, **kwargs):
        result = self.single_query("""
        SELECT id FROM {0}
        WHERE message_id = {message_id} AND message_id = {message_id}
            AND email_address_id = {email_address_id} AND role = '{role}'""".format(
            self.name, **kwargs))
        if result:
            return result['id']
        self.insert_row(self.name,
                        [None, kwargs['message_id'], kwargs['email_address_id'], kwargs['role']])
        return self.single_query("SELECT max(id) AS id FROM {}".format(self.name))['id']


class EmailAddresses(Table):
    name = 'email_addresses'

    def schema(self):
        return [
            ('id', 'INTEGER PRIMARY KEY'),
            ('email_address', 'TEXT')]

    def insert(self, **kwargs):
        result = self.single_query("SELECT id FROM {} WHERE email_address = '{}'".format(
            self.name, kwargs.get('email_address')))
        if result:
            return result['id']
        self.insert_row(self.name, [None, kwargs['email_address']])

        return self.single_query("SELECT max(id) AS id FROM {}".format(self.name))['id']


class Aliases(Table):
    name = 'aliases'

    def schema(self):
        return [
            ('id', 'INTEGER PRIMARY KEY'),
            ('email_address_id', 'INTEGER'),
            ('alias', 'TEXT')]

    def insert(self, **kwargs):
        result = self.single_query("""
        SELECT id FROM {0}
        WHERE email_address_id = ? AND alias = ?""".format(
            self.name), kwargs['email_address_id'], kwargs['alias'])
        if result:
            return result['id']
        self.insert_row(self.name, [None, kwargs['email_address_id'], kwargs['alias']])
        return self.single_query("SELECT max(id) AS id FROM {}".format(self.name))['id']
