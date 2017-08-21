# -*- coding:utf-8 -*-
import json

from crawl_worker import CrawlWorker
from colla.logger import logger
from crawl.connection import mongo_db

class SzOfficeWorker(CrawlWorker):

    queue = 'sz_office_list'

    name = 'sz_office'

    map_info = {u'事务所名称':'name', u'英文名称':'E_name', u'主管机关':'office',
                u'执业证号':'certificate_number', u'设立时间':'es_date',
                u'组织形式':'type', u'负责人':'principal', u'派驻律师':'stationed_lawer',
                u'律师人数':'count', u'执业律师':'lawer', u'办公地址':'address',
                u'邮政编码':'Zip_code', u'总机电话':'switchboard', u'传真号码':'fax',
                u'电子邮箱':'email', u'单位网址':'website', u'事务所简介':'introduction',
                u'合伙人':'partner'
                }

    def get_data(self):
        div_list = self.soup.find('div', 'list')
        trs = div_list.find_all('tr')
        data = {}
        for tr in trs:
            tds = tr.find_all('td')
            spans = tds[1].find_all('span')
            a_list = tds[1].find_all('a')
            if spans:
                content = {}
                for span in spans:
                    a = span.find('a')
                    if a:
                        content[a.text.replace(u'　','').encode('utf-8')] = a['href']
                    else:
                        content[span.text.strip().encode('utf-8')] = ''
            elif a_list:
                content = {}
                for a in a_list:
                    try:
                        content[a.text.replace(u'　','').encode('utf-8')] = a['href']
                    except KeyError,e:
                        content[a.text.replace(u'　','').encode('utf-8')] = ''
            else:
                content = tds[1].text.encode('utf-8')
            try:
                data[self.map_info[tds[0].text]] = content
            except KeyError,e:
                logger.info('map has no key:%s' % tds[0].text)
                raise
                data[tds[0].text.encode('utf-8')] = content
        data['website'] = json.dumps(data['website'])
        self.send_data_to_db(mongo_db.sz_office, data)
