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
#define BUTTON_LED_PIN 10 

// LED States
enum LedState { LED_OFF, LED_ON, LED_PULSE };
LedState currentLedState = LED_OFF; // Bij opstarten uit

SocketIOclient socketIO;
WiFiManager wm;

#define SERVER_HOST "eindopdracht-dev-4-speed-challenge.onrender.com"
#define SERVER_PORT 443
#define SERVER_PATH "/socket.io/?EIO=3"

// NTP instellingen
const char* ntpServer = "pool.ntp.org";
const long  gmtOffset_sec = 3600; 
const int   daylightOffset_sec = 3600; 

unsigned long lastKeepAlive = 0;
const unsigned long KEEPALIVE_INTERVAL = 300000; 

bool isButtonEnabled = false;

// Functie om de modus te zetten
void set_btn_led_mode(LedState state) {
    currentLedState = state;
    
    switch (state) {
        case LED_OFF:
            isButtonEnabled = false;
            analogWrite(BUTTON_LED_PIN, 255); // Uit (Active Low)
            break;
        case LED_ON:
            isButtonEnabled = true;           // Klikbaar als hij aan staat
            analogWrite(BUTTON_LED_PIN, 0);   // Aan (Active Low)
            break;
        case LED_PULSE:
            isButtonEnabled = false;          // Niet klikbaar tijdens pulseren
            break;
    }
}

// Update de pulseer-animatie zonder de code te blokkeren
void updateLedPulse() {
    if (currentLedState == LED_PULSE) {
        float speed = 0.005; 
        int brightness = (sin(millis() * speed) * 127) + 128;
        analogWrite(BUTTON_LED_PIN, 255 - brightness); // Active Low correctie
    }
}

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

        case sIOtype_EVENT: {
            String msg = (char*)payload;
            // Zodra ready ontvangen -> LED vast AAN en knop ENABLED
            if (msg.indexOf("[end-pilar]-device-ready") != -1) {
                Serial.println("[SocketIO] Ready signal! LED ON.");
                set_btn_led_mode(LED_ON);
            }
            break;
        }

        case sIOtype_DISCONNECT:
            Serial.println("[SocketIO] Disconnected!");
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
        http.GET();
        http.end();
        lastKeepAlive = millis();
    }
}

void sendButtonPress() {
    // Zodra geklikt -> LED gaat PULSEREN en knop gaat op DISABLED
    set_btn_led_mode(LED_PULSE);

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
    Serial.println("[SocketIO] Sent button press, status to PULSE");
}

void setup() {
    Serial.begin(115200);
    
    pinMode(ACTION_BUTTON_PIN, INPUT_PULLUP);
    pinMode(LED_STATUS_PIN, OUTPUT);
    pinMode(BUTTON_LED_PIN, OUTPUT);
    
    digitalWrite(LED_STATUS_PIN, HIGH); 
    
    // 1. Bij opstarten: UIT
    set_btn_led_mode(LED_OFF);

    wm.setConnectTimeout(10);
    wm.setConfigPortalBlocking(false);
    wm.autoConnect("Speed Challenge | Start Pilar", "sc-sp-01");

    configTime(gmtOffset_sec, daylightOffset_sec, ntpServer);
    socketIO.beginSSL(SERVER_HOST, SERVER_PORT, SERVER_PATH);
    socketIO.onEvent(socketIOEvent); 
}

void loop() {
    wm.process();

    if (WiFi.status() == WL_CONNECTED) {
        socketIO.loop();
        if (millis() - lastKeepAlive >= KEEPALIVE_INTERVAL) {
            keepAlive();
        }
    }

    // Altijd de puls checken (doet alleen iets in state LED_PULSE)
    updateLedPulse();

    // Button handling
    static bool lastState = HIGH;
    static unsigned long lastDebounce = 0;
    bool currentState = digitalRead(ACTION_BUTTON_PIN);

    if (currentState != lastState) {
        lastDebounce = millis();
        lastState = currentState;
    }

    // Alleen actie als de knop 'Enabled' is (dus als de state LED_ON is)
    if ((millis() - lastDebounce) > 50 && currentState == LOW && isButtonEnabled) {
        if (WiFi.status() == WL_CONNECTED) {
            sendButtonPress();
        }
        while(digitalRead(ACTION_BUTTON_PIN) == LOW) {
            updateLedPulse(); // Blijf pulseren terwijl je de knop vasthoudt
            delay(10);
        }
    }
    delay(1);
}