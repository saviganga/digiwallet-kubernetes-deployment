#!/bin/bash

# deploy secrets and config map
kubectl apply -f deploy/k8s/secrets.yml
kubectl apply -f deploy/k8s/configmap.yml

# deploy database services
# persistent volume(pv) specifies the amount of storage needed
# persistent volume claim makes use of the reserved pv storage
kubectl apply -f deploy/k8s/db/pv.yml
kubectl apply -f deploy/k8s/db/pvc.yml
kubectl apply -f deploy/k8s/db/deployment.yml
kubectl apply -f deploy/k8s/db/service.yml

# wait for the database 
sleep 10

# deploy the redis server
kubectl apply -f deploy/k8s/redis/deployment.yml
kubectl apply -f deploy/k8s/redis/service.yml

# deploy the auth microservice
kubectl apply -f deploy/k8s/auth/deployment.yml
kubectl apply -f deploy/k8s/auth/service.yml

# deploy the celery worker for auth microservice
kubectl apply -f deploy/k8s/celery/deployment.yml
kubectl apply -f deploy/k8s/celery/service.yml

# deploy the config microservice
kubectl apply -f deploy/k8s/config/deployment.yml
kubectl apply -f deploy/k8s/config/service.yml

# deploy the wallet microservice
kubectl apply -f deploy/k8s/wallet/deployment.yml
kubectl apply -f deploy/k8s/wallet/service.yml

