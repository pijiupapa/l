# -*- coding=utf-8 -*-
import os
import subprocess
import time
import redis
import requests
from colla.logger import logger
from adsl.utils import get_real_ip



class VpnClient(object):

    def __init__(self):
        self.redis = redis.StrictRedis()


    def start(self):
        logger.info("vpn ip: %s" %  self.now_pptp_ip)
        self.update_vpn_ip()


    def get_now_ip(self):
        return self.redis.get('vpn_ip')


    def reconnect(self):
        if self.is_pptp:
            logger.info(u"检测到正在拨号")
        if not self.is_pptp:
            logger.info(u"发送拨号信号")
            self.redis.set("pptp", 1)
        self.wait_pptp_complete(self.last_ip)
        logger.info("vpn ip change from %s: to %s" % (self.last_ip, self.now_pptp_ip))
        self.update_vpn_ip()


    @property
    def is_pptp(self):
        return int(self.redis.get("is_pptp"))


    @property
    def now_pptp_ip(self):
        return self.redis.get('vpn_ip')


    def wait_pptp_complete(self, last_ip):
        while True:
            time.sleep(1)
            if self.now_pptp_ip != last_ip:
                break


    @property
    def ip_change(self):
        return self.now_pptp_ip != self.last_ip


    def update_vpn_ip(self):
        self.last_ip = self.now_pptp_ip


    def check_vpn_change(self):
        if self.is_pptp:
            self.wait_pptp_complete(self.last_ip)
        if self.ip_change:
            self.update_vpn_ip()
            raise ExitWithoutDone()
            return True

        return False


vpn_client = VpnClient()
