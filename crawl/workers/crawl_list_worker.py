import json

from bs4 import BeautifulSoup
from colla.worker import Worker
from colla.logger import logger
from crawl.utils.session import create_session
from colla.exceptions import ExitWithDone, ExitWithoutDone, ExitWithDoneNoAck


class CrawlListWorker(Worker):

    queue = 'page'

    name = 'crawl_list_worker'

    def execute(self, task):
        session = create_session(self)
        logger.info(task.url)
        self.task = task
        response = session.get(task.url)
        if response.status_code==200:
            pass
        else:
            raise ExitWithoutDone
        soup = BeautifulSoup(response.content)
        self.get_list(soup)
        yield None

    def get_list(self, soup):
        self.send_list_to_queue(queue='', body='')

    def send_list_to_queue(self, queue, body):
        logger.info('%s: %s' % (queue,body))
        self.task.back_to_queue(queue=queue, body=body)
