import requests
import json
from bs4 import BeautifulSoup
from fake_useragent import UserAgent


url_catalogue = 'https://books.toscrape.com/catalogue/'
ua = UserAgent()
headers = {"User-Agent": ua.chrome}
session = requests.session()

page = 1
books = []

# переходим по страницам каталога до тех пор, пока не появится ошибка
while (True):    
    print(f'Запрашиваем информацию со страницы {page}')

    response = session.get(f'{url_catalogue}page-{page}.html', headers=headers)

    if response.status_code == 200:
        soap = BeautifulSoup(response.text, 'html.parser')

        # формируем список url на книги, расположенные на текущей странице
        # т.к. для каждой книги будет два url (изображение + ссылка-название), то берем каждый второй url
        books_hrefs_on_page = list(map(lambda x: f"{url_catalogue}{x.get('href')}", soap.find('ol', {'class': 'row'}).find_all('a')[1::2]))

        # переходим по каждой книге на странице 
        for books_href in books_hrefs_on_page:
            resp_book = session.get(books_href, headers=headers)
            if resp_book.status_code == 200:
                book_info = {}
                soap_page = BeautifulSoup(resp_book.text, 'html.parser')                        
                info_page = soap_page.find('article', {'class': 'product_page'})
                info_main = info_page.find('div', {'class': 'product_main'})

                # парсим Название и Цену в валюте каталога
                book_info['Title'] = info_main.find('h1').getText()
                book_info['Price'] = info_main.find('p', {'class': 'price_color'}).getText()[1:]

                # парсим Доступность на складе
                available = info_main.find('p', {'class': 'instock availability'}).getText().lower()
                if 'in stock' in available:
                    book_info['Available'] = int(available.split('(')[1].split(' ')[0])
                else:
                    book_info['Available'] = 0

                # парсим Описание
                p_tag_wout_class = info_page.find('p', {'class': ''})
                if p_tag_wout_class:
                    book_info['Description'] = p_tag_wout_class.getText()
                else:
                    book_info['Description'] = 'The description is not specified'
                                
                books.append(book_info)
            else:
                print(f"Запрос к информации о книге завершился неудачей с кодом состояния: {resp_book.status_code}")
                print(resp_book.text)
                break
    else:
        print(f"Запрос завершился неудачей с кодом состояния: {response.status_code}")
        print(response.text)
        break

    page += 1


# записываем в json-файл, устанавливаем параметры для корректной записи Unicode-символов (валют и пр.)
with open('homework02.json', 'w', encoding='utf-8') as json_file:
    json.dump(books, json_file, indent=4, ensure_ascii=False)


print('Парсинг завершен.')
