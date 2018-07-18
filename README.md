# Prometheus fake exporter

## How to run it
This project was created just to test K8S Horizontal Pod Autoscaler.
It exports `fake_metric` with a value fetched from http_endpoint.

Arguments required:  
- namespace
- name of the additional label 
- value of the additional label
- http endpoint serving float value like github raw gist

## HPA (Horizontal Pod Autoscaler) on Kubernetes

Below you will find code snippet with `prometheus-fake-exporter` deployment and HPA associated with that deployment scaling based on Object Deployment metric.
By replacing a value in github gist you can change HPA behaviour and see how it works for yourself.

```
---
apiVersion: extensions/v1beta1
kind: Deployment
metadata:
  name: prometheus-fake-exporter
spec:
  replicas: 1
  template:
    metadata:
      annotations:
        # Automatic prometheus scraping
        prometheus.io/port: '9100'
        prometheus.io/scrape: 'true'
        scope: cluster
      labels:
        app: prometheus-fake-exporter
    spec:
      automountServiceAccountToken: false
      containers:
      - image: 3h4x/prometheus-fake-exporter:latest
        name: prometheus-fake-exporter
        ports:
        - containerPort: 9100
        env:
        - name: LABEL_NAME
          value: deployment
        - name: LABEL_VALUE
          value: prometheus-fake-exporter
        - name: VALUE_HTTP_ENDPOINT
          value: whttps://gist.githubusercontent.com/3h4x/38ba057db9cbb80c7bf8ad768a90d086/raw/value
        - name: POD_NAMESPACE
          valueFrom:	
            fieldRef:	
              fieldPath: metadata.namespace
---
apiVersion: autoscaling/v2beta1
kind: HorizontalPodAutoscaler
metadata:
  name: prometheus-fake-exporter
spec:
  maxReplicas: 40
  minReplicas: 10
  scaleTargetRef:
    apiVersion: extensions/v1beta1
    kind: Deployment
    name: prometheus-fake-exporter
  metrics:
  - type: Object
    object:
      metricName: fake_metric
      target:
        kind: Deployment
        name: prometheus-fake-exporter
      targetValue: 10
```
