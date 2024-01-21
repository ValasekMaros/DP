# Install Node-RED

1. Installing Node-RED
```
docker run -d -p 1880:1880 -v /home/dp/project/nodered:/data --network="iot" --restart unless-stopped --name nodered nodered/node-red
```
