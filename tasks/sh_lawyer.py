# -*- coding:utf-8 -*-

from colla.task import Task, Field

class ShLawyerTask(Task):

    queue = 'sh_lawyer_list'

    url = Field()
