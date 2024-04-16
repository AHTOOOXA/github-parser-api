# Тестовое задание
Прямо сейчас доступно на http://92.53.120.193:7777/docs
## Description
Проект состоит из 2 частей: FastAPI + postgres API и yandex cloud функции-парсера
## Decision process
1. К сожалению у Github GraphQL API маленькие лимиты на запрос и радномные таймауты и приходится доставать дату из REST API
2. Решил придерживаться того что: чем меньше запросов к базу тем лучше - собираем балк инзерты (можно было написать парсер асинхронно но тогда в 4 запроса не обойтись и кажется что это было бы хуже)
3. Клауд функцию вызывать стоит не чаще раза в день тк она db heavy и новые коммиты появляются достаточно редко (но только в случае если нет специфических бизнес требований)
4. На тесты не хватило сил да и тестить тут особо нечего

## To Do
1. Добавить тесты
2. Доделать yandex cloud function github action ну или написать свой скрипт (не стал это делать тк яндексклауд невыносим если честно, нормальных гитхаб экшенов я быстро не нашел)
3. Уместным было бы кешировать эндпоинты для ускорения работы

***Для очень read-heavy приложения*** реализация схемы бд может быть дополнена такими таблицами, заполнение данных станет дороже (оно происходит редко), но get запросы станут быстрее тк мы избавимся от COUNT() 
```sql
CREATE TABLE IF NOT EXISTS activity (
    activity_id SERIAL PRIMARY KEY,
    repo_id INT NOT NULL,
    date DATE NOT NULL,
    commits INT NOT NULL,
    FOREIGN KEY (repo_id) REFERENCES repositories (repo_id)
);
CREATE TABLE IF NOT EXISTS activity_authors (
    activity_id INT NOT NULL,
    author_id INT NOT NULL,
    PRIMARY KEY (activity_id, author_id),
    FOREIGN KEY (activity_id) REFERENCES activity (activity_id),
    FOREIGN KEY (author_id) REFERENCES authors (author_id)
);
```

## Possible flaws
1. Если коммиты на гитхабе удалялись то в нашей базе они остаются навсегда и данные о количестве коммитов могут отображаться некорректно
2. Никак не обозночается в респонсах на .../activity полная ли есть информация о коммитах у нас о интервале since until (было лень так сильно заморачиваться)

## Deploy

### FastAPI App and database
Autodeploy is done via Github Actions (взял за основу деплой vas3k.club). Fork the repo and fill the secrets with your data and you are ready to go (could be done with gitempty commit)

***BE AWARE***: первый раз нужно вручную запустить initial_setup.sql в db_docker (надо в гитхаб экшн бы добавить но я уже засыпаю)

***BE AWARE***: app's docker image name is currently hardcoded in docker-compose.production.yml

Simple and dumb way to deploy
- fill the .env with your data
- ssh to your VDS
- clone the repo
- docker compose -f docker-compose.yml build && docker -f docker-compose.yml compose up
- выполнить initial_setup.sql в db_docker
- Congrats! API is available at YOUR-HOST:7777/docs
### Yandex cloud function
Установить Yandex CLI и выполнить действия аналогично инструкции
https://yandex.cloud/ru/docs/functions/quickstart/create-function/python-function-quickstart
```
yc serverless function create --name=<your function name>
```
Создать .zip архив с содержимым папки yandex-cloud-fucn
```
yc serverless function version create \
  --function-name=<your fucntion name>> \
  --runtime python311 \
  --entrypoint func.handler \
  --memory 256m \
  --execution-timeout 180s \
  --source-path <path to yandex-cloud-func.zip> \
  --environment GITHUB_PAT=<your token>,DB_HOST=${{ secrets.DB_HOST }},DB_PORT=${{ secrets.DB_PORT }},DB_NAME=${{ secrets.DB_NAME }},DB_USER=${{ secrets.DB_USER }},DB_PASS=${{ secrets.DB_PASS }}
```
```
yc serverless function invoke <your function name>
```