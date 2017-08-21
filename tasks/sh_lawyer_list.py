# -*- coding:utf-8 -*-

from colla.task import Task, Field

class ShLawyerListTask(Task):

    queue = 'sh_lawyer_list_page'

    url = Field()
