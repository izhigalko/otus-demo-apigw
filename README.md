# Практика к занятию по теме "Api gateway"

## Зависимости

Для выполнения задания вам потребуется установить зависимости:

- [Minikube 1.20.0](https://github.com/kubernetes/minikube/releases/tag/v1.20.0)
- [Kubectl 0.19.2](https://github.com/kubernetes/kubectl/releases/tag/v0.19.2)
- [Istioctl 1.9.0](https://github.com/istio/istio/releases/tag/1.9.0)

После установки нужно запустить Kubernetes. При необходимости можно изменить используемый драйвер с помощью
флага `--driver`. 

```shell script
minikube start \
--cpus=4 --memory=8g \
--cni=flannel \
--kubernetes-version="v1.19.0"
```

Операции будут совершаться с помощью утилиты `kubectl`

## Содержание

* [Разворачиваем приложения](#Разворачиваем-приложения)
* [Описание стенда](#Описание-стенда)
* [Установка Istio и Gateway](#Установка-Istio-Gateway)
* [Установка Traefik](#Установка-Traefik)
* [Установка Ambassador](#Установка-Ambassador)
* [Установка Nginx ingress](#Установка-Nginx-ingress)
* [Установка Haproxy](#Установка-Haproxy)
* [Аутентификация и Авторизация](#Аутентификация-и-авторизация)

## Разворачиваем приложения

Создать неймспейсы:

```shell
kubectl apply -f namespaces.yaml
```

### Echoserver

Echoserver - сервис, отдающий в виде текста параметры входящего HTTP запроса.

Собрать Docker-образ:

```shell
eval $(minikube docker-env) && docker build -t echoserver:latest -f app/echoserver/Dockerfile app/echoserver
```

Развернуть в Kubernetes:

```shell
kubectl apply -f app/echoserver/k8s.yaml
```

Проверить статус:

```shell
kubectl get po -l "app=echoserver"
```

### Auth-service

Auth-service - сервис аутентификации, предоставляет возможности для входа пользователя и генерирует JWT.

Собрать Docker-образ:

```shell
eval $(minikube docker-env) && docker build -t auth-service:latest -f app/auth-service/Dockerfile app/auth-service
```

Развернуть в Kubernetes:

```shell
kubectl apply -f app/auth-service/k8s.yaml
```

Проверить статус:

```shell
kubectl get po -l "app=auth-service"
```

## Описание стенда

В кластере развернуто два пользовательских приложения: `auth-service`, `echoserver`. А так же, несколько
реализаций API Gateway:

- Istio
- Ambassador
- Traefik
- Nginx ingress

Со всеми Api Gateway действуют правила:

- Запросы к `/auth/*` попадают на `auth-service` и не проходят проверку авторизации
- Остальные запросы попадают на `echoserver` и проходят проверку авторизации

## Установка Istio Gateway

Istio - Service mesh решение для облачных платформ, использующее Envoy.

Установить оператор, разворачивающий Istio:

```shell
istioctl operator init --watchedNamespaces istio-system --operatorNamespace istio-operator
```

Развернуть Istio c помощью оператора:

```shell
kubectl apply -f apigw/istio/istio.yaml
```

Проверить состояние Istio:

```shell
kubectl get all -n istio-system -l istio.io/rev=default
```

Настроить Gateway:

```shell
kubectl apply -f apigw/istio/routes.yaml
```

Получить список портов:

```shell
minikube service -n istio-system istio-ingressgateway 
```

Выбрать порт, соответствующий 80 и перейти по ссылке. При первоначальной настройке 
по ссылке будет ответ от echoserver.

## Установка Traefik

Traefik - позиционируется как "маршрутизатор" запросов из документации. 

Добавить репозиторий в Helm:

```shell
helm repo add traefik https://helm.traefik.io/traefik
helm repo update
```

Развернуть traefik:

```shell
helm install --version "10.1.2" -n traefik -f apigw/traefik/traefik.yaml traefik traefik/traefik
```

Проверить работоспособность:

```shell
kubectl get po -n traefik
```

Настроить маршруты:

```shell
kubectl apply -f apigw/traefik/routes.yaml
```

Получить список портов:

```shell
minikube service -n traefik traefik
```

Выбрать порт, соответствующий 80 и перейти по ссылке. При первоначальной настройке
по ссылке будет ответ от echoserver.


## Установка Ambassador

Ambassador Edge Stack - позиционируется как решение для управления трафиком на уровне L4/L7.

Ambassador поставляется в нескольких вариациях. Для Demo мы будем использовать Community edition.
Для его использования нужно получить ключ по ссылке https://www.getambassador.io/aes-community-license-renewal/.

Добавить репозиторий в Helm:

```shell
helm repo add datawire https://www.getambassador.io
helm repo update
```

Развернуть Ambassador:

```shell
helm install --version "6.7.13" -n ambassador --set licenseKey.value=<Ключ, полученный по ссылке> \
-f apigw/ambassador/ambassador.yaml ambassador datawire/ambassador
```

Проверить работоспособность:

```shell
kubectl get po -n ambassador
```

Настроить маршруты:

```shell
kubectl apply -f apigw/ambassador/routes.yaml
```

Получить список портов:

```shell
minikube service -n ambassador ambassador
```

Выбрать порт, соответствующий 80 и перейти по ссылке. При первоначальной настройке
по ссылке будет ответ от echoserver.

## Установка Nginx ingress

Nginx ingress - стандартное решение для терминирования внешнего трафика в кластер.

Добавить репозиторий в Helm:

```shell
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update
```

Развернуть Nginx ingress:

```shell
helm install --version "3.35.0" -n nginx-ingress -f apigw/nginx-ingress/nginx.yaml \
ingress-nginx ingress-nginx/ingress-nginx
```

Проверить работоспособность:

```shell
kubectl get po -n nginx-ingress
```

Настроить маршруты:

```shell
kubectl apply -f apigw/nginx-ingress/routes.yaml
```

Получить список портов:

```shell
minikube service -n nginx-ingress ingress-nginx-controller 
```

Выбрать порт, соответствующий 80 и перейти по ссылке. При первоначальной настройке
по ссылке будет ответ от echoserver.

# Установка Haproxy

Haproxy - прокси сервер. Это пример того, что прокси сервера можно использовать и для внутренних коммуникаций,
настраивая их вручную.

Развернуть Haproxy:

```shell
kubectl apply -f apigw/haproxy/haproxy.yaml
```

Проверить работоспособность:

```shell
kubectl get po -l app=gateway
```

Получить список портов:

```shell
minikube service gateway
```

Выбрать порт, соответствующий 80 и перейти по ссылке. При первоначальной настройке
по ссылке будет ответ от echoserver.

# Аутентификация и авторизация

Паттерн Forward-Auth позволяет аутентифицировать запрос с помощью [стороннего сервиса](assets/forward-auth.puml).

Так же, паттерн позволяет использовать перенаправления
и можно организовать [процесс аутентификации на их основе](assets/forward-auth-with-login.puml).

Применить настройки аутентификации:

```shell
kubectl apply -f apigw/istio/auth.yaml 
kubectl apply -f apigw/traefik/auth.yaml
kubectl apply -f apigw/ambassador/auth.yaml
kubectl apply -f apigw/nginx-ingress/auth.yaml  
```

Так же, сервис аутентификации может возвращать [Json web token](https://jwt.io/introduction), который можно
использовать для дальнейшей авторизации запроса, без обращения к сервису.

Применить настройки авторизации, которые позволяют пользователю `admin` иметь доступ к ресурсу `/admin`:

```shell
kubectl apply -f apigw/istio/jwt_auth.yaml
kubectl apply -f apigw/ambassador/jwt_auth.yaml
```
