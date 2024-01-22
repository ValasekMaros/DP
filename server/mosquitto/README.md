# Install Mosquitto

1. Installing Mosquitto
```
docker run -d -p 1883:1883 -v /home/dp/project/mosquitto:/mosquitto --network="iot" --restart unless-stopped --name mosquitto eclipse-mosquitto
```
