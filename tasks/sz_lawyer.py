# -*- coding:utf-8 -*-

from colla.task import Task, Field

class SzLawyerTask(Task):

    queue = 'sz_lawyer_list'

    url = Field()
    name = Field()
    licence = Field()
    office = Field()
