# Promtail

```
docker run --name promtail -d -v /home/dp/project/promtail:/mnt/config -v /var/log:/var/log -v /home/dp/project/mosquitto/log/mosquitto.log:/var/log/mosquitto.log --network="iot" grafana/promtail -config.file=/mnt/config/promtail-config.yaml
```
