import email
import imaplib
import logging

import arrow
from tqdm import tqdm

from util import get_creds
from tables import Messages, Recipients, EmailAddresses, Aliases

INBOX = '"[Gmail]/All Mail"'
SENT = '"[Gmail]/Sent Mail"'
SNIPPET_LENGTH = 255

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MailError(Exception):
    pass


def get_mailbox(box=SENT):
    logger.info("Authenticating to {}".format(box))
    mailbox = imaplib.IMAP4_SSL('imap.gmail.com')
    _, msg = mailbox.login(**get_creds())
    mailbox.select(box, readonly=True)
    return mailbox


def check_result(status):
    if status != 'OK':
        raise MailError('Something went wrong! Status: {}'.format(status))


def get_mailbox_uids(mailbox, fetched_ids):
    status, result = mailbox.uid('search', None, 'ALL')
    check_result(status)
    new_results = [j for j in result[0].decode('utf-8').split() if j not in fetched_ids]
    return new_results


def mail_fetcher(fetched_ids):
    for box in (SENT, INBOX):
        mailbox = get_mailbox(box)
        all_uids = get_mailbox_uids(mailbox, fetched_ids)
        n_emails = len(all_uids)
        logger.info('Fetching {:,d} emails from {:s}'.format(n_emails, box))
        for uid in tqdm(all_uids):
            status, result = mailbox.uid('fetch', uid, '(RFC822)')
            check_result(status)
            message = email.message_from_string(result[0][1].decode('utf-8', errors='ignore'))
            yield process_message(message, uid)


def get_message_snippet(message):
    maintype = message.get_content_maintype()
    if maintype == 'multipart':
        for part in message.get_payload():
            if part.get_content_maintype() == 'text':
                return part.get_payload(decode=True)[:SNIPPET_LENGTH].decode(
                    'utf-8', errors='ignore')
    elif maintype == 'text':
        return message.get_payload(decode=True)[:SNIPPET_LENGTH].decode('utf-8', errors='ignore')


def get_recipients(message):
    recipients = []
    for role in ('Bcc', 'Cc', 'To', 'From'):
        if message[role] is not None:
            members = [email.utils.parseaddr(str(j)) for j in message[role].split(',\r\n')]
            for alias, address in members:
                recipients.append({
                    'alias': alias,
                    'email_address': address,
                    'role': role
                })
    return recipients


def get_date(message):
    date_fmt = 'D MMM YYYY HH:mm:ss'
    msg_date = message['Date']
    if msg_date:
        return arrow.get(msg_date[5:], date_fmt).timestamp
    return 0


def process_message(message, uid):
    data = {}
    data['uid'] = int(uid)
    data['sent'] = get_date(message)
    data['subject'] = message['Subject']
    data['snippet'] = get_message_snippet(message)
    data['recipients'] = get_recipients(message)
    return data


def build_db():
    messages = Messages()
    recipients = Recipients()
    email_addresses = EmailAddresses()
    aliases = Aliases()
    for message in mail_fetcher(messages.get_all_uids()):
        message_id = messages.insert(**message)
        for recipient in message['recipients']:
            recipient['message_id'] = message_id
            email_address_id = email_addresses.insert(**recipient)
            recipient['email_address_id'] = email_address_id
            alias_id = aliases.insert(**recipient)
            recipient['alias_id'] = alias_id
            recipients.insert(**recipient)

if __name__ == '__main__':
    build_db()
