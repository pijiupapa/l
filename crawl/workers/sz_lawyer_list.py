import json

from crawl_list_worker import CrawlListWorker

class SzLawyerListWorker(CrawlListWorker):

    queue = 'sz_lawyer_list_page'

    name = 'sz_lawyer_list'

    def get_list(self, soup):
        tab_list = soup.find('table', 'tab_list')
        trs = tab_list.find_all('tr')[1:-1]
        for tr in trs:
            tds = tr.find_all('td')
            data = {}
            if tds[0].find('a'):
                link = tds[0].find('a').get('href')
                data['url'] = 'http://www.szlawyers.com' + link
            else:
                data['url'] = ''
            data['name'] = tds[0].text.strip()
            data['office'] = tds[3].text.strip()
            data['licence'] = tds[-1].text.strip()
            self.send_list_to_queue(queue='sz_lawyer_list', body=json.dumps(data, encoding='utf-8'))
