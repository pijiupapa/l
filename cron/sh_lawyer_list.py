# -*- coding:utf-8 -*-
import requests

from bs4 import BeautifulSoup
from task_maker import TaskMaker

class ShLawyerListTaskMaker(TaskMaker):

    def make_task(self):
        for page in range(1,5489):
            url = 'http://credit.lawyerpass.com/lawyer-list.jsp?page=%s' % page
            self.send_task('sh_lawyer_list_page', {'url':url})

task = ShLawyerListTaskMaker()
