# -*- coding: utf-8 -*-
import re
import scrapy #导入scrapy包
from bs4 import BeautifulSoup
from scrapy.http import Request ##一个单独的request的模块，需要跟进URL的时候，需要用它
from dingdian_spider.items import DingdianSpiderItem ##这是我定义的需要保存的字段，（导入dingdian项目中，items文件中的DingdianItem类）


class DingdianSpider(scrapy.Spider):
    name = 'dingdian'
    allowed_domains = ['www.x23us.com']
    bash_url = 'http://www.x23us.com/class/'
    bashurl = '.html'

    def start_requests(self):
        for i in range(1, 11):
            url = self.bash_url + str(i) + '_1' + self.bashurl
            yield Request(url, self.parse)

        # yield Request('http://www.23wx.com/quanben/1', self.parse)

    def parse(self, response):
        print 'We Get: %s' % response.url

        max_num = BeautifulSoup(response.text, 'lxml').find('div', class_='pagelink').find_all('a')[-1].get_text()
        bashurl = str(response.url)[:-7]
        for num in range(1, int(max_num) + 1):
            url = bashurl + '_' + str(num) + self.bashurl
            print 'We Get Next Url:%s' % url
            yield Request(url, callback=self.get_name)
            """yieid Request，请求新的URL，后面跟的是回调函数，你需要哪一个函数来处理这个返回值，就调用那一个函数，
                返回值会以参数的形式传递给你所调用的函数。
            """

    def get_name(self,response):
        print "spider start:"
        print "We've got all the URLs :%s" % response.url

        tds = BeautifulSoup(response.text, 'lxml').find_all('tr', bgcolor='#FFFFFF')
        for td in tds:
            """这儿用循环是因为find_all取出的来标签是以列表形式存在的；不然没法继续使用find"""
            novelname = td.find_all('a')[1].get_text().encode('utf-8')
            print "novelname:%s"%novelname
            novelurl = td.find('a')['href'].encode('utf-8')
            print "novelurl:%s" % novelurl
            #yield Request(novelurl, callback=self.get_chapterurl, meta={'name': novelname,
            #                                                            'url': novelurl})


    def get_chapterurl(self,response):
        item = DingdianSpiderItem()
        item['name'] = str(response.meta['name']).replace('\xa0', '')
        item['novelurl'] = response.meta['url']
        category = BeautifulSoup(response.text, 'lxml').find('table').find('a').get_text()
        author = BeautifulSoup(response.text, 'lxml').find('table').find_all('td')[1].get_text()
        bash_url = BeautifulSoup(response.text, 'lxml').find('p', class_='btnlinks').find('a', class_='read')['href']
        name_id = str(bash_url)[-6:-1].replace('/', '')
        item['category'] = str(category).replace('/', '')
        item['author'] = str(author).replace('/', '')
        item['name_id'] = name_id
        return item