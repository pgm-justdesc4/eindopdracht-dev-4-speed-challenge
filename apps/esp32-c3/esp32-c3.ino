#include <WiFiManager.h>
#include <WiFi.h>
#include <WebSocketsClient.h>
#include <SocketIOclient.h>
#include <ArduinoJson.h>

#define ACTION_BUTTON_PIN 8

SocketIOclient socketIO;

#define SERVER_HOST "eindopdracht-dev-4-speed-challenge.onrender.com"
#define SERVER_PORT 443
#define SERVER_PATH "/socket.io/?EIO=3"

void socketIOEvent(socketIOmessageType_t type, uint8_t* payload, size_t length) {
    switch (type) {
        case sIOtype_CONNECT:
            Serial.println("[SocketIO] Connected to server!");
            break;
        case sIOtype_DISCONNECT:
            Serial.println("[SocketIO] Disconnected from server!");
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

    WiFiManager wm;
    wm.setConnectTimeout(10);
    wm.setConfigPortalTimeout(60);

    bool res = wm.autoConnect("Speed Challenge | Start Pilar", "sc-sp-01");
    if (!res) {
        Serial.println("Failed — restarting");
        delay(3000);
        ESP.restart();
    }

    Serial.println("WiFi connected! IP: " + WiFi.localIP().toString());

    // Tijdelijke TCP test
    WiFiClient client;
    if (client.connect("192.168.0.107", 3000)) {
        Serial.println("TCP connectie gelukt!");
        client.stop();
    } else {
        Serial.println("TCP connectie mislukt!");
    }

    socketIO.beginSSL(SERVER_HOST, SERVER_PORT, SERVER_PATH);
    socketIO.setReconnectInterval(5000);
    socketIO.onEvent(socketIOEvent);
}

void loop() {
    socketIO.loop();

    static bool lastState = HIGH;
    static unsigned long lastDebounce = 0;
    bool currentState = digitalRead(ACTION_BUTTON_PIN);

    if (currentState != lastState) {
        lastDebounce = millis();
        lastState = currentState;
    }

    if ((millis() - lastDebounce) > 50 && currentState == LOW) {
        Serial.println("button pressed!");
        sendButtonPress();
        delay(300);
    }

    delay(10);
}