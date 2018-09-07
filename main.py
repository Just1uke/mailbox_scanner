# coding: utf-8

from sys import argv

from modules.config import config, MissingConfigurationItem
import datetime
from O365 import Account
import logging
import os


class Main(object):
    def __init__(self):
        logging.basicConfig(level=logging.WARN)

        self.application_id = config['application_id']
        self.client_secret = config['client_secret']

        account = Account((self.application_id, self.client_secret), auth_method='oauth')

        # Absence of this file indicates that we're not logged in to O365.
        if not os.path.isfile('o365_token.txt'):
            # We have to jump through these hoops because OSX limits
            # TTY inputs to 1024 characters - the URL is generally longer than that.
            print(f"Need to authorize this application.\n\n"
                  f"Please visit:\n{account.connection.get_authorization_url()}\n\n"
                  f"When your mailbox finishes loading, put the resulting URL in the 'auth_response_url' section of your config file, then hit enter.")
            input()
            config.reload()
            if config.setdefault('auth_response_url', None):
                account.connection.request_token(config['auth_response_url'])
                config['auth_response_url'] = ''
                config.write()
            else:
                raise MissingConfigurationItem('auth_response_url')

        self.whitelisted_senders = config.setdefault('whitelisted_senders', [])
        self.whitelisted_recipients = config.setdefault('whitelisted_recipients', [])
        self.blacklisted_strings = config.setdefault('blacklisted_strings', [])

        self.mailbox = account.mailbox(config.setdefault('mailbox', None))

        self.look_back_minutes = config.setdefault('look_back_minutes', 5)
        self.look_back_hours = config.setdefault('look_back_hours', 0)

        self.threshold = config.setdefault('threshold', 3)

        self.duration = datetime.timedelta(minutes=self.look_back_minutes, hours=self.look_back_hours)
        self.oldest_date = (datetime.datetime.now(datetime.timezone.utc) - self.duration).strftime("%Y-%m-%dT%H:%M:%SZ")

        self.run()

    def run(self):
        finds = {}

        emails_looked_at = 0

        logging.info('Running.')
        for email in self.mailbox.get_messages(query=f"ReceivedDateTime ge {self.oldest_date}", order_by="ReceivedDateTime asc", limit=None):
            emails_looked_at += 1

            if email.has_attachments:
                email.attachments.download_attachments()
                for attachment in email.attachments:
                    attachment_obj = email.attachments.get_attachement(attachment)['item']
                    if attachment_obj['@odata.type'] == '#microsoft.graph.message':
                        sender = attachment_obj['sender']['emailAddress']['address']
                        recipients = attachment_obj['toRecipients']
                        attachment_content = attachment_obj['body']['content']

                        # Check for blacklisted strings in the attachment
                        if any(word in attachment_content for word in self.blacklisted_strings):
                            # Don't consider an e-mail bad if the recipient is whitelisted.
                            if not any(any(contact['emailAddress']['address'] == whitelisted_email for contact in recipients) for whitelisted_email in
                                       self.whitelisted_recipients):
                                # Don't consider an e-mail bad if the sender is whitelisted.
                                if not any(sender == whitelisted_email for whitelisted_email in self.whitelisted_senders):
                                    # Otherwise, add a hit to the matched user
                                    username = sender.split('@')[0]
                                    finds.setdefault(username, 0)
                                    finds[username] += 1
                                    logging.info(f'Found malicious e-mail for {username}.')
                                else:
                                    logging.info(f'Sender is whitelisted {sender}')
                            else:
                                logging.info('Detected whitelisted recipient.')
                        else:
                            logging.info('No blacklisted words found.')

        # Iterate over the finds from the scan
        for username in finds:
            # If the user has more hits than threshold, alert
            if finds[username] > self.threshold:
                print(f"Detected {username}: {finds[username]} blacklisted e-mails in the past {self.duration}")

                # Additional custom code to auto-suspend the account would go here.

        print(f'\nLooked at a total of {emails_looked_at} e-mails.')


if __name__ == "__main__":
    if len(argv) > 0:
        Main()
    else:
        print('Usage: %s config.yaml' % argv[0])
