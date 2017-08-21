# -*- coding:utf-8 -*-

from colla.task import Task, Field

class SzOfficeTask(Task):

    queue = 'sz_office_list'

    url = Field()
