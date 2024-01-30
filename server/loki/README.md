# Loki

```
docker run --name loki -d -v /home/dp/project/loki:/mnt/config --network="iot" -p 3100:3100 grafana/loki:2.9.4 -config.file=/mnt/config/loki-config.yaml
```
