# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import scrapy
from itemadapter import ItemAdapter
from scrapy.pipelines.images import ImagesPipeline
import csv
import os


# Сохранение результатов работы паука
class Save2CSVPipeline:
    def __init__(self):
        self.items = []

    # записываем данные при завершении работы паука
    def close_spider(self, spider):
        """Метод вызывается при завершении работы паука."""
        HEADERS = ['category', 'name', 'path', 'url']
        if self.items:                        
            with open(f'{spider.name}.csv', newline='', mode='w', encoding='utf-8') as file_csv:                
                self.writer = csv.DictWriter(file_csv, fieldnames=HEADERS, delimiter=';', quoting=csv.QUOTE_ALL)
                self.writer.writeheader()
                self.writer.writerows(self.items)
            print('Запись полученных данных в CSV завершена.')        

    # накапливаем полученные данные
    def process_item(self, item, spider):
        """Метод вызывается для каждого элемента, полученного пауком."""                
        self.items.append(item)          
        return item


# Основной класс пайплайна
class UnsplashparserPipeline(ImagesPipeline):    
    def file_path(self, request, response=None, info=None, *, item=None):        
        """Корректируем путь сохранения изображения в зависимости от его категории."""                
        original_path = super().file_path(request, response, info, item=item)        
        category = item.get('category', 'default').replace(" ",'_')        
        return os.path.join(category, original_path).replace(os.sep, '/')

    def get_media_requests(self, item, info):
        try:
            yield scrapy.Request(item['url'])
        except Exception as e:
            print(e)

    def item_completed(self, results, item, info):        
        if results:            
            item['path'] = results[0][1]['path'] if results[0][0] else None
        print(item)     # для прогресса
        return item
