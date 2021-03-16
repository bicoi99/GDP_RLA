#include "AccelStepper.h"
#include "Arduino.h"
#include "LiquidCrystal.h"

// Prototype
void drilling();

// LCD
const int rs = 7, en = 6, d4 = 5, d5 = 4, d6 = 3, d7 = 2;
LiquidCrystal lcd(rs, en, d4, d5, d6, d7);
// Stepper
AccelStepper myStepper(4, 12, 9, 10, 8);
// DC motor
const int motorPin = 11;
// Serial communication
int incomingByte = 0;

void setup() {
    // Open serial port
    Serial.begin(9600);
    // LCD set default message on 16x2 screen
    lcd.begin(16, 2);
    lcd.print("Waiting for Pi.");
    // Indication LED turn off by default
    pinMode(LED_BUILTIN, OUTPUT);
    digitalWrite(LED_BUILTIN, LOW);
    // Initialise DC motor pin
    pinMode(motorPin, OUTPUT);
    // Stepper motor options
    myStepper.setMaxSpeed(1000.0);
    myStepper.setAcceleration(50.0);
    myStepper.setSpeed(600.0);
}

void loop() {
    // If any data is available
    if (Serial.available() > 0) {
        // Read data and start drilling if correct signal
        incomingByte = Serial.read();
        if (incomingByte == '1') {
            drilling();
        }
    }
}

void drilling() {
    // Turn on indication LED
    digitalWrite(LED_BUILTIN, HIGH);
    // Change LCD message
    lcd.clear();
    lcd.print("Drilling...");
    // Turn DC motor
    analogWrite(motorPin, 200);
    // Stepper motor forward
    myStepper.moveTo(500);
    while (myStepper.distanceToGo() != 0) {
        myStepper.run();
    }
    // Stepper motor backward
    myStepper.moveTo(-500);
    while (myStepper.distanceToGo() != 0) {
        myStepper.run();
    }
    // Stop turning DC motor
    digitalWrite(motorPin, LOW);
    // Change LCD screen
    lcd.clear();
    lcd.print("Finished!");
    lcd.setCursor(0, 1);
    lcd.print("Sent data back.");
    // Send data back Pi
    Serial.write(1);
    // Turn off indication LED
    digitalWrite(LED_BUILTIN, LOW);
    // Wait 3s and change LCD screen
    delay(3000);
    lcd.clear();
    lcd.print("Waiting for Pi.");
}