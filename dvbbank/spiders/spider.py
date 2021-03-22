import scrapy

from scrapy.loader import ItemLoader

from ..items import DvbbankItem
from itemloaders.processors import TakeFirst


class DvbbankSpider(scrapy.Spider):
	name = 'dvbbank'
	start_urls = ['https://www.dvbbank.com/en/media/press-releases']

	def parse(self, response):
		year_links = response.xpath('//div[@class="newsletter_tab"]//a/@href').getall()
		yield from response.follow_all(year_links, self.parse_year)

	def parse_year(self, response):
		post_links = response.xpath('//p/a/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

		next_page = response.xpath('//div[@class="prpagination"]//a/@href').getall()
		for page in next_page:
			if page != 'javascript:':
				yield response.follow(page, self.parse)

	def parse_post(self, response):
		title = response.xpath('//div[@class="rad-introtext titlePR"]/text()[normalize-space()]').get()
		description = response.xpath('//div[@class="contentPR"]//p//text()[normalize-space()]').getall()
		description = [p.strip() for p in description]
		description = ' '.join(description).strip()
		date = response.xpath('//div[@class="rad-introtext titlePR"]/div[@class="datePR"]/text()').get()

		item = ItemLoader(item=DvbbankItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
