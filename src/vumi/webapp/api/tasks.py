import logging
from django.conf import settings
from celery.task import Task

class SendSMSTask(Task):
    routing_key = 'vumi.webapp.sms.send'

class ReceiveSMSTask(Task):
    routing_key = 'vumi.webapp.sms.receive'

class DeliveryReportTask(Task):
    routing_key = 'vumi.webapp.sms.receipt'
