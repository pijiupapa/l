# -*- encoding:utf-8 -*-

from colla.logger import logger
from colla.utils import LazyMongoConnection, LazyRabbitmqChannel
import crawl.settings as settings


mongo_db = LazyMongoConnection(host=settings.mongo_host, port=settings.mongo_port, username=settings.mongo_user,password=settings.mongo_password, db=settings.mongo_name)
channel = LazyRabbitmqChannel(url_param='')
