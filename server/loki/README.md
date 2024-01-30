# Loki

```
docker run --name loki -d -v /home/dp/project/loki:/mnt/config --network="iot" -p 3100:3100 grafana/loki -config.file=/mnt/config/loki-config.yaml
```
