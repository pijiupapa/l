# -*- coding=utf-8 -*-
import time
import os
import subprocess
import redis
from ppoe.common import READY, REQUEST_PPOE_SIGNAL, RESPONSE_PPOE_SIGNAL, REGISTER_PIDS, IP, IS_PPOE, WAIT_PPOE
from utils import get_real_ip
from logger import logger


class PpoeServer(object):

    def __init__(self):
        self.redis = redis.Redis()
        self.using_ip = get_real_ip()
        self.redis.set(IP, self.using_ip)
        self.init_redis()


    def init_redis(self):
        self.redis.set(IS_PPOE, 0)
        self.redis.set(RESPONSE_PPOE_SIGNAL, 0)
        self.redis.set(IP, self.using_ip)
        self.redis.setnx(REQUEST_PPOE_SIGNAL, 0)

    def is_process_alive(self, pid):
        try:
            os.kill(int(pid), 0)
        except OSError:
            return False
        else:
            return True


    def test_all_pids_alive(self):
        pids = self.redis.hgetall(REGISTER_PIDS)
        for pid, state in pids.items():
            alive = self.is_process_alive(pid)
            if not alive:
                self.redis.hdel(REGISTER_PIDS, pid)


    def test_all_pid_ready(self):
        states = self.redis.hgetall(REGISTER_PIDS).values()
        return all(map(lambda x: x == READY,states))


    def notify_ppoe_signal(self):
        logger.info("notify ppoe signal")
        self.redis.set(RESPONSE_PPOE_SIGNAL, 1)
        # wait for all pid ok for ppoe
        wait_start_time = time.time()

        # wait for at most 60s
        wait_timeout = 60
        while True:
            self.test_all_pids_alive()
            if time.time() - wait_start_time > wait_timeout:
                break
            if self.test_all_pid_ready():
                logger.info("all pid are ready for ppoe")
                break
            time.sleep(1)




    def reset_pids_state(self):
        pids = self.redis.hgetall(REGISTER_PIDS)
        for pid, state in pids.items():
            self.redis.hset(REGISTER_PIDS, pid, WAIT_PPOE)


    def reset_request_signal(self):
        self.redis.set(REQUEST_PPOE_SIGNAL, 0)


    def reset_notify_ppoe_signal(self):
        self.redis.set(RESPONSE_PPOE_SIGNAL, 0)


    def set_ban_ip(self, ip):
        self.redis.set(ip, 1, ex=60*1)


    def is_ban(self, ip):
        ret = self.redis.get(ip)
        return ret is None


    def reconnet(self):

        while True:
            self.adsl_stop()
            time.sleep(5)
            self.adsl_start()
            new_ip =  get_real_ip()
            logger.info("new ip after adsl: %s" % new_ip)
            if new_ip and new_ip != self.using_ip and self.is_ban(new_ip):
                # new_ip may be none, indicate adsl-start does not success
                self.using_ip = new_ip
                self.redis.set(IP, self.using_ip)
                break


    def adsl_start(self):
        logger.info("adsl start")
        shell = "adsl-start"
        subprocess.call(shell, shell=True)


    def adsl_stop(self):
        logger.info("adsl stop")
        shell = "adsl-stop"
        subprocess.call(shell, shell=True)


    def is_adsl_alive(self):
        shell = "ifconfig |grep ppp0|awk '{print $1}'"
        return 'ppp0' in os.popen(shell).read()
        # inter = subprocess.Popen(shell, shell=True, stdout=subprocess.PIPE)
        # return 'ppp0' == inter.stdout.read().strip()


    def run(self):
        self.adsl_start()
        while True:
            ppoe_signal = int(self.redis.get(REQUEST_PPOE_SIGNAL))
            if ppoe_signal:
                logger.info("check request ppoe signal: %s" % ppoe_signal)
                self.set_ban_ip(self.using_ip)
                self.redis.set(IS_PPOE, 1)
                self.notify_ppoe_signal()
                self.reconnet()
                self.reset_pids_state()
                self.reset_request_signal()
                self.reset_notify_ppoe_signal()
                self.redis.set(IS_PPOE, 0)
            self.test_all_pids_alive()

            if not self.is_adsl_alive():
                self.reconnet()
            time.sleep(1)


if __name__ == "__main__":
    server = PpoeServer()
    server.run()
