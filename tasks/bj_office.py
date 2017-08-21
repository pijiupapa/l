# -*- coding:utf-8 -*-

from colla.task import Task, Field

class BjLawyerTask(Task):

    queue = 'bj_office_list'

    url = Field()
