#include "Arduino.h"

// Prototypes
void drilling();

// Constants
const int enable = 5;
const int dirA = 6;
const int dirB = 7;
int incomingByte = 0;

void setup() {
    Serial.begin(9600);

    // Motor pins
    pinMode(enable, OUTPUT);
    pinMode(dirA, OUTPUT);
    pinMode(dirB, OUTPUT);

    // LED builtin used for indicating when drilling is occuring
    pinMode(LED_BUILTIN, OUTPUT);
    digitalWrite(LED_BUILTIN, LOW);
}

void loop() {
    if (Serial.available() > 0) {
        incomingByte = Serial.read();

        if (incomingByte == '1') {
            drilling();
        }
    }
}

/**
 * Function to simulate drilling
 */
void drilling() {
    digitalWrite(LED_BUILTIN, HIGH);
    // Drill down for 3 seconds
    analogWrite(enable, 128);
    digitalWrite(dirA, HIGH);
    digitalWrite(dirB, LOW);
    delay(3000);
    // Stop for 1 second
    digitalWrite(enable, LOW);
    delay(1000);
    // Drill up for 3 seconds
    digitalWrite(enable, 128);
    digitalWrite(dirA, HIGH);
    digitalWrite(dirB, LOW);
    // Stop motor
    digitalWrite(enable, LOW);
    delay(1000);

    // Send signal back to Pi indicating drilling is finished
    Serial.write(1);
    digitalWrite(LED_BUILTIN, LOW);
}
