# -*- coding:utf-8 -*-
import requests

from bs4 import BeautifulSoup
from task_maker import TaskMaker

class SzOfficeListTaskMaker(TaskMaker):

    def make_task(self):
        url = 'http://www.szlawyers.com/searchLawFirm?name=&x=36&y=16&page=1'
        response = requests.get(url)
        soup = BeautifulSoup(response.content)
        pages = int(soup.find('div', 'page').find_all('a')[-2].text)
        for page in range(1,pages+1):
            url = 'http://www.szlawyers.com/searchLawFirm?name=&x=36&y=16&page=%s' % page
            self.send_task('sz_office_list_page', {'url':url})

task = SzOfficeListTaskMaker()
