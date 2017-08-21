# -*- encoding:utf-8 -*-
import inspect
import datetime
import time
import pika
from django.conf import LazyObject
from pymongo import MongoClient
from pkgutil import iter_modules
from importlib import import_module
from itertools import izip


def walk_modules(path, load=False):
    """Loads a module and all its submodules from a the given module path and
    returns them. If *any* module throws an exception while importing, that
    exception is thrown back.

    For example: walk_modules('scrapy.utils')
    """

    mods = []
    mod = import_module(path)
    mods.append(mod)
    if hasattr(mod, '__path__'):
        for _, subpath, ispkg in iter_modules(mod.__path__):
            fullpath = path + '.' + subpath
            if ispkg:
                mods += walk_modules(fullpath)
            else:
                submod = import_module(fullpath)
                mods.append(submod)
    return mods


def iter_classes(module_name, baseclass):

    for module in walk_modules(module_name):
        for obj in vars(module).itervalues():
            if inspect.isclass(obj) and issubclass(obj, baseclass) and obj.__module__ == module.__name__:
                yield obj


def get_class_from_module(module_path, baseclass):
    result = {}
    for cls in iter_classes(module_path, baseclass):
        result[cls.name] = cls
    return result


def get_class_from_module_path(module_path, baseclass):
    module = import_module(module_path)
    for obj in vars(module).itervalues():
        if inspect.isclass(obj) and issubclass(obj, baseclass) and obj != baseclass:
            return obj


def import_module_object(object_path):
    module_path, object_name = object_path.rsplit('.', 1)
    module = import_module(module_path)
    return getattr(module, object_name)


def pairwise(iterable):
    a = iter(iterable)
    return izip(a, a)


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i+n]



def reconnect_database():
    from django.db import connection
    connection.connection = None


def close_database():
    from django.db import connection
    connection.close()


def convert_date(date_str, format="%Y-%m-%d"):
    return datetime.datetime.strptime(date_str, format).date()



class LazyMongoConnection(LazyObject):
    """
    self.client reference to MongoClient object
    """
    def __init__(self, host, db, username=None, password=None, port=27017):
        super(LazyMongoConnection, self).__init__()
        self.__dict__['_host'] = host
        self.__dict__['_port'] = port
        self.__dict__['_username'] = username
        self.__dict__['_password'] = password
        self.__dict__['_db'] = db

    def _setup(self):
        client = MongoClient(host=self.__dict__['_host'], port=self.__dict__['_port'])
        db = client[self.__dict__['_db']]
        if self.__dict__['_username'] and self.__dict__['_password']:
            db.authenticate(self.__dict__['_username'], self.__dict__['_password'])
        self._wrapped = db


class LazyRabbitmqChannel(LazyObject):
    def __init__(self, url_param):
        super(LazyRabbitmqChannel, self).__init__()
        self.__dict__['url_param'] = url_param

    def _setup(self):
        logger.info("connecting to rabbitmq" )
        parameters = pika.URLParameters(self.__dict__['url_param'])
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        self._wrapped = channel
