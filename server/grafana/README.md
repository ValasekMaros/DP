# Install Grafana

1. Installing Grafana
```
docker run -d -p 3000:3000 --user "$(id -u)" -v /home/dp/project/grafana:/var/lib/grafana --network="iot" --restart unless-stopped --name grafana grafana/grafana
```
