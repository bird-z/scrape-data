# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

def parse_flow(flow):
    if flow[-1] == '万':
        return int(float(flow[:-1]) * 10000)
    elif flow[-1] == '亿':
        return int(float(flow[:-1]) * 100000000)
    elif flow[-1] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
        return int(flow)
    return 0
 

class NewsItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()

    title = scrapy.Field()
    url = scrapy.Field()
    flow = scrapy.Field(serializer=parse_flow)

   