# -*- coding=utf-8 -*-
import datetime
import time
import copy
import requests
import crawl.settings as settings
from colla.logger import logger
from colla.exceptions import ExitWithoutDone
from colla.influx import influx_logger



class ResponseError(Exception):
    pass


class BanError(Exception):
    pass



class BaseSession(requests.Session):

    timeout = 60
    max_retry = 3

    def __init__(self, worker, *args, **kwargs):
        self.worker = worker
        self.timeout = kwargs.get('timeout', None) or self.timeout
        self.max_retry = kwargs.get('max_retry', None) or self.max_retry
        super(BaseSession, self).__init__()
        self.headers['User-Agent'] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36"


    def request(self, *args, **kwargs):
        if 'timeout' not in kwargs:
            kwargs['timeout'] = self.timeout
        max_retry =  kwargs.pop('max_retry', None) or self.max_retry
        content_type = kwargs.pop("content_type", "text/html")

        read_timeout_times = 0
        connection_error_times = 0
        response_error_times = 0
        for i in range(max_retry):
            try:
                before_req_time = time.time()
                response = super(BaseSession, self).request(*args, **kwargs)
                response.content_type = content_type
                span_time = time.time() - before_req_time
                logger.debug("requst cost time: %s" % span_time)
                response.cost_time = span_time
                self.log_response(response)
                self.check_error_page(response)
                self.check_ban(response)
                return response

            except requests.exceptions.ConnectionError:
                connection_error_times += 1
                logger.debug("request session connection error")
                self.connection_error()

            except requests.exceptions.ReadTimeout:
                read_timeout_times += 1
                logger.debug("request session receive data timeout")

            except requests.exceptions.ChunkedEncodingError:
                logger.debug("request session chunked encoding error")

            except BanError:
                logger.debug("ip has been banned by server")
                self.on_ban(response)

            except ResponseError:
                response_error_times += 1
                logger.info("response error page")
                self.on_error(response)

        else:
            logger.debug("request session connect times greater than %s" % max_retry)
            self.error_times(read_timeout_times, connection_error_times, response_error_times, max_retry)
            raise ExitWithoutDone()



    def connection_error(self):
        pass


    def check_ban(self, reponse):
        pass


    def on_ban(self, response):
        pass


    def on_error(self, response):
        pass


    def error_times(self, read_timeout_times, connection_error_times, response_error_times, request_times):
        pass


    def check_error_page(self, response):
        if response.status_code >= 500 or response.status_code == 404:
            logger.info("reponse error status code : %s" % response.status_code)

            if self.is_text_html(response):
                # only log html
                content = self.unicode_content(response.content)
                logger.info(u"reponse error content: %s" % content)
            raise ResponseError()


    def is_text_html(self, response):
        content_type = response.headers.get("Content-Type", None) or response.content_type
        if ";" in content_type:
            content_type = content_type.split(';')[0]
        return content_type == "text/html"


    def unicode_content(self, content, encoding='utf-8', encodings=['utf-8', 'gbk']):
        if isinstance(content, unicode):
            return content

        if isinstance(content, str):
            encodings = copy.copy(encodings) # default kwargs can be change, so copy it
            # change encodings order
            encodings.remove(encoding)
            encodings.insert(0, encoding)

            for en in encodings:
                try:
                    return content.decode(en)
                except UnicodeDecodeError:
                    continue
            else:
                raise ValueError('unknown encoding when try %s' % encodings)


    def log_response(self, response):
        logger.debug("log response into influxdb")
        url_id = self.get_influx_url_id(response.request.url)
        cost = int(response.cost_time*1000)
        line = "request,host=%s,project=%s,url_id=%s,status=%s cost=%s" % (settings.host, settings.project, url_id, response.status_code, cost)
        influx_logger.log(line)


    def get_influx_url_id(self, url):
        return 'other'
