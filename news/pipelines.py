# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

import mysql.connector
import pymongo

class NewsmysqlPipeline:
    def __init__(self):
        self.connection = mysql.connector.connect(
            host='localhost',
            user='lcbird',
            password='1140',
            database='newsdb'
        )
        self.cursor = self.connection.cursor()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        flow_raw = adapter.get('flow') or '0'

        if flow_raw[-1] == '万':
            flow_val = int(float(flow_raw[:-1]) * 10000)
        elif flow_raw[-1] == '亿':
            flow_val = int(float(flow_raw[:-1]) * 100000000)
        elif flow_raw[-1].isdigit():
            flow_val = int(flow_raw)
        else:
            flow_val = 0

        # url 上有唯一索引：重复条目更新热度，不产生重复行
        self.cursor.execute(
            'INSERT INTO news (name, url, flow) VALUES (%s, %s, %s) '
            'ON DUPLICATE KEY UPDATE name = VALUES(name), flow = VALUES(flow)',
            (adapter.get('title'), adapter.get('url'), flow_val)
        )
        self.connection.commit()
        return item

    def close_spider(self, spider):
        self.cursor.close()
        self.connection.close()

class NewsMongoPipeline:
    """Atlas 备份存储。连接为懒加载 + 可容错：外网/DNS 不可用时
    只打一条警告并跳过写入，不再拖死整个爬虫。"""

    def __init__(self):
        self.uri = "mongodb+srv://bird:1140@birdb.weqklox.mongodb.net/?appName=birdb"
        self.client = None
        self.collection = None
        self._warned = False

    def _ensure_connected(self):
        if self.collection is not None:
            return True
        try:
            self.client = pymongo.MongoClient(self.uri, serverSelectionTimeoutMS=3000)
            self.client.admin.command('ping')
            self.collection = self.client['Mynews']['bili']
            return True
        except Exception:
            if not self._warned:
                import logging
                logging.getLogger(__name__).warning(
                    'MongoDB Atlas unreachable; mongo pipeline disabled for this run')
                self._warned = True
            return False

    def process_item(self, item, spider):
        if not self._ensure_connected():
            return item
        adapter = ItemAdapter(item)
        flow_raw = adapter.get('flow') or '0'

        if flow_raw[-1] == '万':
            flow_val = int(float(flow_raw[:-1]) * 10000)
        elif flow_raw[-1] == '亿':
            flow_val = int(float(flow_raw[:-1]) * 100000000)
        elif flow_raw[-1].isdigit():
            flow_val = int(flow_raw)
        else:
            flow_val = 0

        try:
            self.collection.insert_one({
                'name': adapter.get('title'),
                'url': adapter.get('url'),
                'flow': flow_val
            })
        except Exception:
            pass
        return item

    def close_spider(self, spider):
        if self.client is not None:
            self.client.close()
