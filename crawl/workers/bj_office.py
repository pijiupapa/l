# -*- coding:utf-8 -*-
import json

from crawl_worker import CrawlWorker
from colla.logger import logger
from crawl.connection import mongo_db

class BjOfficeWorker(CrawlWorker):

    queue = 'bj_office_list'

    name = 'bj_office'

    map_info = {
                u'名称':'name', u'所属区县':'office', u'组织形式':'type',
                u'主任':'principal', u'统一社会信用代码':'certificate_number',
                u'地址':'address', u'邮编':'Zip_code', u'注册资金':'fund',
                u'办公面积':'space', u'场所性质':'nature', u'办公传真':'fax',
                u'办公电话':'telephone', u'网址':'website', u'执业状态':'status',
                u'业务专长':'expert', u'发证日期':'licence_date'
                }

    def get_data(self):
        shiwusuo = self.soup.find('div', 'shiwusuo')
        table = shiwusuo.find('table').find('table')
        tds = table.find_all('td')
        data = {}
        for td in tds:
            key, value = td.text.strip().split(u'：', 1)
            data[self.map_info[key]] = value.strip()
        mongo_db.bj_office.update_one({'name':data['name'],'certificate_number':data['certificate_number']}, {'$set':data}, upsert=True)
