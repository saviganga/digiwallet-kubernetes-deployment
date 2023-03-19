# digiwallet-service-kubernetes

In this project, I deployed and managed three (3) django microservice applications using kubernetes

- PREREQUISITES
1. docker
2. minikube/docker-desktop
3. kubernetes enabled
4. basic knowledge of kubernetes
5. knowledge of django is a bonus

- DIRECTORY EXPLANATION
1. authService
    - django microservice to handle user authentication

2. configService
    - django microservice to handle general configurations

3. walletApp
    - django microservice to handle wallet logic

4. deploy
    - k8s: folder containing configuration files for kubernetes deployment and management
        - secrets.yml: contains base64 encrypted secrets for k8s cluster
        - configmap.yml: contains environment variables for k8s cluster
        - ingress.yml: contains imgress routing rules. Maps domain names to internal services for acess from the internet.
        - db:
            - pv.yml: persistent volume configuration file - used to reserve a specified amount of storage
            - pvc.yml: persistent volume claim configuration file - used to utilize the reserved storage in persistent volume
            - deployment.yml: deployment configuration file for postgres database
            - service.yml: service configuration file for postgres deployment - used to access the pod (internally by other pods)
        - redis:
            - deployment.yml: deployment configuration file for redis
            - service.yml: service configuration file for redis deployment - used to access the pod (internally by other pods)
        - auth:
            - deployment.yml: deployment configuration file for django auth microservice
            - service.yml: service configuration file for django auth microservice deployment - used to access the pod (internally by other pods and externally from the internet- nodePort)
        - celery:
            - deployment.yml: deployment configuration file for celery worker
            - service.yml: service configuration file for celery worker deployment - used to access the pod (internally by other pods)
        - config:
            - deployment.yml: deployment configuration file for django config microservice
            - service.yml: service configuration file for django config microservice deployment - used to access the pod (internally by other pods and externally from the internet- nodePort)
        - wallet:
            - deployment.yml: deployment configuration file for django wallet microservice
            - service.yml: service configuration file for django wallet microservice deployment - used to access the pod (internally by other pods and externally from the internet- nodePort)

- BONUS
1. start_cluster.sh
    - bash shell with commands to start the kubernetes cluster

- USAGE

1. Set up Ingress controller (Load Balancer) for your environment - https://kubernetes.github.io/ingress-nginx/deploy/#quick-start
2. Map your domain name to the Load Balancer DNS
3. Modify external services. (make them internal so they can be mapped to the ingress rule)
4. run ./start_cluster.sh script to start the cluster
5. Test access to your application using the registered domain name
6. run kubectl commands to manage the cluster

- IMPROVEMENTS
1. using variables to improve reusability