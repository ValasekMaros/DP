# Install InfluxDB v2

1. Installing InfluxDB v2
```
docker run -d -p 8086:8086 -v /home/dp/project/influxdb:/var/lib/influxdb2 --network="iot" --restart unless-stopped --name influxdb influxdb
```
