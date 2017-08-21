import json

from crawl_list_worker import CrawlListWorker

class ShLawyerListWorker(CrawlListWorker):

    queue = 'sh_lawyer_list_page'

    name = 'sh_lawyer_list'

    def get_list(self, soup):
        list_base = soup.find('div', 'list-base')
        list_items = list_base.find_all('a')
        for list_item in list_items:
            url = 'http://credit.lawyerpass.com/' + list_item['href']
            self.send_list_to_queue(queue='sh_lawyer_list', body=json.dumps({'url':url}, encoding='utf-8'))
