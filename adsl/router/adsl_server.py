# -*- coding=utf-8 -*-
import telnetlib
import time
import requests
import settings
import os
from colla.signals import adsl_signal, pptp_signal
from colla.logger import logger


def pptp():
    logger.info("ip: %s" % get_real_ip())
    os.system("bash pptp.sh")
    logger.info("after pptp, ip:%s " % get_real_ip())

def get_real_ip():
    resp = requests.get('http://httpbin.org/ip')
    return resp.json()['origin']



def adsl_model():
    adsl_signal.send(None)
    logger.info("ip: %s" % get_real_ip())
    HOST = "192.168.2.1"
    user = 'admin'
    password= 'minkelly'
    tn = telnetlib.Telnet(HOST)

    tn.read_until("login: ")
    tn.write(user + "\n")
    tn.read_until("Password: ")
    tn.write(password + "\n")

    kill_pppd = "killall pppd" + "\n"
    tn.write(kill_pppd)
    time.sleep(5) # 暂停5s，防止拨号过快，得到相同的ip
    pppoe = "pppd file /tmp/ppp/options.wan0" + "\n"
    tn.write(pppoe)
    tn.write("exit\n")

    time.sleep(10) # 暂停5s，等待拨号完成
    logger.info("after pptp, ip:%s " % get_real_ip())
