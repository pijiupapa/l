# -*- coding=utf-8 -*-

import os
import time
import redis
from colla.logger import logger
from adsl.signals import ppoe_before_adsl, ppoe_after_adsl
from .common import REGISTER_PIDS, REQUEST_PPOE_SIGNAL, RESPONSE_PPOE_SIGNAL, WAIT_PPOE, OK_PPOE, IS_PPOE, IP, READY, RESPONSE_PPOE_SIGNAL


class PpoeClient(object):

    def start(self):

        self.redis = redis.Redis()
        self.start_ip = self.get_ip()
        self.register_pid()


    def get_ip(self):
        return self.redis.get(IP)


    def get_pid(self):
        return os.getpid()


    def get_is_ppoe(self):
        return int(self.redis.get(REQUEST_PPOE_SIGNAL))


    def get_notify_ppoe_signal(self):
        return int(self.redis.get(RESPONSE_PPOE_SIGNAL))


    def send_ready_signal(self):
        logger.info("send ready signal")
        self.redis.hset(REGISTER_PIDS, self.get_pid(), READY)


    def reset_ready_signal(self):
        self.redis.hset(REGISTER_PIDS, self.get_pid(), WAIT_PPOE)


    def request_ppoe(self):
        logger.info("request adsl")
        self.redis.set(REQUEST_PPOE_SIGNAL, 1)


    def check_ppoe_signal(self):
        return int(self.redis.get(RESPONSE_PPOE_SIGNAL))


    def wait_ppoe_complete(self):
        while True:
            new_ip = self.get_ip()
            if new_ip != self.start_ip:
                # get new different ip
                self.start_ip = new_ip
                break
            time.sleep(1)


    def register_pid(self):
        self.redis.hset(REGISTER_PIDS, self.get_pid(), WAIT_PPOE)


    def unregister_pid(self):
        self.redis.hdel(REGISTER_PIDS, self.get_pid())


    def reconnect(self):
        logger.info("adsl reconnect")
        ppoe_before_adsl.send(self)
        if not self.get_is_ppoe():
            # if is adsling, then skip and wait complete
            self.request_ppoe()
        self.ready_for_ppoe()
        ppoe_after_adsl.send(self)


    def ready_for_ppoe(self):
        self.send_ready_signal()
        logger.info("wait ppoe complete")
        self.wait_ppoe_complete()
        self.reset_ready_signal()


    def stop(self):
        self.unregister_pid()



ppoe_client = PpoeClient()
