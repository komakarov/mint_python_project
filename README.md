REST API бекенд онлайн ацкциона с возможностью прокси ставок, которые реализуют аукцион второй цены. 
Для запуска проекта необходимо добавить .env файл, который будет содержать переменные
```
DB_USER - пользователь базы данных
DB_PASSWORD - пароль от базы данных
DB_HOST - ip базы данных
DB_PORT - порт для соединений
DB_NAME - имя базы

```
После добавления .env файла необходимо создать виртуальное окружение и установить все зависимости из pyproject.toml к себе в виртуальное окружение
в нашем случае это будет осуществляться командой
```
uv pip install -r pyproject.toml
```

при запуске необходимо запустить миграции, которые реализованы через alembic, база данных в основном проекте postgres, для автотестов используется sqlite.

ER диаграмма представлена ниже

<img width="369" alt="Снимок экрана 2025-05-16 в 03 17 10" src="https://github.com/user-attachments/assets/6c45881f-84ed-4228-99f5-42f9a83fb2f7" />

после осуществления миграций можно запустить проект при помощи 

```
 uvicorn app.main:app --reload 
```
Далее мы можем перейти на localhost:8000 и увидеть, что нам доступны эндпоинты /docs и /redoc, выбираем /docs и переходим в swagger проекта
