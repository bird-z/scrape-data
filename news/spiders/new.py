import scrapy
from news.items import NewsItem

class NewSpider(scrapy.Spider):
    name = "new"
    allowed_domains = ["tophub.today"]
    start_urls = ["https://tophub.today/n/74KvxwokxM"]

    def parse(self, response):
        
        for news in response.xpath("//tbody/tr"):
            news_name = news.xpath("td[@class='al'][last()]//a/text()").get()
            news_url = news.xpath("td[@class='al'][last()]//a/@href").get()
            news_flow = news.xpath("td[@class='al'][last()]/div[@class='item-desc']/text()").get()

            mynews=NewsItem()

            mynews['title'] = news_name
            mynews['url'] = news_url
            mynews['flow'] = news_flow

            yield mynews
            
