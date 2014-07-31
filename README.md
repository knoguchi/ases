THIS IS A WIP PROJECT. IT DOESN'T RUN YET.


Amazon SES sendmail
===================

* concurrent sendmail.  100/sec
* delivery and open view tracking
* bounces and complaints handling

Requirements
============
boto
gevent
redis

Memory Usage
============
This module creates an object for each email.  If the module is configured to store the object in the redis, it may fill up quickly.
The lifetime of the object varies by configuration. 

* Bounces and deliveries notification requires a few seconds to 2 weeks.  Usually sending and delivery are happening in a few seconds unless the destination ISP is not ready to accept.
* Openview and complaints notification takes days.  The recipient needs to open the email, and click complaint.   It's wise to set the retention time max two weeks.

In order to avoid Out of Memory Killer, it's recommended to configure redis with the eviction policy.

AWS Configuration
=============
Configure SQS, SNS, and SES in the following order.

* SQS
  Create 4 queues
	- SES_SENDMAIL_QUEUE
	- SES_BOUNCES_QUEUE
	- SES_COMPLAINTS_QUEUE
	- SES_DELIVERIES_QUEUE

* SNS
  Create 3 topics for bounces, complaints, and deliveries.
	- SES_BOUNCES_TOPIC - subscribe to SES_BOUNCES_QUEUE endpoint using sqs protocol.
	- SES_COMPLAINTS_TOPIC - subscribe to SES_COMPLAINTS_QUEUE endpoint using sqs protocol.
	- SES_DELIVERIES_TOPIC - subscribe to SES_DELIVERIES_QUEUE endpoint using sqs protocol.

* SES
  In the SES console, open `Email Addresses` or `Domains` in the `Verified Senders` section.  Click on the icon for the desired domain, and click `Edit Configuration` button in the `Notifications` section.
  Subscribe to the 3 SNS topic.
	Email Feedback Forwarding: 	disabled
	Bounce Notifications SNS Topic:   SES_BOUNCES_TOPIC
	Complaint Notifications SNS Topic: SES_COMPLAINTS_TOPIC
	Delivery Notifications SNS Topic:  SES_DELIVERIES_TOPIC

Ases Configrution
=================
ases = Ases(aws_key, aws_secret, sendmail_queue, deliveries_queue, bounces_queue, complaints_queue)

Send email
==========
ses_message_id = ases.sendmail(sender, recipient, body. local_message_id=None)

Check status
==============
ases.get_status(ses_message_id)

* Constants
 * MESSAGE_STAUTS
 - UNKNOWN
 - QUEUED
 - PUSHED
 - DELIVERED
 - BOUNCED
 - COMPLAINTED

