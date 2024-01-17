#include <esp_sleep.h>
#include <ArduinoJson.h>  //https://github.com/bblanchon/ArduinoJson
#include <DHT.h>
#include <WiFi.h>
//#include "PubSubClient.h"
#include <AsyncMQTT_ESP32.h>
#include <Adafruit_BMP085.h>

// Pins for energy power
#define DHTPOWER 13
#define BMPPOWER 19
// Pins for communication
#define DHTPIN 33

#define Time_To_Sleep_Failure 60  // Time ESP32 will go to sleep in some case of failure, like ssid not found, etc (in seconds)
#define Time_To_Sleep 300         // Time ESP32 will go to sleep in normal occasion (in seconds)
#define S_To_uS_Factor 1000000ULL

#define DHTTYPE DHT22      // Define type of DHT (DHT11, DHT22)
DHT dht(DHTPIN, DHTTYPE);  // Initialize DHT sensor

//Adafruit_BMP085 bmp;

AsyncMqttClient mqttClient;

float teplota = 0;
float vlhkost = 0;
int tlak = 0;
DynamicJsonDocument meranieTHB(256);
char buffer[256];

// WIFI
//-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
char ssid[32] = "xxx";
char password[32] = "xxx";
//-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

// MQTT
//-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
char mqtt_broker[32] = "xxx.xxx.xxx.xxx";  // Adresa Servera
char mqtt_port[8] = "1883";              // Port
char mqtt_username[32] = "xxx";
char mqtt_password[32] = "xxx";
char mqtt_topic[32] = "/Test";  // Topic
char miestnost[16] = "00";
//-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

//flag for saving data
bool shouldSaveConfig = false;
bool setupReset = false;
bool setupConfig = false;

unsigned long startProgram;
unsigned long endProgram;

unsigned long programTime;
unsigned long sleepTime;

//callback notifying us of the need to save confi

//MQTT Setup
/*
WiFiClient espClient;
PubSubClient client(espClient);
*/

//#define Time_To_Sleep_ms 285000
//#define S_To_mS_Factor 1000

