# -*- coding=utf-8 -*-
import time
import datetime
import urlparse
import crawl.settings as settings
from colla.logger import logger
from colla.exceptions import ExitWithoutDone, ExitWithDone, ExitWithDoneNoAck
from colla.session import BaseSession, ResponseError
from adsl.ppoe.client import ppoe_client


class LawSession(BaseSession):
    timeout = 30

    def on_ban(self, response):
        time.sleep(5)

    def error_times(self, read_timeout_times, connection_error_times, request_times):
        time.sleep(5)

    def get_influx_url_id(self, url):
        path_ids = {
            'searchLawFirm': 'office_list',
            'lawfirm': 'office',
        }
        path =  urlparse.urlparse(url).path.split('/')[1]
        return path_ids.get(path, 'other')


class SessionWithVpn(LawSession):

    def on_ban(self, response):
        from adsl.pptp.client import vpn_client
        vpn_client.reconnect()
        raise ExitWithoutDone()

    def error_times(self, read_timeout_times, connection_error_times, request_times):
        from adsl.pptp.client import vpn_client
        vpn_client.reconnect()
        raise ExitWithoutDone()

class SessionWithAdsl(LawSession):

    def on_ban(self, response):
        logger.info("ip has been banned")
        self.adsl_reconnect()
        raise ExitWithDoneNoAck()


    def request(self, *args, **kwargs):
        self.check_notify_ppoe_signal()
        return super(SessionWithAdsl, self).request(*args, **kwargs)


    def check_notify_ppoe_signal(self):
        is_will_ppoe = ppoe_client.get_notify_ppoe_signal()
        if is_will_ppoe:
            logger.info("check ppoe will reconnect")
            self.adsl_reconnect()
            raise ExitWithDoneNoAck()


    def error_times(self, read_timeout_times, connection_error_times,response_error_times, request_times):
        self.worker.adsl()
        raise ExitWithDoneNoAck()



def create_session(worker, *args, **kwargs):
    if settings.USE_ADSL:
        return SessionWithAdsl(worker, *args, **kwargs)
    elif settings.USING_VPN:
        return SessionWithVpn(worker, *args, **kwargs)
    else:
        return LawSession(worker, *args, **kwargs)
