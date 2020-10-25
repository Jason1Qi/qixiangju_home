import scrapy
import json
import logging
import ipdb
import re

HOST = 'http://39.97.163.26/'
SEARCH_LIST_URL = HOST + 'nm-framework-web-baike/searchList.do'
RELATED_URL = HOST + 'nm-framework-web-baike/relatedTerms.do'
SEARCH_CONTENT_URL = HOST + 'nm-framework-web-baike/searchContent.do'

SEARCH_LIST_TEMPLATE = {
    'page': '1', #页码
    'word': '',
    'type': '',
    'year': '',
    'sidtype': 0, #分类id
    'users': '',
    'twoWord': ''
}
SEARCH_CONTENT_TEMPLATE = {
    'id': '0', #实体id
    'version': '1',
    'param': ''
}
RELATED_TEMPLATE = {
    'word': ''
}
ENTITIES_FILE = './statistics/entities/{}，{}.json'
RELATIONS_FILE = './statistics/relations/{}，{}.json'
CLASS_FILE = './statistics/classification.json'

class Home(scrapy.Spider):
    name = 'home'

    def get_class_list(self):
        with open(CLASS_FILE, mode='r', encoding='UTF-8') as f:
            classes = json.load(f)
            result = [item['sid'] for item in classes]
            logging.info('classification list read successfully')
            return set(result)

    def start_requests(self):
        class_list = self.get_class_list()
        for i in class_list:
            req_data = SEARCH_LIST_TEMPLATE.copy()
            req_data['sidtype'] = i
            logging.info('start requesting sid: {}, page: {}'.format(i, 1))
            yield scrapy.FormRequest(
                url=SEARCH_LIST_URL,
                callback=self.parse_search_list,
                meta={
                    'sidtype': i,
                    'page': '1'
                },
                method='POST',
                formdata=req_data
            )
        
    def parse_search_list(self, response):
        sidtype = response.meta['sidtype']
        page = response.meta['page']
        content = json.loads(response.text)[0]
        total_pages = content['searchPage']
        words = content['word']
        if page == '1':
            for index in range(2, total_pages + 1):
                req_data = SEARCH_LIST_TEMPLATE.copy()
                req_data['sidtype'] = sidtype
                req_data['page'] = str(index)
                logging.info('start requesting sid: {}, page: {}'.format(sidtype, index))
                yield scrapy.FormRequest(
                    url=SEARCH_LIST_URL,
                    callback=self.parse_search_list,
                    meta={
                        'sidtype': sidtype,
                        'page': str(index)
                    },
                    method='POST',
                    formdata=req_data
                )
        for word in words:
            wid = word['id'][0]
            name = word['auto_stringITSV_title']
            req_data = SEARCH_CONTENT_TEMPLATE.copy()
            req_data['id'] = str(wid)
            logging.info('start requesting word: {}, id: {}'.format(name, wid))
            yield scrapy.FormRequest(
                url=SEARCH_CONTENT_URL,
                callback=self.parse_search_content,
                meta={
                    'wid': wid,
                    'name': name
                },
                method='POST',
                formdata=req_data
            )

    def parse_search_content(self, response):
        wid = response.meta['wid']
        name = response.meta['name']
        content = json.loads(response.text)[0]
        file_name = ENTITIES_FILE.format(wid, name)
        with open(file_name, mode='w', encoding='UTF-8') as f:
            json.dump(content, f)
            logging.info('word {}, id {} saved'.format(name, wid))
        req_data = RELATED_TEMPLATE.copy()
        req_data['word'] = name
        logging.info('start requesting relation of word {}, id {}'.format(name, wid))
        yield scrapy.FormRequest(
            url=RELATED_URL,
            callback=self.parse_related,
            meta={
                'wid': wid,
                'name': name
            },
            method='POST',
            formdata=req_data
        )
    
    def parse_related(self, response):
        wid = response.meta['wid']
        name = response.meta['name']
        content = json.loads(response.text)
        file_name = RELATIONS_FILE.format(wid, name)
        with open(file_name, mode='w', encoding='UTF-8') as f:
            json.dump(content, f)
            logging.info('relations of word {}, id {} saved'.format(name, wid))

# .*10-24.*relations.*word.*saved