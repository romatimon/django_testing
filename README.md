### Тестирование проектов, новостного сайта и электронной записной книжки.
```
# новостной сайт, где пользователи могут оставлять комментарии к новостям.
# электронная записная книжка для тех, кто не хочет ничего забыть и поэтому всё записывает. 
```
##
- тестами покрыт основной функционал новостного сайта и записной книжки, такие как добавление, редактирование и удаление элементов;
- реализована проверка различных сценариев работы с пользователями, таких как проверка корректной регистрации, аутентификации, обновления данных и других операций.

# Использованные технологии:
- Python 3.9
- Django 3.2
- Pytest
- Unittest
# Запуск проекта
1. ### Склонируйте репозиторий:
```
git clone https://github.com/romatimon/django_testing
```

2. ### Создайте и активируйте виртуальное окружение:
Команда для установки виртуального окружения на Mac или Linux:
```
python3 -m venv env
source env/bin/activate
```

Команда для установки виртуального окружения на Windows:
```
python -m venv venv
source venv/Scripts/activate
```

3. ### Установите зависимости:
```
pip install -r requirements.txt
```

## Как запустить тесты

Переходим в директорию ya_news и запускаем Pytest:

```
cd ya_news

pytest
```

Переходим в директорию ya_note и запускаем тесты Unittest:

```
cd ya_note

python manage.py test
```
Автор [romatimon](https://github.com/romatimon)
