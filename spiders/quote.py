import logging

from lxml import etree
from Item import Item

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class Spider:
    urls = ['http://quotes.toscrape.com/'] * 3
    workerNum = 3

    def parse(self, response):
        for quote in response.extract('//div[@class="quote"]/span[@class="text"]/text()'):
            item = Item()    
            item['quote'] = quote
            logger.info(f'item: {item}')
            yield item

        next_page = response.extract_first('//li[@class="next"]/a/@href')
        if next_page:
            yield response.follow(next_page)
