# -*- coding:utf-8 -*-
import requests

from bs4 import BeautifulSoup
from task_maker import TaskMaker

class BjOfficeListTaskMaker(TaskMaker):

    def make_task(self):
        for type_id in range(1,30):
            url = 'http://www.beijinglawyers.org.cn/cgi/RnewsActionsearchLawfirm2.do?text5=&text6=&typeid=%s' % type_id
            response = requests.get(url)
            soup = BeautifulSoup(response.content)
            xy = soup.find('div', 'xy')
            pages = int(xy.text.split('/')[-1].split(u'页')[0])
            for page in range(1,pages+1):
                url = 'http://www.beijinglawyers.org.cn/cgi/RnewsActionsearchLawfirm2.do?text5=&text6=&typeid=%s&cur=%s' % (type_id, page)
                self.send_task('bj_office_list_page', {'url':url})

task = BjOfficeListTaskMaker()
