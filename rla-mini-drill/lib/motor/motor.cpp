#include "Arduino.h"

#define ENABLE 11
#define DIRA 6
#define DIRB 7

void setup() {
    pinMode(ENABLE, OUTPUT);
    pinMode(DIRA, OUTPUT);
    pinMode(DIRB, OUTPUT);
    Serial.begin(9600);
}

void loop() {
    // Turn half speed 1 way for 3 seconds
    Serial.println("Turning halfspeed one way");
    analogWrite(ENABLE, 200);
    digitalWrite(DIRA, HIGH);
    digitalWrite(DIRB, LOW);
    delay(3000);
    // Stop for 1 second
    Serial.println("Stopping for 1 second");
    digitalWrite(ENABLE, LOW);
    delay(1000);
    // Turn half speed the other way for 3 seconds
    Serial.println("Turning halfspeed the other way");
    analogWrite(ENABLE, 200);
    digitalWrite(DIRA, LOW);
    digitalWrite(DIRB, HIGH);
    delay(3000);
    // Stop for 1 second
    Serial.println("Stopping for 1 second");
    digitalWrite(ENABLE, LOW);
    delay(1000);
}