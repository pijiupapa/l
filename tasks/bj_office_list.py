# -*- coding:utf-8 -*-

from colla.task import Task, Field

class BjOfficeListTask(Task):

    queue = 'bj_office_list_page'

    url = Field()
