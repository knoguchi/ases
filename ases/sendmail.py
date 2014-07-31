from boto.ses import connect_to_region
from .constants import SES_MESSAGE_ID_PREFIX, SES_MAX_MESSAGES

class Sendmail(QueueProcessor):
    def __init__(self, sqs, queue_name, pool_size):
        super(Sendmail, self).__init__(sqs, queue_name, pool_size)
        # connect to SES
        self.ses = connect_to_region(self.region, aws_access_key_id=config.aws_key, aws_secret_access_key=config.aws_secret)

    def ses_sendmail(self, local_message_id, message):
        """
        send an email to SES
        """
        cache_key = SES_MESSAGE_ID_PREFIX + ses_message_id
        if self.cache.get(cache_key, local_message_id):
            msg = "duplicate local message ID found: {}".format(local_message_id)
            log.warn(msg)
            raise DuplicateLocalMessageID(msg, local_message_id)

        self.cache.set(cache_key, local_message_id)
        ses_message_id = self.ses.write(message)
        if not ses_message_id:
            self.cache.delete(cache_key)
            return
        return ses_message_id

    def process_message(self, message):
        """
        pump out a set of messages from the sendmail queue
        send one by one
        runs forever
        """
        local_message_id = self.get_local_message_id(message)
        try:
            ses_message_id = self.ses_sendmail(message)
            if ses_message_id:
                self.queue.delete_message(message)
            else:
                # we leave the message in the queue.
                pass
        except DuplicateLocalMesageID, e:
            self.error_queue.put(message)
            self.queue.delete_message(message)

    def _push_email_to_ses_sendmail_queue(self, local_message_id, email):
        payload = email.to_payload()
        msg = self.queue.new_message(body=payload)
        # write() may return False or raise exception if not successful.
        return self.queue.write((local_message_id, msg))

    def get_email_status_by_local_message_id(self, local_message_id):
        assert self.cache
        ses_message_id = self.cache(LOCAL_MESSAGE_ID_PREFIX + local_message_id)
        status = self.cache(SES_MESSAGE_STATUS_PREFIX + ses_message_id)
        return status


class Email(object):
    def __init__(self, sender, recipients, cc, bcc, reply_to, subject, body, encoding=None, local_message_id=None):
        """
        sender: (name, email_addr)
        recipients: list of (name, email_addr)
        cc: list of (name, email_addr)
        bcc: list of (name, email_addr)
        reply_to: (name, email_addr)
        subject: string or unicode
        body: string or unicode
        encoding: RFC conforming encoding string.  Pick optimal encoding if not specified
        local_message_id: string.
        """
        if not local_message_id:
            local_message_id = uuid()
        self.sender = sender
        self.recpients = recipients
        self.cc = cc
        self.bcc = bcc
        self.reply_to = reply_to
        self.subject = subject
        self.body = body
        self.encoding = encoding
        # Amazon overwrites the messageId in the header
        self.local_message_id = local_message_id


class DuplicateLocalMessageID(Exception):
    def __init__(self, message, local_message_id):
        super(DuplicateLocalMessageID, self).__init__(message, local_message_id)
