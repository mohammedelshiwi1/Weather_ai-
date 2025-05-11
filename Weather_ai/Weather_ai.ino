#include <Wire.h>
#include <BH1750.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BMP280.h>
#include <LiquidCrystal_I2C.h>
#include <DHT11.h>
#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>
#include <WiFiClient.h>

/*
  ESP8266 IoT Weather Station with Web Server
  
  Features:
  - Web server provides JSON API for Django integration
  - Continuous display of current weather data on LCD first line
  - Static IP display on LCD second line
  - All requested sensor data available via HTTP
*/

// ─── Configuration ─────────────────────────────────────
#define SDA_PIN        D2
#define SCL_PIN        D1
#define DHT11_PIN      D4
#define RAIN_PIN       A0
#define LCD_ADDR       0x27
#define BH1750_ADDR    0x23
#define BMP280_ADDR    0x76

// WiFi credentials
const char* ssid = "yoyo";
const char* password = "01501908507m";

// Lux thresholds
#define LUX_NIGHT_TH         50
#define LUX_EARLY_MORN_TH    300
#define LUX_MORNING_TH       1000
#define LUX_AFTERNOON_TH     10000
#define RAIN_THRESHOLD       500

// ─── Global Variables ─────────────────────────────────
float max_temp = 0;
float min_temp = 100;
int max_feel_like = 0;
int min_feel_like = 100;
float current_realTemp = 0;
int current_humidity = 0;
String current_timePeriod = "";
String current_rainStatus = "";
float current_pressure = 0;
uint16_t current_lux = 0;

// Sensor objects
BH1750 lightMeter(BH1750_ADDR);
Adafruit_BMP280 bmp;
LiquidCrystal_I2C lcd(LCD_ADDR, 16, 2);
DHT11 dht11(DHT11_PIN);

// Web server
ESP8266WebServer server(80);

// ─── Helper Functions ──────────────────────────────────

String getTimePeriod(uint16_t lux) {
  if (lux < LUX_NIGHT_TH)         return "Night";
  else if (lux < LUX_EARLY_MORN_TH) return "Early Morn";
  else if (lux < LUX_MORNING_TH)    return "Morning";
  else if (lux < LUX_AFTERNOON_TH)  return "Afternoon";
  else                              return "Evening";
}

String getRainStatus() {
  int rainValue = analogRead(RAIN_PIN);
  return (rainValue < RAIN_THRESHOLD) ? "Rain" : "Dry";
}

void updateSensorData() {
  // Read all sensor data
  uint16_t lux = lightMeter.readLightLevel();
  current_lux = lux;

  current_realTemp = bmp.readTemperature();
  float feelsLikeC = 0.95*current_realTemp;
  current_humidity = dht11.readHumidity();
  current_pressure = bmp.readPressure() / 100000.0F;
  
  // Update time period and rain status
  current_timePeriod = getTimePeriod(lux);
  current_rainStatus = getRainStatus();
  
  // Update min/max values
  if (current_realTemp > max_temp) max_temp = current_realTemp;
  if (current_realTemp < min_temp) min_temp = current_realTemp;
  if (feelsLikeC > max_feel_like) max_feel_like = feelsLikeC;
  if (feelsLikeC < min_feel_like) min_feel_like = feelsLikeC;
}

void updateLCD() {
  // First line: Current weather data (scroll through different parameters)
  static unsigned long lastUpdate = 0;
  static int displayState = 0;
  
  if (millis() - lastUpdate > 3000) { // Change every 3 seconds
    lastUpdate = millis();
    displayState = (displayState + 1) % 7;
    
    lcd.setCursor(0, 0);
    lcd.print("                "); // Clear line
    
    switch(displayState) {
      case 0:
        lcd.setCursor(0, 0);
        lcd.print("T:");
        lcd.print(current_realTemp, 1);
        lcd.print((char)223);
        break;
      case 1:
        lcd.setCursor(0, 0);
        lcd.print("Rain:");
        lcd.print(current_rainStatus);
        break;
      case 2:
        lcd.setCursor(0, 0);
        lcd.print("P:");
        lcd.print(current_pressure, 3);
        lcd.print("bar");
        break;
      case 3:
        lcd.setCursor(0, 0);
        lcd.print("Min:");
        lcd.print(min_temp, 1);
        lcd.print((char)223);
        break;
      case 4:
        lcd.setCursor(0, 0);
        lcd.print("Max:");
        lcd.print(max_temp, 1);
        lcd.print((char)223);
        break; 
      case 5:
        lcd.setCursor(0, 0);
        lcd.print("H:");
        lcd.print(current_humidity);
        lcd.print("%"); 
        break;
      case 6:
        lcd.setCursor(0, 0);
        lcd.print(current_timePeriod);
        break;
    }
  }
  
  // Second line: Static IP display
  lcd.setCursor(0, 1);
  lcd.print("IP:");
  lcd.print(WiFi.localIP());
}

// ─── Web Server Handlers ───────────────────────────────

void handleRoot() {
  String json;
  json.reserve(350);  // حجز مسبق للذاكرة لتقليل التهنيج

  json = "{";
  json += "\"min_feel_like\":" + String(min_feel_like) + ",";
  json += "\"max_feel_like\":" + String(max_feel_like) + ",";
  json += "\"min_temp\":" + String(min_temp, 2) + ",";
  json += "\"max_temp\":" + String(max_temp, 2) + ",";
  json += "\"humidity\":" + String(current_humidity) + ",";
  json += "\"time_period\":\"" + current_timePeriod + "\",";
  json += "\"realTempC\":" + String(current_realTemp, 2) + ",";
  json += "\"rain_status\":\"" + current_rainStatus + "\",";
  json += "\"pressure\":" + String(current_pressure, 3) + ",";
  json += "\"lux\":" + String(current_lux);
  json += "}";
  
  server.send(200, "application/json", json);
}

void handleNotFound() {
  server.send(404, "text/plain", "Not Found");
}

// ─── Setup ────────────────────────────────────────────

void setup() {
  // Initialize serial
  Serial.begin(115200);
  
  // Initialize I2C and sensors
  Wire.begin(SDA_PIN, SCL_PIN);
  lightMeter.begin();
  bmp.begin(BMP280_ADDR);
  
  // Initialize LCD
  lcd.init();
  lcd.backlight();
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Initializing...");
  
  // Connect to WiFi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    lcd.setCursor(0, 1);
    lcd.print("Connecting...");
  }
  
  // Set up web server
  server.on("/", handleRoot);
  server.onNotFound(handleNotFound);
  server.begin();
  
  // Display initial info
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Weather Station");
  lcd.setCursor(0, 1);
  lcd.print("IP:");
  lcd.print(WiFi.localIP());
  delay(2000);
}

// ─── Main Loop ────────────────────────────────────────

void loop() {
  // Update sensor data
  updateSensorData();
  
  // Update LCD display
  updateLCD();
  
  // Handle web server requests
  server.handleClient();
  
  // Small delay to prevent flickering
  delay(300);
yield();     

}