//setupsetupsetupsetupsetupsetupsetupsetupsetupsetupsetupsetupsetupsetupsetupsetupsetupsetupsetupsetupsetupsetupsetupsetupsetupsetupsetupsetupsetupsetupsetupsetup
void setup() {

  startProgram = micros();  // Time when program started

  Serial.begin(115200);
  Serial.println();
  Serial.println("Starting Inicialization...");

  // Setup CPU frequency
  setCpuFrequencyMhz(80);  // (80, 160, 240)
  // Print CPU frequency to console
  Serial.print("Frekvencia CPU: ");
  Serial.println(getCpuFrequencyMhz());

  // Setup pins to diferent modes (INPUT, INPUT_PULLUP, OUTPUT)
  pinMode(DHTPOWER, OUTPUT);
  //pinMode(BMPPOWER, OUTPUT);

  // Setting OUTPIN-s to HIGH so sensors have power
  digitalWrite(DHTPOWER, HIGH);
  //digitalWrite(BMPPOWER, HIGH);

  // Start DHT and BMP
  dht.begin();
  /*while (!bmp.begin()) {
    failureRestart();
  }*/

  // Setting MQTT Broker
  int mqtt_port_temp = atoi(mqtt_port);       // Convert ASCII to int
  mqttClient.setKeepAlive(15);                // How long will be user logged in
  mqttClient.onDisconnect(onMqttDisconnect);  // What happens on MQTT disconnect
  mqttClient.onPublish(onMqttPublish);        // What happens when message is published
  mqttClient.onConnect(onMqttConnect);

  mqttClient.setCredentials(mqtt_username, mqtt_password);  // MQTT username and password
  mqttClient.setServer(mqtt_broker, mqtt_port_temp);        // MQTT Broker IP adress and port

  delay(100);
  THB_Meranie();
  saveToJSON();

  // Connecting to WiFi
  Serial.print("[WiFi] Connecting to ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);
  //delay(2000);

  while (true) {

    switch (WiFi.status()) {
      case WL_NO_SSID_AVAIL:
        Serial.println("[WiFi] SSID not found");
        restartTimer();
        break;
      case WL_CONNECT_FAILED:
        Serial.print("[WiFi] Failed - WiFi not connected!");
        failureRestart();
        return;
        break;
      case WL_CONNECTION_LOST:
        Serial.println("[WiFi] Connection was lost");
        restartTimer();
        break;
      case WL_DISCONNECTED:
        Serial.println("[WiFi] WiFi is disconnected");
        restartTimer();
        break;
      case WL_CONNECTED:
        Serial.println("[WiFi] WiFi is connected!");
        Serial.print("[WiFi] IP address: ");
        Serial.println(WiFi.localIP());
        mqttClient.connect();
        return;
        break;
      default:
        Serial.print("[WiFi] WiFi Status: ");
        Serial.println(WiFi.status());
        break;
    }
    delay(100);
    restartTimer();
  }

  Serial.println("...Ending Inicialization");
}
//setupsetupsetupsetupsetupsetupsetupsetupsetupsetupsetupsetupsetupsetupsetupsetupsetupsetupsetupsetupsetupsetupsetupsetupsetupsetupsetupsetupsetupsetupsetupsetup

//looplooplooplooplooplooplooplooplooplooplooplooplooplooplooplooplooplooplooplooplooplooplooplooplooplooplooplooplooplooplooplooplooplooplooplooplooplooplooploop
void loop() {

/*
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("WiFi Pripojene");
    mqttClient.connect();
    MQTT_Pub2();
  } else {
    Serial.println("WiFi NEpripojene");
  }
  */

  delay(500);

  restartTimer();
}
//looplooplooplooplooplooplooplooplooplooplooplooplooplooplooplooplooplooplooplooplooplooplooplooplooplooplooplooplooplooplooplooplooplooplooplooplooplooplooploop

// Measuring variables from sensors
void THB_Meranie() {

  //delay(250);
  teplota = dht.readTemperature();
  vlhkost = dht.readHumidity();
  //tlak = bmp.readPressure();
  digitalWrite(DHTPOWER, LOW);
  digitalWrite(BMPPOWER, LOW);

  Serial.print("Teplota:");
  Serial.println(teplota);
  Serial.print("Vlhkost:");
  Serial.println(vlhkost);
  Serial.print("Tlak:");
  Serial.println(tlak);
}

// Saving data to JSON
void saveToJSON() {

  meranieTHB["m"] = miestnost;
  meranieTHB["t"] = round2(teplota);
  meranieTHB["h"] = round2(vlhkost);
  meranieTHB["p"] = tlak;

  serializeJson(meranieTHB, buffer);
}

double round2(double value) {
  return (int)(value * 100 + 0.001) / 100.0;
}

void MQTT_Pub2() {

  //reconnectMQTT();
  uint16_t packetIdPub = mqttClient.publish(mqtt_topic, 2, true, buffer);
  Serial.print("Publishing at QoS 2, packetId: ");
  Serial.println(packetIdPub);
  Serial.println(buffer);
  Serial.flush();
  delay(50);
}

void onMqttConnect(bool sessionPresent) {
  Serial.print("Connected to MQTT broker: ");
  Serial.print(mqtt_broker);
  Serial.print(", port: ");
  Serial.println(mqtt_port);
  Serial.print("PubTopic: ");
  Serial.println(mqtt_topic);

  uint16_t packetIdPub = mqttClient.publish(mqtt_topic, 2, true, buffer);
  Serial.print("Publishing at QoS 2, packetId: ");
  Serial.println(packetIdPub);
  Serial.println(buffer);
  Serial.flush();
  delay(50);
}

void onMqttPublish(const uint16_t& packetId) {
  Serial.println("Publish acknowledged");
  Serial.print("  PacketId: ");
  Serial.println(packetId);

  endProgram = micros();
  programTime = endProgram - startProgram;
  sleepTime = (Time_To_Sleep * S_To_uS_Factor) - programTime;
  esp_sleep_enable_timer_wakeup(sleepTime);
  Serial.print("Cycle time: ");
  Serial.println(programTime);
  Serial.print("Sleep time: ");
  Serial.println(sleepTime);
  Serial.println("DEEP SLEEP, MQTT Posted");
  Serial.flush();
  esp_deep_sleep_start();
}

void onMqttDisconnect(AsyncMqttClientDisconnectReason reason) {
  (void)reason;

  Serial.println("Disconnected from MQTT.");
  ESP.restart();
}

void restartTimer() {
  endProgram = micros();
  programTime = endProgram - startProgram;

  if (programTime > 10000000) {
    failureRestart();
  }
}

void failureRestart() {
  esp_sleep_enable_timer_wakeup(Time_To_Sleep_Failure * S_To_uS_Factor);
  Serial.println("DEEP SLEEP, with Failure");
  Serial.flush();
  esp_deep_sleep_start();
}
