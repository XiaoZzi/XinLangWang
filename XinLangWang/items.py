# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import TakeFirst, Join
from scrapy.loader import ItemLoader
import datetime
from settings import SQL_DATE_FORMAT


class XinLang(ItemLoader):
    default_output_processor = TakeFirst()


class XinlangwangDetailItem(scrapy.Item):
    crawl_keyword = scrapy.Field()
    title = scrapy.Field()
    date = scrapy.Field()
    url = scrapy.Field()
    url_id = scrapy.Field()
    content = scrapy.Field(
        output_processor=Join('')
    )
    comment_num = scrapy.Field()
    participate_num = scrapy.Field()
    crawl_time = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = '''
                    INSERT INTO sina(content, url_id, crawl_time, comment_num, participate_num, crawl_keyword, title, 
                    date, url) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE content=VALUES(
                    content), crawl_time=VALUES(crawl_time)
                '''
        crawl_time = datetime.datetime.now().strftime(SQL_DATE_FORMAT)
        if self['comment_num']:
            comment_num = int(self['comment_num'])
        else:
            comment_num = 0
        if self['participate_num']:
            participate_num = int(self['participate_num'])
        else:
            participate_num = 0
        if self['content']:
            content = self['content']
        else:
            content = ''

        params = (content, self['url_id'], crawl_time, comment_num, participate_num, self['crawl_keyword'],
                  self['title'], self['date'], self['url'])
        return insert_sql, params
