# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html




import json
import codecs


from twisted.enterprise import adbapi
import MySQLdb
import MySQLdb.cursors
import copy
from items import DingdianSpiderItem,DcontentItem
import logging

class DingdianSpiderPipeline(object):
    def process_item(self, item, spider):
        return item

'''保存文件'''
class JsonWithEncodingPipeline(object):
    def __init__(self):
        self.file = codecs.open('save_data.json', mode='wb', encoding='utf-8')

    def process_item(self, item, spider):

        line = json.dumps(dict(item)) + '\n'
        self.file.write(line.decode("unicode_escape"))
        return item


"""
保存在数据库
"""

class MySQLPipeline(object):
    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        dbargs = dict(
            host=settings['MYSQL_HOST'],
            db=settings['MYSQL_DBNAME'],
            user=settings['MYSQL_USER'],
            passwd=settings['MYSQL_PASSWD'],
            charset='utf8',
            cursorclass=MySQLdb.cursors.DictCursor,
            use_unicode=True,
        )
        dbpool = adbapi.ConnectionPool('MySQLdb', **dbargs)
        return cls(dbpool)

    # pipeline默认调用
    def process_item(self, item, spider):
        logging.info("process_item function ")
        # 深拷贝,防止进入数据库有重复
        asynItem = copy.deepcopy(item)
        d = self.dbpool.runInteraction(self._do_upinsert, asynItem, spider)

        # d = self.dbpool.runInteraction(self._do_upinsert, item, spider)
        d.addErrback(self._handle_error, item, spider)
        d.addBoth(lambda _: item)
        return d

    # 将每行更新或写入数据库中
    def _do_upinsert(self, conn, item, spider):

        if isinstance(item, DingdianSpiderItem):
            select_sql = "select id from dd_name where name_id= '%s'" % (item['name_id'])
            conn.execute(select_sql)
            ret = conn.fetchone()

            if ret:
                logging.info("_do_upinsert function --DingdianSpiderItem-- Item already stored in db:%s" % item)
            else:
                insert_sql = "insert into dd_name (xs_name,xs_author,category,name_id) values ('%s','%s','%s','%s')" \
                             % (item['name'], item['author'], item['category'], item['name_id'])
                conn.execute(insert_sql)

                logging.info("_do_upinsert function --DingdianSpiderItem-- Item stored in db: %s" % insert_sql)

        if isinstance(item, DcontentItem):
            select_sql = "select id from dd_chaptername where url= '%s'" % (item['chapterurl'])
            conn.execute(select_sql)
            ret = conn.fetchone()

            if ret:
                logging.info("_do_upinsert function --DcontentItem-- Item already stored in db:%s" % item)
            else:
                insert_sql = "insert into dd_chaptername (`xs_chaptername`, `xs_content`, `id_name`, `num_id`, `url`) values ('%s','%s','%s','%s','%s')" \
                             % (item['chaptername'], item['chaptercontent'], item['id_name'], item['num'], item['chapterurl'])
                conn.execute(insert_sql)

                logging.info("_do_upinsert function --DcontentItem-- Item stored in db: %s" % insert_sql)


    # 异常处理
    def _handle_error(self, failure, item, spider):
        logging.info("_handle_error function -- failure:%s" % failure)


