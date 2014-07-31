class Deliveries(QueueProcessor):
    """
    deliveries notification porcessing
    """
    def process_message(self, message):
        """
        set the status DELIVERED for ses_message_id
        """
        msg = json.loads(message)
        ses_message_id = msg['mail']['messageId']
        self.set_status(ses_message_id, MESSAGE_STATUS.DELIVERED)
