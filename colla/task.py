# -*- coding=utf-8 -*-
import copy
import json
import pika


class NOT_PROVIDED:
    pass


class InvaidTaskFormat(Exception):
    pass


class Field(object):

    def __init__(self, default=NOT_PROVIDED, null=False):
        self.default=default
        self.null = null

    def has_default(self):
        return self.default is not NOT_PROVIDED

    def get_default(self):
        return self.default

    def validate(self, value):
        pass

    def get_clean_value(self, value):
        return value


class IntegerField(Field):

    def validate(self, value):
        pass


    def get_clean_value(self, value):
        pass



class TaskMeta(type):

    def __new__(mcs, class_name, bases, attrs):
        cls = super(TaskMeta, mcs).__new__(mcs, class_name, bases, attrs)

        fields = {}
        for name, value in attrs.iteritems():
            if isinstance(value, Field):
                fields[name] = copy.deepcopy(value)
        cls._fields = fields
        return cls


class Task(object):

    __metaclass__ = TaskMeta

    queue = None

    def __init__(self, **kwargs):
        fields_value = {}
        for name, field in self._fields.items():
            if name in kwargs:
                value = kwargs[name]
                setattr(self, name, value)
                fields_value[name] = value
                del kwargs[name]
            elif field.has_default():
                default = field.get_default()
                setattr(self, name, default)

        self._fields_value = fields_value

        self.meta = {}
        self.meta.update(kwargs)
        # for key, value in kwargs.items():
            # setattr(self, key, value)


    @classmethod
    def from_jsondata(cls, jsondata):
        data = json.loads(jsondata, encoding='utf-8')
        return cls(**data)

    def ack(self):
        self.scheduler.ack_task(self)

    def in_queue(self):
        self.scheduler.requeue(self)


    def to_body(self):
        return json.dumps(self._fields_value, encoding='utf-8')

    def back_to_queue(self, queue, body):
        self.scheduler.queue_declare(queue)
        self.scheduler.channel.basic_publish(exchange='', routing_key=queue, body=body,
                                                 properties=pika.BasicProperties(delivery_mode=2))
