# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from twisted.enterprise import adbapi
import pymysql


class XinlangwangPipeline(object):
    def process_item(self, item, spider):
        return item


class MysqlTwistedPipeline(object):
    # twisted内置的mysql异步存储方式
    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_crawler(cls, crawler):
        dbparams = dict(
            host=crawler.settings.get('MYSQL_HOST'),
            user=crawler.settings.get('MYSQL_USER'),
            password=crawler.settings.get('MYSQL_PASSWORD'),
            port=crawler.settings.get('MYSQL_PORT'),
            database=crawler.settings.get('MYSQL_DB'),
            charset=crawler.settings.get('MYSQL_CHARSET'),
            cursorclass=pymysql.cursors.DictCursor,
            use_unicode=True,
        )
        dbpool = adbapi.ConnectionPool('pymysql', **dbparams)
        return cls(dbpool)

    def process_item(self, item, spider):
        # 使用twisted将mysql变为异步执行
        query = self.dbpool.runInteraction(self.do_insert, item)  # 将函数变为异步执行,并返回处理后的query对象
        query.addErrback(self.handle_error, item, spider)  # 对错误进行异步处理
        return item

    def do_insert(self, cursor, item):
        insert_sql, params = item.get_insert_sql()
        cursor.execute(insert_sql, params)
        return item

    def handle_error(self, failure, item, spider):
        # 处理异步插入的异常
        print(failure)
        print('failure', item)

