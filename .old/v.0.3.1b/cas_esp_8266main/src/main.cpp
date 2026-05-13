#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>
#include <ArduinoOTA.h>
#include "secret.h"

// Tvoje stávající zapojení
#define DS_PIN    D4  // Serial Data
#define SHCP_PIN  D1  // Clock (SRCK)
#define STCP_PIN  D0  // Latch (RCK)

ESP8266WebServer server(80);
bool debug_mode = true;
int casA = 0;
int casB = 0;

// Tabulka pro čísla 0-9 (segmenty Q1 až Q7)
// Formát: 0bGFEDCBAx (x je Q0, ten v tabulce necháváme na 0)
const uint8_t cislice[] = {
  0b01111110, // 0
  0b01000001, // 1
  0b01101101, // 2
  0b01001111, // 3
  0b00010111, // 4
  0b01011011, // 5
  0b01111011, // 6
  0b00001110, // 7
  0b11111111, // 8
  0b01011111  // 9
};

uint8_t cisliceProCislo(int cislo) {
  if (cislo < 0 || cislo > 9) {
    return 0x00;
  }
  return cislice[cislo];
}

void swSPITransfer(uint8_t hodnota) {
  for (int i = 7; i >= 0; i--) {
    digitalWrite(DS_PIN, (hodnota & (1 << i)) ? HIGH : LOW);
    digitalWrite(SHCP_PIN, HIGH);
    delayMicroseconds(2);
    digitalWrite(SHCP_PIN, LOW);
    delayMicroseconds(1);
  }
}

void aktualizujRetezec(uint8_t *data) {
  digitalWrite(STCP_PIN, LOW);
  delayMicroseconds(5);

  for (int i = 7; i >= 0; i--) {
    swSPITransfer(data[i]);
  }

  digitalWrite(STCP_PIN, HIGH);
}

void zobrazCasy(int a, int b) {
  uint8_t pole[8] = {0};

  pole[0] = 0b11111111;
  pole[1] = 0b11111111;
  pole[2] = 0b11111111;
  pole[3] = 0b11111111;

  pole[4] = 0b11111111;
  pole[5] = 0b11111111;
  pole[6] = 0b11111111;
  pole[7] = 0b11111111;

  aktualizujRetezec(pole);
}

void handleDataRequest() {
  String payload = "{\"time_a\":" + String(casA) + ",\"time_b\":" + String(casB) + "}";
  server.send(200, "application/json", payload);
}

void setup() {
  pinMode(DS_PIN, OUTPUT);
  pinMode(SHCP_PIN, OUTPUT);
  pinMode(STCP_PIN, OUTPUT);

  digitalWrite(STCP_PIN, HIGH);
  digitalWrite(SHCP_PIN, LOW);
  digitalWrite(DS_PIN, LOW);

  Serial.begin(115200);
  WiFi.softAP(wifi_ssid, wifi_password);
  delay(100);
  Serial.println();
  Serial.println("ESP8266 AP mode active");
  Serial.print("IP address: ");
  Serial.println(WiFi.softAPIP());

  server.on("/data", HTTP_GET, handleDataRequest);
  server.onNotFound([]() {
    server.send(404, "text/plain", "Not found");
  });
  server.begin();
  Serial.println("HTTP server started on /data");

  ArduinoOTA.setPassword(OTA_PASSWORD);
  ArduinoOTA.begin();
  Serial.println("OTA ready");
}

void loop() {
  server.handleClient();
  ArduinoOTA.handle();

  if (debug_mode) {
    casA = random(0, 100);
    casB = random(0, 100);
    zobrazCasy(casA, casB);
    delay(500);
  }
}
