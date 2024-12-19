import scrapy
from scrapy.http import HtmlResponse
from autoparser.items import AutoparserItem
from dromru_headers import HEADERS


class DromruSpider(scrapy.Spider):
    name = "dromru"
    allowed_domains = ["drom.ru"]
    start_urls = ["https://irkutsk.drom.ru/toyota/rav4/"]


    def parse(self, response: HtmlResponse):
        print(f'Обработка страницы {response.url}, код ответа {response.status}')

        if response.status == 200:
            # распараллелим обработку:
            
            # - переходим на следующую страницу
            next_page = response.xpath("//a[@data-ftid='component_pagination-item-next']/@href").get()
            if next_page:
                yield response.follow(next_page, callback=self.parse)

            # - обрабатываем текущую страницу
            links = response.xpath("//a[@data-ftid='bull_title']/@href").getall()      
            for link in links:
                yield response.follow(link, callback=self.auto_ad_parse)          


    # функция для парсинга одного объявления
    def auto_ad_parse(self, response: HtmlResponse):        
        data = {key: '' for key in HEADERS}        
        data['Название'] = response.xpath("//h1[@class='css-1tjirrw e18vbajn0']/span/text()").get()
        data['Цена'] = float(response.xpath("//div[@class='wb9m8q0']//text()").get().replace('\xa0', ''))
                
        # Ищем все строки таблицы <tr> - данные об автомобиле хранятся в них (th - параметр, td - значение)
        tr_elements = response.xpath("//table/tbody/tr")        
        if tr_elements:
            for tr in tr_elements:                
                key = tr.xpath('.//th/text()').get()
                value = tr.xpath('.//td//text()').getall()
    
                # Удаляем лишнее
                if key and value:
                    cleaned_value = ' '.join(v.strip() for v in value if v.strip() and '{' not in v and '}' not in v)
                    if key == 'Мощность':
                        cleaned_value = cleaned_value.replace(' , налог', '')
                    if key == 'Пробег':
                        cleaned_value = cleaned_value.replace(' ', '').replace('\xa0', '').replace('км','')
                    data[key.strip()] = cleaned_value
        data['url'] = response.url        
        
        yield AutoparserItem(info=data)
          
