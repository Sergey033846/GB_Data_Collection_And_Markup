# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import csv
import json
from itemadapter import ItemAdapter
from dromru_headers import HEADERS

class AutoparserPipeline:
    def __init__(self):
        self.items = []


    # записываем данные при завершении работы паука
    def close_spider(self, spider):
        """Метод вызывается при завершении работы паука."""
        if self.items:                        
            with open(f'{spider.name}.csv', newline='', mode='w', encoding='utf-8') as file_csv:                
                self.writer = csv.DictWriter(file_csv, fieldnames=HEADERS, delimiter=';', quoting=csv.QUOTE_ALL)
                self.writer.writeheader()
                self.writer.writerows(self.items)
            print('Запись полученных данных в CSV завершена.')        

            with open(f'{spider.name}.json', 'w', encoding='utf-8') as file_json:
                json.dump(self.items, file_json, ensure_ascii=False, indent=4)
            print('Запись полученных данных в JSON завершена.')


    # накапливаем полученные данные
    def process_item(self, item, spider):
        """Метод вызывается для каждого элемента, полученного пауком."""        
        self.items.append(list(dict(item).values())[0])  
        print(f'{len(self.items)} - {self.items[-1]['Название']} - {self.items[-1]['Цена']}')   # для прогресса
        return item
