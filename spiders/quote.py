from lxml import etree
from Item import Item

class Spider:
    urls = ['http://quotes.toscrape.com/'] * 3
    workerNum = 3

    def parse(self, response):
        tree = etree.HTML(response)
        for quote in tree.xpath('//div[@class="quote"]/span[@class="text"]/text()'):
            item = Item()    
            item['quote'] = quote
            yield item

        next_page = tree.xpath('//li[@class="next"]/a/@href')
        if next_page:
            yield 'http://quotes.toscrape.com' + next_page[0]
