
#include <LiquidCrystal.h>
#include <Stepper.h>

// LCD : RS, E, D4, D5, D6, D7
LiquidCrystal lcd(12, 11, 5, 4, 3, 2);

// Moteur 28BYJ-48 + ULN2003
const int stepsPerRevolution = 2048;
Stepper motor(stepsPerRevolution, 8, 10, 9, 13);

// Entrees
const int potPin = A3;
const int buttonManual = A0;
const int buttonAuto = A1;
const int buttonStop = A2;

enum Mode { MANUAL, AUTOMATIC, STOP };
Mode mode = STOP;

const int buttonPins[] = {A0, A1, A2};
int lastReading[] = {HIGH, HIGH, HIGH};
int stableState[] = {HIGH, HIGH, HIGH};
unsigned long lastChange[] = {0, 0, 0};

unsigned long lastDisplay = 0;
unsigned long lastSerialData = 0;

long autoSteps = 0;
int autoDirection = 1;
int currentRPM = 5;

void setup() {
  pinMode(buttonManual, INPUT_PULLUP);
  pinMode(buttonAuto, INPUT_PULLUP);
  pinMode(buttonStop, INPUT_PULLUP);

  lcd.begin(16, 2);

  lcd.setCursor(0, 0);
  lcd.print("Smart Controller");
  lcd.setCursor(0, 1);
  lcd.print("Initializing...");

  motor.setSpeed(5);
  Serial.begin(9600);

  delay(1000);
  lcd.clear();
}

void readButtons() {
  for (int i = 0; i < 3; i++) {
    int reading = digitalRead(buttonPins[i]);

    if (reading != lastReading[i]) {
      lastChange[i] = millis();
      lastReading[i] = reading;
    }

    if (millis() - lastChange[i] > 35) {
      if (reading != stableState[i]) {
        stableState[i] = reading;

        if (stableState[i] == LOW) {
          if (i == 0) {
            mode = MANUAL;
            Serial.println("MANUAL");
          } else if (i == 1) {
            mode = AUTOMATIC;
            autoSteps = 0;
            autoDirection = 1;
            Serial.println("AUTOMATIC");
          } else {
            mode = STOP;
            Serial.println("STOP");
          }
        }
      }
    }
  }
}

void updateDisplay() {
  if (millis() - lastDisplay < 250) return;
  lastDisplay = millis();

  lcd.setCursor(0, 0);

  if (mode == MANUAL) {
    lcd.print("MODE: MANUAL    ");
  } else if (mode == AUTOMATIC) {
    lcd.print("MODE: AUTOMATIC ");
  } else {
    lcd.print("MODE: STOP      ");
  }

  lcd.setCursor(0, 1);

  if (mode == MANUAL) {
    lcd.print("SPD:");
    lcd.print(currentRPM);
    lcd.print(" RPM DIR:");
    lcd.print(autoDirection > 0 ? 'R' : 'L');
    lcd.print("   ");
  } else if (mode == AUTOMATIC) {
    lcd.print("SPD:6 RPM DIR:");
    lcd.print(autoDirection > 0 ? 'R' : 'L');
    lcd.print("   ");
  } else {
    lcd.print("Motor stopped   ");
  }
}

void sendSerialData() {
  if (millis() - lastSerialData < 250) return;
  lastSerialData = millis();

  if (mode == MANUAL) {
    Serial.print("DATA,MANUAL,");
    Serial.print(currentRPM);
    Serial.print(",");
    Serial.println(autoDirection > 0 ? 'R' : 'L');
  } else if (mode == AUTOMATIC) {
    Serial.print("DATA,AUTOMATIC,6,");
    Serial.println(autoDirection > 0 ? 'R' : 'L');
  } else {
    Serial.println("DATA,STOP,0,-");
  }
}

void loop() {
  readButtons();

  if (mode == MANUAL) {
    int potValue = analogRead(potPin);
    currentRPM = map(potValue, 0, 1023, 2, 12);
    motor.setSpeed(currentRPM);
    motor.step(1);
  } else if (mode == AUTOMATIC) {
    motor.setSpeed(6);
    motor.step(autoDirection);

    autoSteps++;

    if (autoSteps >= stepsPerRevolution) {
      autoSteps = 0;
      autoDirection = -autoDirection;
    }
  }

  updateDisplay();
  sendSerialData();
}
