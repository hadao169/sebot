#include "Motor.h"

const int voltagePin = A0;         // Analog input pin
const float R1 = 9820.0;          // 10k ohms
const float R2 = 4720.0;           // 4.7k ohms
const float voltageScale = (R1 + R2) / R2; // ~3.13

Motor *Motor::instances[2] = {nullptr, nullptr};
int Motor::instanceCount = 0;

//Motor motor1(4,5,9,2,3);
Motor motor1( 6, 8, 5, 3, 4);
Motor motor2(11,12,10, 2, 9);

int mode = 0; // 0=PWM 1=SPEED
int alive = 0;
int aliveSignal = 10*3; // 3s
int printDelay = 0;

unsigned long startTime = 0;

String msg;

void setup() {
  motor1.begin();
  motor2.begin();

  Serial.begin(115200);
}

void loop() {
 if(millis()-startTime>=1) {
    startTime++;
    if(printDelay==0) {
      printDelay=100; // 100ms

      if(alive>0) {
        alive--;
      }

      if(aliveSignal == 0) { alive = 1; }

      motor1.run(mode, alive);
      motor2.run(mode, alive);

      //sendData();
    }
    printDelay--;

    readSerialPort();

    if (msg != "") {
      sendData();
    }
  }
  //delay(1); //1ms
}

void readSerialPort() {
  msg = "";
  String sa[4];
  int r=0, t=0;
  if (Serial.available()) {
    msg = Serial.readStringUntil('\n');

    for (int i=0; i < msg.length(); i++)
    { 
    if(msg.charAt(i) == ';') 
      { 
        sa[t] = msg.substring(r, i);
        r=(i+1); 
        t++; 
      }
    }
    if(sa[0] == "PWM") {
      mode = 0;
      motor1.setPWM(sa[1].toInt());
      motor2.setPWM(sa[2].toInt());
    }
    else if(sa[0] == "SPD") {
      mode = 1;
      alive = aliveSignal;
      motor1.setSPD(sa[1].toInt());
      motor2.setSPD(sa[2].toInt());
    }
    else if(sa[0] == "PID") {
      motor1.setPID(sa[1].toFloat(),sa[2].toFloat(),sa[3].toFloat());
      motor2.setPID(sa[1].toFloat(),sa[2].toFloat(),sa[3].toFloat());
    }
    else if(sa[0] == "ZERO") {
      motor1.zeroEncoder();
      motor2.zeroEncoder();
    }
    else if(sa[0] == "ALIVE") {
      aliveSignal = sa[1].toInt()*10;
    }

    Serial.flush();
  }
}

void sendData() {
  Serial.print(motor1.getEncoder());
  Serial.print(";");
  Serial.print(motor2.getEncoder());
  Serial.print(";");
  Serial.print(motor1.getSpeed());
  Serial.print(";");
  Serial.print(motor2.getSpeed());
  Serial.print(";");
  Serial.print(motor1.getMotorSpeed());
  Serial.print(";");
  Serial.print(motor2.getMotorSpeed());
  Serial.print(";");
  Serial.print(readBatteryVoltage(), 2); // Battery voltage with 2 decimals
  Serial.print("\n");
}

float readBatteryVoltage() {
  int raw = analogRead(voltagePin);            // 0–1023
  float voltage = (raw / 1023.0) * 5.0;         // Convert to voltage
  return voltage * voltageScale;               // Scale to actual battery voltage
}
