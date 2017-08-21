# -*- coding=utf-8 -*-
import os
import time
import glob
import pika
from colla.utils import get_class_from_module_path
from colla.task import Task
from colla.logger import logger


class Scheduler(object):

    def __init__(self, amqp_url):
        self.parameters = pika.URLParameters(amqp_url)
        self.init_connection()
        self.load_task()


    def init_connection(self):
        while True:
            try:
                self.connection = pika.BlockingConnection(self.parameters)
                self.channel = self.connection.channel()
                return
            except pika.exceptions.ConnectionClosed:
                logger.info("rabbitmq connect fail, retry.....")
                time.sleep(2)


    def load_task(self):
        self.tasks = {}
        for module_path in glob.glob('tasks/*.py'):
            module_path = module_path.replace('/', '.').strip('py').strip('.')
            task_cls = get_class_from_module_path(module_path, Task)
            if task_cls:
                self.tasks[task_cls.queue] = task_cls


    def next_task(self, queue):
        while True:
            logger.debug("get task")
            method, header, body = self.channel.basic_get(queue)
            if not method:
                time.sleep(1)
                continue
            message = Message(method, header, body)
            task_cls = self.tasks[queue]
            task = task_cls.from_jsondata(body)
            task.message = message
            task.scheduler = self
            return task


    def ack_task(self, task):
        self.channel.basic_ack(task.message.method.delivery_tag)


    def requeue(self, task):
        self.channel.basic_publish(exchange='', routing_key=task.queue, body=task.to_body(),
                          properties=pika.BasicProperties(delivery_mode=2))


    def queue_declare(self, queue):
        self.channel.queue_declare(queue, durable=True)


    @classmethod
    def from_settings(cls, settings):
        return cls(settings.AMPQ_URL)


    def close(self):
        logger.info(u"正在关闭rabbitmq")
        # self.channel.close()
        self.connection.close()

    def publish_msg(self, queue, body):
        self.channel.basic_publish(exchange='', routing_key=queue, body=body,
                                    properties=pika.BasicProperties(delivery_mode=2))


    def reconnect(self):
        # self.connection = pika.BlockingConnection(self.parameters)
        # self.channel = self.connection.channel()
        self.init_connection()
        logger.info("rabbitmq connection open state: %s" % self.connection.is_open)



class Message(object):

    def __init__(self, method, header, body):
        self.method = method
        self.header = header
        self.body = body
