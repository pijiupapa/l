# -*- coding=utf-8 -*-
import pika
import json
from pymongo import MongoClient
from cron import settings
# from colla.logger import logger



class TaskMaker(object):

    mongo = False

    def __init__(self):
        if self.mongo:
            self.init_mongo()
        self.init_queue()
        self.make_task()
        self.close()

    def init_mongo(self):
        self.client = MongoClient(host=settings.mongo_host, port=settings.mongo_port)
        self.db = self.client[settings.mongo_name]
        if getattr(settings, "mongo_user", None) and getattr(settings, "mongo_password", None):
            self.db.authenticate(settings.mongo_user, settings.mongo_password)

    def init_queue(self):
        parameters = pika.URLParameters(settings.rabbitmq_url)
        self.connection = pika.BlockingConnection(parameters)
        self.channel = self.connection.channel()

    def make_task(self):
        pass

    def send_task(self, queue, data):
        self.declare_queue(queue)
        self.channel.basic_publish(exchange='', routing_key=queue,
                    body=json.dumps(data, encoding='utf-8'),
                    properties=pika.BasicProperties(delivery_mode=2))

    def declare_queue(self, queue):
        self.channel.queue_declare(queue, durable=True)

    def close(self):
        if self.mongo:
            self.client.close()
        self.connection.close()
