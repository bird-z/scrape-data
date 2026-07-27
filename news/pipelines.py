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

        self.cursor.execute(
            'INSERT INTO news (name, url, flow) VALUES (%s, %s, %s)',
            (adapter.get('title'), adapter.get('url'), flow_val)
        )
        self.connection.commit()
        return item

    def close_spider(self, spider):
        self.cursor.close()
        self.connection.close()

class NewsMongoPipeline:
    def __init__(self):
        self.uri = "mongodb+srv://bird:1140@birdb.weqklox.mongodb.net/?appName=birdb"
        self.client=pymongo.MongoClient(self.uri)
        self.db=self.client['Mynews']
        self.collection=self.db['bili']
        # self.collection.client.serverSelectionTimeoutMS=5000

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

        self.collection.insert_one({
            'name': adapter.get('title'),
            'url': adapter.get('url'),
            'flow': flow_val
        })
        return item

    def close_spider(self, spider):
        self.client.close()
