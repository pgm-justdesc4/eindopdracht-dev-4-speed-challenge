#include <WiFiManager.h>
#include <WiFi.h>
#include <WebSocketsClient.h>
#include <SocketIOclient.h>
#include <ArduinoJson.h>
#include <HTTPClient.h>
#include <time.h>

// Pins
#define LED_STATUS_PIN 8
#define ACTION_BUTTON_PIN 9

SocketIOclient socketIO;
WiFiManager wm;

#define SERVER_HOST "eindopdracht-dev-4-speed-challenge.onrender.com"
#define SERVER_PORT 443
#define SERVER_PATH "/socket.io/?EIO=3"

// NTP instellingen
const char* ntpServer = "  ";
const long  gmtOffset_sec = 3600; 
const int   daylightOffset_sec = 3600; 

unsigned long lastKeepAlive = 0;
const unsigned long KEEPALIVE_INTERVAL = 300000; 

String getTimestamp() {
    struct tm timeinfo;
    if (!getLocalTime(&timeinfo)) {
        return "1970-01-01T00:00:00Z";
    }
    char timeStringBuff[25];
    strftime(timeStringBuff, sizeof(timeStringBuff), "%Y-%m-%dT%H:%M:%SZ", &timeinfo);
    return String(timeStringBuff);
}

void socketIOEvent(socketIOmessageType_t type, uint8_t* payload, size_t length) {
    switch (type) {
        case sIOtype_CONNECT:
            Serial.println("[SocketIO] Connected!");
            digitalWrite(LED_STATUS_PIN, LOW); 
            break;
        case sIOtype_DISCONNECT:
            Serial.println("[SocketIO] Disconnected!");
            digitalWrite(LED_STATUS_PIN, HIGH);  
            break;
        case sIOtype_ERROR:
            Serial.printf("[SocketIO] Error: %s\n", payload);
            digitalWrite(LED_STATUS_PIN, HIGH);
            break;
        default:
            break;
    }
}

void keepAlive() {
    if (WiFi.status() == WL_CONNECTED) {
        HTTPClient http;
        String url = "https://" + String(SERVER_HOST) + "/";
        http.begin(url);
        int httpCode = http.GET();
        http.end();
        lastKeepAlive = millis();
        Serial.println("[HTTP] Keep-alive sent");
    }
}

void sendButtonPress() {
    JsonDocument doc;
    JsonArray array = doc.to<JsonArray>();
    array.add("button_pressed");
    
    JsonObject data = array.add<JsonObject>();
    data["device"] = "ESP32-C3";
    data["send_at"] = getTimestamp();
    data["message"] = "start";

    String output;
    serializeJson(doc, output);
    socketIO.sendEVENT(output);
    Serial.println("[SocketIO] Sent: " + output);
}

void setup() {
    Serial.begin(115200);
    
    // Pin configuratie
    pinMode(ACTION_BUTTON_PIN, INPUT_PULLUP);
    pinMode(LED_STATUS_PIN, OUTPUT);
    
    // Make sure LED is off (active low)
    digitalWrite(LED_STATUS_PIN, HIGH); 

    wm.setConnectTimeout(10);
    wm.setConfigPortalBlocking(false);

    bool connected = wm.autoConnect("Speed Challenge | Start Pilar", "sc-sp-01");

    if (connected) {
        configTime(gmtOffset_sec, daylightOffset_sec, ntpServer);
        
        socketIO.beginSSL(SERVER_HOST, SERVER_PORT, SERVER_PATH);
        socketIO.setReconnectInterval(5000);
        socketIO.onEvent(socketIOEvent); 
        keepAlive();
    }
}

void loop() {
    bool justConnected = wm.process();

    if (justConnected) {
        configTime(gmtOffset_sec, daylightOffset_sec, ntpServer);
        socketIO.beginSSL(SERVER_HOST, SERVER_PORT, SERVER_PATH);
        socketIO.setReconnectInterval(5000);
        socketIO.onEvent(socketIOEvent);
        keepAlive();
    }

    if (WiFi.status() == WL_CONNECTED) {
        socketIO.loop();
        if (millis() - lastKeepAlive >= KEEPALIVE_INTERVAL) {
            keepAlive();
        }
    }

    // Button handling
    static bool lastState = HIGH;
    static unsigned long lastDebounce = 0;
    bool currentState = digitalRead(ACTION_BUTTON_PIN);

    if (currentState != lastState) {
        lastDebounce = millis();
        lastState = currentState;
    }

    if ((millis() - lastDebounce) > 50 && currentState == LOW) {
        if (WiFi.status() == WL_CONNECTED) {
            sendButtonPress();
        }
        delay(300); 
    }
    delay(10);
}