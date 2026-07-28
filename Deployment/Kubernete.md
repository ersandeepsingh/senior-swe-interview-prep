# Kubernetes Commands — Quick Reference

A **Kubernetes YAML file** describes how to deploy and manage containers at scale. Below you'll find frequently used `kubectl` commands, followed by a sample Deployment YAML.

---

## Basic kubectl Commands


| Command                                        | Description                                           |
| ---------------------------------------------- | ----------------------------------------------------- |
| `kubectl get pods`                             | List all pods                                         |
| `kubectl get deployments`                      | List all deployments                                  |
| `kubectl get services`                         | List all services                                     |
| `kubectl describe pod <pod-name>`              | Show detailed info about a pod                        |
| `kubectl logs <pod-name>`                      | Show logs of a pod                                    |
| `kubectl apply -f <file.yaml>`                 | Create/update resources from YAML file                |
| `kubectl delete -f <file.yaml>`                | Delete resources described in YAML file               |
| `kubectl exec -it <pod-name> -- bash`          | Start a shell in a running pod (if bash is installed) |
| `kubectl port-forward svc/<svc-name> 8080:80`  | Forward local port 8080 to service port 80            |
| `kubectl scale deployment <name> --replicas=3` | Scale deployment to 3 pods                            |
| `kubectl rollout restart deployment/<name>`    | Restart all pods in the deployment                    |


---



## Sample Kubernetes Deployment YAML

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
spec:
  replicas: 2
  selector:
    matchLabels:
      app: my-app
  template:
    metadata:
      labels:
        app: my-app
    spec:
      containers:
        - name: my-app
          image: myuser/my-app:latest
          ports:
            - containerPort: 8080
          env:
            - name: ENVIRONMENT
              value: production
```

To expose this deployment via a Kubernetes service:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-app-service
spec:
  type: ClusterIP  # or LoadBalancer for external access (cloud)
  selector:
    app: my-app
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8080
```

---

**How to use:**

1. Deploy the app:
  ```sh
   kubectl apply -f deployment.yaml
   kubectl apply -f service.yaml
  ```
2. Check status:
  ```sh
   kubectl get pods
   kubectl get svc
  ```
3. Delete:
  ```sh
   kubectl delete -f deployment.yaml
   kubectl delete -f service.yaml
  ```

---

