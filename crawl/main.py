# -*- coding=utf-8 -*-
import argparse
import sys
import logging
from colla.engine import engine
from colla.logger import logger, LOGGING
from colla.signals import engine_start, engine_setup, engine_stop
from adsl.signals import ppoe_before_adsl, ppoe_after_adsl
from crawl.connection import mongo_db
import crawl.settings as settings


def setup_vpn(enginer):
    if not settings.USING_VPN:
        return

    from adsl.pptp.client import vpn_client
    logger.debug(u"配置vpn")
    vpn_client.start()


def setup_adsl(enginer):
    if not settings.USE_ADSL:
        return

    from adsl.ppoe.client import ppoe_client
    logger.debug(u"配置adsl")
    ppoe_client.start()


def close_database(sender):
    logger.info("close database")
    mongo_db.client.close()


def close_rabbitmq(sender):
    logger.info("close rabbbitmq")
    engine.scheduler.close()


def open_rabbitmq(sender):
    logger.info("rabbitmq connect")
    engine.scheduler.reconnect()



def main():
    # engine_setup.connect(setup_mongo)
    engine_setup.connect(setup_vpn)
    engine_setup.connect(setup_adsl)
    engine_stop.connect(close_database)
    engine_stop.connect(close_rabbitmq)

    ppoe_before_adsl.connect(close_database)
    ppoe_before_adsl.connect(close_rabbitmq)
    ppoe_after_adsl.connect(open_rabbitmq)

    parser = argparse.ArgumentParser()
    parser.add_argument("command")
    parser.add_argument("worker_name")
    options = parser.parse_args()

    LOGGING['handlers']['info_file']['filename'] = "log/%s.log" % options.worker_name
    logging.config.dictConfig(LOGGING)

    engine.start(settings)
    engine.create_worker(options.worker_name)
    engine.run()
