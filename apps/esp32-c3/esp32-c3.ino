#include <WiFiManager.h>
#include <WiFi.h>
#include <WebSocketsClient.h>
#include <SocketIOclient.h>
#include <ArduinoJson.h>

#define ACTION_BUTTON_PIN 8

SocketIOclient socketIO;
WiFiManager wm;

#define SERVER_HOST "eindopdracht-dev-4-speed-challenge.onrender.com"
#define SERVER_PORT 443
#define SERVER_PATH "/socket.io/?EIO=3"

void socketIOEvent(socketIOmessageType_t type, uint8_t* payload, size_t length) {
    switch (type) {
        case sIOtype_CONNECT:
            Serial.println("[SocketIO] Connected!");
            break;
        case sIOtype_DISCONNECT:
            Serial.println("[SocketIO] Disconnected!");
            break;
        case sIOtype_ERROR:
            Serial.printf("[SocketIO] Error: %s\n", payload);
            break;
        default:
            break;
    }
}

void sendButtonPress() {
    JsonDocument doc;
    JsonArray array = doc.to<JsonArray>();
    array.add("button_pressed");
    JsonObject data = array.add<JsonObject>();
    data["device"] = "ESP32-C3";

    String output;
    serializeJson(doc, output);
    socketIO.sendEVENT(output);
    Serial.println("[SocketIO] Sent: " + output);
}

void setup() {
    Serial.begin(115200);
    delay(1000);

    pinMode(ACTION_BUTTON_PIN, INPUT_PULLUP);

    wm.setConnectTimeout(10);

    // Portaal blijft altijd aan, geen timeout
    wm.setConfigPortalTimeout(0);
    wm.setConfigPortalBlocking(false);

    bool connected = wm.autoConnect("Speed Challenge | Start Pilar", "sc-sp-01");

    if (connected) {
        Serial.println("WiFi connected! IP: " + WiFi.localIP().toString());
        socketIO.beginSSL(SERVER_HOST, SERVER_PORT, SERVER_PATH);
        socketIO.setReconnectInterval(5000);
        socketIO.onEvent(socketIOEvent);
    } else {
        Serial.println("Geen WiFi — portaal actief, wachten...");
    }
}

void loop() {
    // Verwerkt portaal requests + herverbinding na netwerk wisselen
    bool justConnected = wm.process();

    if (justConnected) {
        Serial.println("Verbonden via portaal! IP: " + WiFi.localIP().toString());
        socketIO.beginSSL(SERVER_HOST, SERVER_PORT, SERVER_PATH);
        socketIO.setReconnectInterval(5000);
        socketIO.onEvent(socketIOEvent);
    }

    if (WiFi.status() == WL_CONNECTED) {
        socketIO.loop();
    }

    static bool lastState = HIGH;
    static unsigned long lastDebounce = 0;
    bool currentState = digitalRead(ACTION_BUTTON_PIN);

    if (currentState != lastState) {
        lastDebounce = millis();
        lastState = currentState;
    }

    if ((millis() - lastDebounce) > 50 && currentState == LOW) {
        if (WiFi.status() == WL_CONNECTED) {
            Serial.println("button pressed!");
            sendButtonPress();
        } else {
            Serial.println("Knop genegeerd — geen WiFi");
        }
        delay(300);
    }

    delay(10);
}