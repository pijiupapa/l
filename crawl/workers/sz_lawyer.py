# -*- coding:utf-8 -*-
import json
import base64

from bs4 import BeautifulSoup
from crawl_worker import CrawlWorker
from colla.logger import logger
from crawl.connection import mongo_db

class SzLawyerWorker(CrawlWorker):

    queue = 'sz_lawyer_list'

    name = 'sz_lawyer'

    def get_data(self):
        data = {}
        if isinstance(self.soup, BeautifulSoup):
            lawyer_info = self.soup.find('table', 'lawyer_info')
            trs = lawyer_info.find_all('tr')
            data['name'] = lawyer_info.find('span', id='lawlist_LawerName').text
            img_url = lawyer_info.find('img', id='lawlist_lsxp').get('src')
            if img_url=='/static/images/cn/none.jpg':
                data['img'] = ''
            else:
                data['img'] = base64.b64encode(self.session.get(img_url).content)
            data['E_name'] = lawyer_info.find('span', id='lawlist_cym').text
            data['gender'] = lawyer_info.find('span', id='lawlist_LawerSex').text
            data['office'] = lawyer_info.find('span', id='lawlist_Enterprise').text
            data['pro_type'] = lawyer_info.find('span', id='lawlist_Class').text
            data['qualification_code'] = lawyer_info.find('span', id='lawlist_LawerqualNo').text
            data['qualification_date'] = lawyer_info.find('span', id='lawlist_dtLawerqualNo').text
            data['licence_code'] = self.task.licence
            data['licence_date'] = lawyer_info.find('span', id='lawlist_qdzyzsj').text
            data['work_date'] = lawyer_info.find('span', id='lawlist_zszkszysj').text
            data['political'] = lawyer_info.find('span', id='lawlist_zzmm').text
            data['language'] = lawyer_info.find('span', id='lawlist_gzyy').text
            spans = trs[14].find_all('span')
            l = [span.text.strip() for span in spans]
            if ','.join(l)==',,':
                data['expert'] = ''
            else:
                data['expert'] = ','.join(l)
        else:
            data['name'] = self.task.name
            data['licence_code'] = self.task.licence
            data['office'] = self.task.office
        office_id = mongo_db.sz_office.find_one({'name':data['office']})
        if office_id:
            data['office_id'] = str(office_id['_id'])
        else:
            data['office_id'] = ''
        logger.info('Licence:%s' % data['licence_code'])
        mongo_db.sz_lawyer.update_one({'licence_code':data['licence_code']}, {'$set':data}, upsert=True)
