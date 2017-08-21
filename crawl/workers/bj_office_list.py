import json

from crawl_list_worker import CrawlListWorker

class BjOfficeListWorker(CrawlListWorker):

    queue = 'bj_office_list_page'

    name = 'bj_office_list'

    def get_list(self, soup):
        shiwusuo = soup.find('div', 'shiwusuo')
        tables = shiwusuo.find_all('table')[2:]
        for table in tables:
            href = table.find('a').get('href')
            body = 'http://www.beijinglawyers.org.cn' + href
            self.send_list_to_queue(queue='bj_office_list', body=json.dumps({'url':body}, encoding='utf-8'))
