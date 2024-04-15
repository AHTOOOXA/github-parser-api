# Тестовое задание
## Description

## Decision process

## Deploy

### FastAPI App and database


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
