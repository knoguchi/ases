class SqsProcessor(object):
    def __init__(self, sqs, queue_name, pool_size):
        self.sqs = sqs
        self.queue = sqs.create_queue(queue_name)
        self.pool = Pool(pool_size)

    def process_message(self, message):
        raise NotImplemented()

    def worker(self):
        """
        retrieve messages, and process one by one
        """
        while True:
            for message in self.queue.get_messages(SQS_MAX_MESSAGES):
                self.process_message(message)
                self.queue.delete_message(message)
            else:
                # sleep if no messages found in the sendmail queue
                time.sleep(10)
        
    def start(self):
        while True:
            self.pool.spawn(self.worker)
