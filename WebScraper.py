import scrapy
from scrapy.crawler import CrawlerProcess

import os
import json

import logging

class JsonWriterPipeline(object):

    def open_spider(self, spider):
        if not os.path.exists('./data'):
            os.mkdir('./data')
        self.file = open('./data/coronacases.jsonl', 'w')

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        line = json.dumps(dict(item)) + "\n"
        self.file.write(line)
        return item


class Coronacases(scrapy.Spider):
    name = 'countries'
    allowed_domains = ['www.worldometers.info']
    start_urls = ['https://www.worldometers.info/coronavirus/']

    custom_settings = {
        'LOG_LEVEL': logging.WARNING,
        'ITEM_PIPELINES': {'__main__.JsonWriterPipeline': 1},
        'FEED_FORMAT':'json',                                 
        'FEED_URI': './data/coronacases.json'                        
    }

    def parse(self, response):

        rows = response.xpath('(.//table[@id="main_table_countries_today"])[1]/tbody/tr[@style=""]')
        for row in rows:
            name = row.xpath('.//td[2]/a/text() | .//td[2]/span/text() ').get()
            totcases = row.xpath(".//td[3]/text()").get()
            totdeaths = row.xpath(".//td[5]/text()").get()
            actcases = row.xpath(".//td[9]/text()").get()
            totpop = row.xpath(".//td[15]/a/text() | .//td[15]/text() ").get()
            if ((actcases!='N/A' and actcases!=' ') and (totpop!='N/A' and totpop!=' ')):
                percpop = round(((float(actcases.replace(',',''))/float(totpop.replace(',','')))*100),5)
            yield {
               "country_name": name,
                "Total_cases": totcases,
                "Total_deaths":totdeaths,
                "Active_Cases":actcases,
                "Total_Population":totpop,
                "% Active Cases per capita": str(percpop) + " %"
            }


process = CrawlerProcess({
    'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
})



process.crawl(Coronacases) 
process.start()
