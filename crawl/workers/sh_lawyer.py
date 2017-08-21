# -*- coding:utf-8 -*-
import json
import base64

from bs4 import BeautifulSoup
from crawl_worker import CrawlWorker
from colla.logger import logger
from crawl.connection import mongo_db

class ShLawyerWorker(CrawlWorker):

    queue = 'sh_lawyer_list'

    name = 'sh_lawyer'

    map_info = {
                u'执业证号':'licence_code', u'性别':'gender', u'年龄':'age',
                u'民族':'nation', u'学历':'education', u'执业类型':'pro_type',
                u'政治面貌':'political', u'资格证号':'qualification_code',
                u'首次执业时间':'licence_date', u'资格证取得时间':'qualification_date',
                u'所内身份':'position', u'主管司法局':'area', u'email':'email'
                }

    def get_data(self):
        user_info = self.soup.find('dl', 'user-info')
        user_info_extra = self.soup.find('div', id='detail01')
        data={}
        data['name'] = user_info.find('dd', 'name').text.strip()
        data['office'] = user_info.find('a').text.strip()
        data['office_url'] = user_info.find('a').get('href')
        spans = user_info.find('dd', 'tag').find_all('span')
        l = [span.text.strip() for span in spans]
        if ','.join(l)==',,':
            data['expert'] = ''
        else:
            data['expert'] = ','.join(l)
        img_url = user_info.find('img').get('src')
        data['img'] = base64.b64encode(self.session.get(img_url).content)
        lis = user_info_extra.find_all('li')
        for li in lis:
            key,value =  li.text.split(u'：', 1)
            data[self.map_info[key]] = value
        logger.info('Licence:%s' % data['licence_code'])
        mongo_db.sh_lawyer.update_one({'licence_code':data['licence_code']}, {'$set':data}, upsert=True)
