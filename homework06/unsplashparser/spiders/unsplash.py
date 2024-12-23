import scrapy
from scrapy.http import HtmlResponse
from unsplashparser.items import UnsplashparserItem
from scrapy.loader import ItemLoader
from unsplashparser.items import UnsplashparserItem

class UnsplashSpider(scrapy.Spider):
    name = "unsplash"

    #allowed_domains = ["unsplash.com"]        
    #start_urls = ['https://unsplash.com/backgrounds/']    

    """
    Почему-то при попытке использовать паука с сайтом unsplash.com возникает ошибка 403.
    При этом в браузере все открывается.
    В качестве альтернативы был использован похожий сайт lummi.ai, с ним все работает без ошибок.
    """

    allowed_domains = ['lummi.ai']
    start_urls = ['https://www.lummi.ai/explore']

    def parse(self, response: HtmlResponse):        
        """Перебираем категории изображений."""                       
        categories_divs = response.xpath("//div[@class='flex gap-2']/div[@class='grow first:pl-3 sm:first:pl-6 last:pr-3 sm:last:pr-6']")
        for category_div in categories_divs: 
            category_link = category_div.xpath("./a/@href").get()
            category_text = category_div.xpath(".//span/text()").get()            
            yield response.follow(url=category_link, callback=self.parse_category, cb_kwargs={'category': category_text})
        
    def parse_category(self, response: HtmlResponse, category):       
        """Перебираем изображения внутри категории."""                        
        image_page_links = response.xpath("//a[@class='absolute inset-0 z-20']/@href").getall()        
        for image_link in image_page_links:            
            yield response.follow(image_link, callback=self.parse_image, cb_kwargs={'category': category})

    def parse_image(self, response: HtmlResponse, category):        
        """Скрейпим одно изображение."""                       
        loader = ItemLoader(item=UnsplashparserItem(), response=response)        
        loader.add_value('category', category)
        loader.add_xpath('name', '//h1/text()')        
        loader.add_xpath('url', "//img[@class='absolute inset-0 m-auto max-w-full max-h-full']/@src")
        item = loader.load_item()       
        yield item
