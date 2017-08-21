import json

from crawl_list_worker import CrawlListWorker

class SzOfficeListWorker(CrawlListWorker):

    queue = 'sz_office_list_page'

    name = 'sz_office_list'

    def get_list(self, soup):
        tab_list = soup.find('table', 'tab_list')
        trs = tab_list.find_all('tr')[1:-1]
        for tr in trs:
            href = tr.find('a').get('href')
            body = 'http://www.szlawyers.com' + href
            self.send_list_to_queue(queue='sz_office_list', body=json.dumps({'url':body}, encoding='utf-8'))
