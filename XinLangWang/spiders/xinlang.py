# -*- coding: utf-8 -*-
import json
import scrapy
from settings import KEYWORDS
from selenium import webdriver
from scrapy import signals
from pydispatch import dispatcher
from urllib import parse
from items import XinLang, XinlangwangDetailItem
from utils.common import get_md5


class XinlangSpider(scrapy.Spider):
    name = 'xinlang'
    # allowed_domains = ['www.sina.com.cn']
    start_urls = ['http://www.sina.com.cn/']

    custom_settings = {
        'DOWNLOAD_DELAY': 0.2,
        'CONCURRENT_REQUESTS_PER_IP': 1,
    }
    base_url = 'http://api.search.sina.com.cn/?'

    # def __init__(self):
    #     super(XinlangSpider, self).__init__()
    #     self.driver = webdriver.Chrome()
    #     chrome_opt = webdriver.ChromeOptions()
    #     pref = {'profile.managed_default_content_settings.images': 2}
    #     chrome_opt.add_experimental_option('prefs', pref)
    #     self.driver = webdriver.Chrome(chrome_options=chrome_opt)
    #     dispatcher.connect(self.close_driver, signal=signals.spider_closed)
    #
    # def close_driver(self):
    #     print('driver quit')
    #     self.driver.quit()

    def start_requests(self):
        global start_url
        for keyword in KEYWORDS:
            for i in range(5):
                parms = {
                    'c': 'news',
                    'q': keyword,
                    't': '',
                    # 'pf': '2140076151',
                    # 'ps': '2130770042',
                    'page': str(i),
                    # 'sort': 'rel',
                    # 'highlight': '1',
                    # 'num': '10',
                    'ie': 'utf-8'
                }
                start_url = self.base_url + parse.urlencode(parms)
                yield scrapy.Request(url=start_url, callback=self.parse, meta={'keyword': keyword})

    def parse(self, response):
        # 提取keyword
        keyword = response.meta.get('keyword', '')

        # 从接口提取详情页URL
        if 200 <= response.status < 300:
            response = json.loads(response.body)
            info_list = response.get('result').get('list')
            for info in info_list:
                url = info.get('url')
                if url.endswith('shtml'):
                    yield scrapy.Request(url=url, callback=self.parse_content, meta={'keyword': keyword})

    def parse_content(self, response):
        if 200 <= response.status < 300:
            item_loader = XinLang(item=XinlangwangDetailItem(), response=response)
            item_loader.add_value('url_id', get_md5(response.url))
            item_loader.add_value('crawl_keyword', response.meta.get('keyword'))
            item_loader.add_value('url', response.url)
            if response.xpath('//*[@class="time-source"]/span[1]/text()'):
                item_loader.add_xpath('date', '//*[@class="time-source"]/span[1]/text()')
            elif response.xpath('//*[@class="date-source"]/span[1]/text()'):
                item_loader.add_xpath('date', '//*[@class="date-source"]/span[1]/text()')
            elif response.css('#pub_date::text'):
                item_loader.add_css('date', '#pub_date::text')
            else:
                item_loader.add_value('date', 'NULL')
            item_loader.add_css('title', 'h1::text')
            if response.css('#artibody p::text'):
                item_loader.add_css('content', '#artibody p::text')
            else:
                item_loader.add_value('content', '')
            if response.css('#bottom_sina_comment .hd.clearfix a[data-sudaclick="comment_sum_p"]::text'):
                item_loader.add_css('comment_num', '#bottom_sina_comment .hd.clearfix a[data-sudaclick="comment_sum_p"]::text')
            else:
                item_loader.add_value('comment_num', 0)
            if response.css('#bottom_sina_comment .hd.clearfix a[data-sudaclick="comment_participatesum_p"]::text'):
                item_loader.add_css('participate_num', '#bottom_sina_comment .hd.clearfix a[data-sudaclick="comment_participatesum_p"]::text')
            else:
                item_loader.add_value('participate_num', 0)
            item = item_loader.load_item()
            yield item
