# Тестовое задание
## Description
Проект состоит из 2 частей: FastAPI + postgres API и yandex cloud функции-парсера
## Decision process
1. К сожалению у Github GraphQL API маленькие лимиты на запрос и радномные таймауты и приходится доставать дату из REST API
2. Решил придерживаться того что: чем меньше запросов к базу тем лучше - собираем балк инзерты (straight-forward решение зачекаучено в ветке basic-solution, его минус в том что оно делает непозволительно много запросов к бд)
3. Клауд функция...

## Possible flaws
1. Если коммиты на гитхабе удалялись то в нашей базе они остаются навсегда и данные о количестве коммитов могут отображаться некорректно

## Deploy

### FastAPI App and database
Autodeploy is done via Github Actions. Fork the repo and fill the secrets with your data and you are ready to go (could be done with gitempty commit)

BE AWARE: app's docker image name is currently hardcoded in docker-compose.production.yml

Simple and dumb way to deploy
- fill the .env with your data
- ssh to your VDS
- clone the repo
- docker compose -f docker-compose.yml build && docker -f docker-compose.yml compose up
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
  --memory 128m \
  --execution-timeout 30s \
  --source-path <path to yandex-cloud-func.zip> \
  --environment GITHUB_PAT=<your token>
```
## To do
