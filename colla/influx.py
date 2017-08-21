# -*- coding=utf-8 -*-
import requests
import crawl.settings as settings

class InfluxLogger(object):

    def start(self, settings):
        self.influxdb_auth = requests.auth.HTTPBasicAuth(username=settings.influxdb_username, password=settings.influxdb_password)
        self.influxdb_url = settings.influxdb_url


    def log(self, line):
        try:
            requests.post(self.influxdb_url, data=line, auth=self.influxdb_auth, timeout=10)
        except requests.exceptions.Timeout:
            logger.info("request influxdb timeout")


influx_logger = InfluxLogger()
influx_logger.start(settings)
