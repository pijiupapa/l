import json

from bs4 import BeautifulSoup
from colla.worker import Worker
from colla.logger import logger
from crawl.utils.session import create_session
from colla.exceptions import ExitWithDone, ExitWithoutDone, ExitWithDoneNoAck


class CrawlWorker(Worker):

    queue = 'list'

    name = 'crawl_worker'

    def execute(self, task):
        self.task = task
        self.session = create_session(self)
        if self.task.url:
            logger.info(self.task.url)
            response = self.session.get(self.task.url)
            if response.status_code==200:
                pass
            else:
                raise ExitWithoutDone
            soup = BeautifulSoup(response.content)
            self.soup = soup
        else:
            self.soup = ''
        self.get_data()
        yield None

    def get_data(self):
        pass

    def send_data_to_db(self, db, data):
        db.update_one({'name':data['name']}, {'$set':data}, upsert=True)
