# -*- coding:utf-8 -*-

from colla.task import Task, Field

class SzOfficeListTask(Task):

    queue = 'sz_office_list_page'

    url = Field()
