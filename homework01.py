# Напишите сценарий на языке Python, который предложит пользователю 
# ввести интересующую его категорию (например, кофейни, музеи, парки и т.д.).

# Используйте API Foursquare для поиска заведений в указанной категории.

# Получите название заведения, его адрес и рейтинг для каждого из них.
# Скрипт должен вывести название и адрес и рейтинг каждого заведения в консоль.

import requests
import json
import os
from dotenv import load_dotenv

# Загружаем окружение
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

# Вводим исходные данные
city = input("Введите город: ")
category = input("Введите категорию (например, кофейни, музеи, парки и т.д.): ")

# Конечная точка API
endpoint = "https://api.foursquare.com/v3/places/search"

# Определение параметров для запроса API
params = {    
    "near": city,
    "query": category,
    "limit": 10
}

headers = {
    "Accept": "application/json",
    "Authorization": os.getenv("API_KEY_FOURSQUARE")
}

# Отправка запроса API и получение ответа
response = requests.get(endpoint, params=params, headers=headers)

# Проверка успешности запроса API
if response.status_code == 200:
    print("Успешный запрос API!\n")
    data = json.loads(response.text)

    # Обработка результата запроса
    places = data["results"]
    for place in places:
        name = place.get('name', 'без названия')              
        address = place.get('location', '').get('address', '')        
        rating = place.get('rating', '')

        # Вывод информации о каждом заведении
        print(f"Название: {name}")
        print(f"Адрес: {address}")        
        print(f"Рейтинг: {rating}")
        print()
else:
    print("Запрос API завершился неудачей с кодом состояния:", response.status_code)
    print(response.text)
