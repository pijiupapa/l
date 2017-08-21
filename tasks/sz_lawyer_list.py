# -*- coding:utf-8 -*-

from colla.task import Task, Field

class SzLawyerListTask(Task):

    queue = 'sz_lawyer_list_page'

    url = Field()
