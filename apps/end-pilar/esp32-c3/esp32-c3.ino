#include <Arduino.h>
#include <WiFi.h>
#include <WiFiManager.h>
#include <WebSocketsClient.h>
#include <SocketIOclient.h>

#define LED_STATUS_PIN 8
#define SERVER_HOST "eindopdracht-dev-4-speed-challenge.onrender.com"
#define SERVER_PORT 443
#define SERVER_PATH "/socket.io/?EIO=3"

SocketIOclient socketIO;
WiFiManager wm;

void socketIOEvent(socketIOmessageType_t type, uint8_t * payload, size_t length) {
    switch(type) {
        case sIOtype_DISCONNECT:
            Serial.println("SYSTEM:DISCONNECTED");
            break;
        case sIOtype_CONNECT:
            Serial.println("SYSTEM:CONNECTED");
            socketIO.send(sIOtype_CONNECT, "/");
            break;
        case sIOtype_EVENT:
            Serial.print("DATA:");
            Serial.println((char*)payload);
            
            // LED feedback
            digitalWrite(LED_STATUS_PIN, HIGH);
            delay(10);
            digitalWrite(LED_STATUS_PIN, LOW);
            break;
    }
}

void setup() {
    Serial.begin(115200);
    pinMode(LED_STATUS_PIN, OUTPUT);

    wm.setConnectTimeout(10);
    wm.setConfigPortalBlocking(false);
    
    if (!wm.autoConnect("Speed Challenge | End Pilar", "sc-ep-01")) {
        Serial.println("Config portal running...");
    } else {
        Serial.println("WiFi connected");
    }

    // Setup Socket.IO
    socketIO.beginSSL(SERVER_HOST, SERVER_PORT, SERVER_PATH);
    socketIO.onEvent(socketIOEvent);
}

void loop() {
    wm.process();
    socketIO.loop();
}