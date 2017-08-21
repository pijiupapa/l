# -*- coding=utf-8 -*-
import os
import time
import logger
import random
import subprocess
import redis
import requests
from utils import get_real_ip
from logger import logger
from pptp.base import VpnConnectionBase, VpnManagerBase


class LinuxVpnConnection(VpnConnectionBase):

    def __init__(self, username, password, vpn_name, vpn_server):
        self.username = username
        self.password = password
        self.vpn_name = vpn_name
        self.vpn_server = vpn_server

    @property
    def status(self):
        vpn_runing = os.popen('ifconfig').read().find('ppp0')
        if vpn_runing == -1:
            return 'disconnect'
        return 'connected'


    def start(self):
        while True:
            if self.status == 'connected':
                logger.debug(u"vpn已经连接")
                break
            shell = 'pptpsetup --create %s --server %s --username %s --password %s --encrypt --start' % (self.vpn_name, self.vpn_server, self.username, self.password)
            logger.debug("shell: %s" % shell)
            os.system(shell)

            while True:
                ret = self.wait_pptp_status('connected')
                if ret:
                    return
                if self.status == 'disconnect':
                    logger.debug(u"vpn连接失败")
                    time.sleep(2)
                    break


    def wait_pptp_status(self, status, timeout=5):
        start_time = time.time()
        while True:
            if self.status == status:
                return True
            if time.time() - start_time > timeout:
                return False
            time.sleep(1)


    def close(self):
        if self.status == 'disconnect':
            logger.info(u"vpn的状态为已关闭, 不需要重新关闭")
            return
        logger.info(u"关闭vpn")
        shell = "pkill pppd"
        subprocess.call(shell, shell=True)
        logger.debug("shell: %s" % shell)
        self.wait_pptp_status('disconnect')


class LinuxVpnManager(VpnManagerBase):

    def __init__(self, username, password, hosts):
        self.redis = redis.Redis()
        self.username = username
        self.password = password
        self.clients = []
        self.using_vpn = None
        self.using_ip = None
        self.vpn_index = 0
        self.name_servers = hosts

    def start(self):
        for name , server in self.name_servers.items():
            client = LinuxVpnConnection(self.username, self.password, name, server)
            self.clients.append(client)

        if self.using_vpn is None:
            self.using_vpn = random.choice(self.clients)
        self.set_is_pptp(1)
        self.using_vpn.start()
        self.add_default_route()
        self.using_ip = get_real_ip()
        self.set_vpn_ip(self.using_ip)
        self.set_is_pptp(0)


    def add_default_route(self):
        shell = "route add default dev ppp0"
        os.system(shell)


    def set_is_pptp(self, value):
        self.redis.set("is_pptp", value)

    def get_ip_pptp(self):
        return int(self.redis.get("is_pptp"))


    def set_vpn_ip(self, ip):
        self.redis.set("vpn_ip", ip)

    @property
    def is_died(self):
        return self.using_vpn.status == 'disconnect'


    def run(self):
        self.start()
        while True:
            logger.debug("check pptp signal")
            is_going_pptp = int(self.redis.get("pptp"))
            is_pptp = self.get_ip_pptp()
            if is_going_pptp or self.is_died:
                    logger.info("old vpn ip: %s" % self.using_ip)
                    self.set_is_pptp(1)
                    while True:
                        self.reconnect()
                        new_using_ip = get_real_ip()
                        print new_using_ip, self.using_ip
                        if new_using_ip != self.using_ip:
                            break
                        logger.info(u"adsl get same ip, we need adsl again")
                    logger.info("new vpn ip: %s" % new_using_ip)
                    self.set_vpn_ip(new_using_ip)
                    self.using_ip = new_using_ip
                    self.set_is_pptp(0)
                    self.redis.set("pptp", 0)

            time.sleep(1)

    def random_choice(self):
        self.vpn_index += 1
        self.vpn_index = self.vpn_index % len(self.clients)
        return self.clients[self.vpn_index]


    def reconnect(self):

        self.using_vpn.close()
        self.using_vpn = self.random_choice()
        logger.info("use vpn %s" % self.using_vpn.vpn_name)
        time.sleep(5)
        self.using_vpn.start()
        self.add_default_route()



if __name__ == "__main__":


    username = '90250'
    password = '12345'

    hosts = {'crawl_sx': 'zjsxzjsx.6655.la',
            'crawl_changzhou': 'jscczz.6655.la',
            'crawl_bingzhou': 'jscczz.6655.la',
            # 'crawl_jx': '',
            # 'crawl_lyg': '',
    }

    server = LinuxVpnManager(username, password, hosts)
    server.run()
