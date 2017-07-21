# -*- coding: utf-8 -*-

import re
import scrapy #导入scrapy包
from bs4 import BeautifulSoup
from scrapy.http import Request ##一个单独的request的模块，需要跟进URL的时候，需要用它
from dingdian_spider.items import DingdianSpiderItem,DcontentItem ##这是我定义的需要保存的字段，（导入dingdian项目中，items文件中的DingdianItem类）

import logging

class DingdianSpider(scrapy.Spider):
    name = 'dingdian'
    allowed_domains = ['www.x23us.com']
    bash_url = 'http://www.x23us.com/class/'
    bashurl = '.html'

    def start_requests(self):
        for i in range(1, 2):
            url = self.bash_url + str(i) + '_1' + self.bashurl
            yield Request(url, self.parse)

        # yield Request('http://www.23wx.com/quanben/1', self.parse)

    def parse(self, response):
        logging.info('Parse function called on %s'% response.url)

        max_num = BeautifulSoup(response.text, 'lxml').find('div', class_='pagelink').find_all('a')[-1].get_text()
        bashurl = str(response.url)[:-7]
        for num in range(1, int(max_num) + 1):
            url = bashurl + '_' + str(num) + self.bashurl
            # print 'We Get Next Url:%s' % url
            yield Request(url, callback=self.get_name)
            """yieid Request，请求新的URL，后面跟的是回调函数，你需要哪一个函数来处理这个返回值，就调用那一个函数，
                返回值会以参数的形式传递给你所调用的函数。
            """

    def get_name(self,response):
        # logging.info('Get_name function called on %s'%response.url)
        tds = BeautifulSoup(response.text, 'lxml').find_all('tr', bgcolor='#FFFFFF')
        for td in tds:
            """这儿用循环是因为find_all取出的来标签是以列表形式存在的；不然没法继续使用find"""
            novelname = td.find_all('a')[1].get_text().encode('utf-8')
            # print "novelname:%s"%novelname
            novelurl = td.find('a')['href'].encode('utf-8')
            # print "novelurl:%s" % novelurl
            # logging.info('function get_name novelname:%s,novelurl:%s' %(novelname,novelurl))
            yield Request(novelurl, callback=self.get_chapterurl, meta={'name': novelname,
                                                                       'url': novelurl})


    def get_chapterurl(self,response):
        logging.info('Get_chapterurl function called on %s'%response.url)
        item = DingdianSpiderItem()
        item['name'] = str(response.meta['name'])
        item['novelurl'] = response.meta['url']
        category = BeautifulSoup(response.text, 'lxml').find('table').find('a').get_text().encode('utf-8')
        author = BeautifulSoup(response.text, 'lxml').find('table').find_all('td')[1].get_text().encode('utf-8')

        bash_url = BeautifulSoup(response.text, 'lxml').find('p', class_='btnlinks').find('a', class_='read')['href'].encode('utf-8')
        name_id = str(bash_url)[-6:-1].replace('/', '')
        item['category'] = category
        item['author'] = author
        item['name_id'] = name_id
        # logging.info('name:%s,category:%s,author:%s,name_id:%s' % (item['name'],category, author, item['name_id']))
        # return item

        yield item
        yield Request(url=bash_url, callback=self.get_chapter, meta={'name_id': name_id})



    def get_chapter(self,response):
        urls = re.findall(r'<td class="L"><a href="(.*?)">(.*?)</a></td>', response.text)
        num = 0
        for url in urls:
            num = num + 1
            chapterurl = response.url + url[0]
            chaptername = url[1]
            # rets = Sql.sclect_chapter(chapterurl)
            # if rets[0] == 1:
            #     print('章节已经存在了')
            #     return False
            # else:
            logging.info('Get_chapter function name_id: %s,chaptername: %s,chapterurl: %s' % (response.meta['name_id'],chaptername,chapterurl))
            yield Request(chapterurl, callback=self.get_chaptercontent, meta={'num': num,
                                                                                  'name_id': response.meta['name_id'],
                                                                                  'chaptername': chaptername,
                                                                                  'chapterurl': chapterurl
                                                                                  })



    def get_chaptercontent(self,response):

        item = DcontentItem()
        item['num'] = response.meta['num']
        item['id_name'] = response.meta['name_id']
        item['chaptername'] = response.meta['chaptername']
        item['chapterurl'] = response.meta['chapterurl']
        content = BeautifulSoup(response.text, 'lxml').find('dd', id='contents').get_text()
        item['chaptercontent'] = content
        logging.info('chaptername:%s,id_name:%s,num:%s,chapterurl:%s,chaptercontent:%s' % (item['chaptername'], item['id_name'], item['num'], item['chapterurl'],item['chaptercontent']))
        yield item