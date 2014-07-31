import hashlib
from .constants import MESSAGE_STATUS, BOUNCED_EMAIL_HASH_PREFIX


class Bounces(QueueProcessor):
    def register_bounced_email_address(email_addr):
        """
        do something with the bounced email addr
        for now just put in the cache
        """
        email_addr = email_addr.strip().lower()
        email_hash = hashlib.sha1(email_addr).hexdigest()
        self.cache.set(BOUNCE_EMAIL_HASH_PREFIX + email_hash)

    def process_message(self, message):
        """
        set the status BOUNCED for the ses_message_id
        register bounced email address
        """
        msg = json.loads(message)
        ses_message_id = msg['mail']['messageId']
        email_addr = msg['email']['destination']
        is_permanent = msg['mail']['bounce_type'] == 'permanent'
        if is_permanent:
            self.set_status(ses_message_id, MESSAGE_STATUS.BOUNCED)
            self.register_bounced_email_address(email_addr)
    
