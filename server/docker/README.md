# Install Docker

1. Docker GPG key and Apt sources:
```
sudo apt-get install ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
```
```
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```
2. Install Docker:
```
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```
3. Modify user:
```
sudo usermod -aG docker $USER 
```
4. Hello World:
```
sudo docker run hello-world
```
5. Used Images
- eclipse-mosquitto: docker pull eclipse-mosquitto
- nodered/node-red:  docker pull nodered/node-red
- influxdb:          docker pull influxdb
- grafana/grafana:   docker pull grafana/grafana
