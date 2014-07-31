import hashlib
from .constants import MESSAGE_STATUS, COMPLAINTED_EMAIL_ADDR_PREFIX

class Complaints(QueueProcessor):
    """
    complaints notification processing
    """
    def register_complainted_email_address(email_addr):
        """
        do something with the bounced email addr
        for now just put in the cache
        """
        email_addr = email_addr.strip().lower()
        email_hash = hashlib.sha1(email_addr).hexdigest()
        self.cache.set(COMPLAINTED_EMAIL_HASH_PREFIX + email_hash)

    def process_message(self, message):
        """
        set the status COMPLAINT for the ses_message_id
        register complainted email address
        """
        msg = json.loads(message)
        ses_message_id = msg['mail']['messageId']
        email_addr = msg['email']['destination']
        is_permanent = msg['mail']['bounce_type'] == 'permanent'
        if is_permanent:
            self.set_status(ses_message_id, MESSAGE_STATUS.COMPLAINTED)
            self.register_complainted_email_address(email_addr)
