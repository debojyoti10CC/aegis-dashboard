
// ESP32 Sensor Simulation for Aegis Disaster Management System
// Sends JSON data over Serial to be picked up by the Python backend

#include <Arduino.h>

// Configuration
const int BAUD_RATE = 115200;
const int LED_PIN = 2; // Onboard LED

// Simulation variables
unsigned long lastTriggerTime = 0;
const long TRIGGER_INTERVAL = 15000; // Send data every 15 seconds

void setup() {
  Serial.begin(BAUD_RATE);
  pinMode(LED_PIN, OUTPUT);
  
  // Wait for serial connection
  delay(1000);
  
  Serial.println("ESP32 Sensor Module Initialized");
  Serial.println("Waiting for system connection...");
}

void loop() {
  // Check for incoming commands (optional)
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    
    if (command == "PING") {
      Serial.println("{\"status\": \"PONG\", \"device\": \"ESP32-SENS-01\"}");
    }
  }
  
  // Simulate periodic sensor reading triggers
  unsigned long currentMillis = millis();
  
  // Every 15 seconds, simulate a randomly detected event or heartbeat
  if (currentMillis - lastTriggerTime >= TRIGGER_INTERVAL) {
    lastTriggerTime = currentMillis;
    
    // Blink LED to indicate transmission
    digitalWrite(LED_PIN, HIGH);
    
    // 20% chance of detecting a disaster
    int rand = random(100);
    
    if (rand < 20) {
      // Simulate Fire Detection
      Serial.println("{\"type\": \"disaster_event\", \"sensor_type\": \"fire\", \"confidence\": 95, \"severity\": 0.8, \"location\": \"34.0522,-118.2437\"}");
    } else if (rand < 30) {
      // Simulate Flood Detection
      Serial.println("{\"type\": \"disaster_event\", \"sensor_type\": \"flood\", \"confidence\": 88, \"severity\": 0.6, \"location\": \"34.0522,-118.2437\"}");
    } else {
      // Regular Heartbeat / Status Update
      float temp = 25.0 + (random(50) / 10.0);
      float hum = 60.0 + (random(200) / 10.0);
      Serial.printf("{\"type\": \"sensor_reading\", \"temperature\": %.1f, \"humidity\": %.1f, \"status\": \"nominal\"}\n", temp, hum);
    }
    
    delay(100);
    digitalWrite(LED_PIN, LOW);
  }
  
  delay(100);
}
