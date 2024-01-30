# Install Mosquitto

1. Installing Mosquitto for development
```
docker run -d -p 1883:1883 -v /home/dp/project/mosquitto/config:/mosquitto/config -v /home/dp/project/mosquitto/data:/mosquitto/data -v /home/dp/project/mosquitto/log:/mosquitto/log --network="iot" --restart unless-stopped --name mosquitto eclipse-mosquitto
```
