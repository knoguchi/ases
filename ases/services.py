import gevent.monkey
gevent.monkey.patch_all()

from gevent.pool import Pool
from gevent.queue import JoinableQueue, Queue

import signal
import logging
import logging.handlers

# use boto 2.30 or later that supports "Signature Version 4" for a message larger than 64K bytes.
from boto.sqs.connection import SQSConnection
from .constants import QUEUES, AUTH_SERVICE_NAME, AUTH_REGION_NAME, SES_MAX_MESSAGES
                        
class Ases(object):
    def __init__(self, aws_key, aws_secret, region=None, sendmail_queue=None, deliveries_queue=None, bounces_queue=None, complaints_queue=None):
        # connect to SQS
        self.sqs = SQSConnection(aws_key, aws_secret)
        self.sqs.auth_service_name = AUTH_SERVICE_NAME
        self.sqs.auth_region_name = AUTH_REGION_NAME

        # setup queue processors
        self.sendmail = Sendmail(self.sqs, QUEUES.SENDMAIL_QUEUE, SENDMAIL_POOL_SIZE)
        self.deliveries = Deliveries(self.sqs, QUEUES.DELIVERIES_QUEUE, DELIVERIES_POOL_SIZE)
        self.bounces = Bounces(self.sqs, QUEUES.BOUNCES_QUEUE, BOUNCES_POOL_SIZE)
        self.complaints = Complaints(self.sqs, QUEUES.COMPLAINTS_QUEUE, COMPLAINTS_POOL_SIZE)
    
    def start(self):
        self.sendmail.start()
        self.delievries.start()
        self.bounces.start()
        self.complaints.start()

    def stop(self):
        self.sendmail.stop()
        self.delievries.stop()
        self.bounces.stop()
        self.complaints.stop()
