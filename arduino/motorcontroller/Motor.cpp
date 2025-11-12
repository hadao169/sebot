// Motor.cpp
#include "Motor.h"

Motor::Motor(int pin1, int pin2, int pin3, int pin4, int pin5) :
    controlPin1(pin1),
    controlPin2(pin2),
    enablePin(pin3),
    encoderPin1(pin4),
    encoderPin2(pin5),
    motorSpeed(0),
    encoderPosCount(0) {
      instanceId = instanceCount++;
    }


void Motor::begin() {
    setSpeed = 0;
    encoderSpeed = 0;

    instances[instanceId] = this;
    pinMode(controlPin1, OUTPUT);
    pinMode(controlPin2, OUTPUT);
    pinMode(enablePin, OUTPUT);
    digitalWrite(enablePin, LOW);

    pinMode(encoderPin1, INPUT);
    pinMode(encoderPin2, INPUT);

    attachInterrupt(digitalPinToInterrupt(encoderPin1), instanceId == 0 ? handleInterrupt0 : handleInterrupt1, CHANGE);
}

void Motor::run(int mode, int alive) {
  encoderSpeed = encoderPrevPosCount - encoderPosCount;
  encoderPrevPosCount = encoderPosCount;

  if(mode == 1) {
    if(alive>0) {
      PID_Control();
      motorSpeed=control_signal;
    }
    else {
      motorSpeed = 0;
    }
  }

  if(motorSpeed == 0) {
    digitalWrite(enablePin, LOW);
  }
  else {
    if(motorSpeed < 0) {
      digitalWrite(controlPin1, HIGH);
      digitalWrite(controlPin2, LOW);
    }
    else {
      digitalWrite(controlPin1, LOW);
      digitalWrite(controlPin2, HIGH);
    }
    analogWrite(enablePin, abs(motorSpeed));
  } 
}

void Motor::setPID(float p, float i, float d) {
  Kp2=p;
  Ki2=i;
  Kd2=d;
}

void Motor::zeroEncoder() {
  encoderPrevPosCount = 0;
  encoderPosCount = 0;
}

void Motor::setPWM(int pwm) {
  motorSpeed=pwm;
}

void Motor::setSPD(int speed) {
  setSpeed=speed;
}

int Motor::getEncoder() {
  return encoderPosCount;
}

int Motor::getSpeed() {
  return encoderSpeed;
}

int Motor::getMotorSpeed() {
  return motorSpeed;
}

void Motor::updateEncoderInstance() {
  clk = digitalRead(encoderPin1);
  dir = digitalRead(encoderPin2);
  encoderPosCount+=clk==dir?-1:1;
}
static void Motor::handleInterrupt0() {
  if(instances[0]) {
    instances[0]->updateEncoderInstance();
  }
}

static void Motor::handleInterrupt1() {
  if(instances[1]) {
    instances[1]->updateEncoderInstance();
  }
}

void Motor::PID_Control(){
  double error = setSpeed - encoderSpeed;

  if(error == 0) {
    total_error += total_error>0?-1:1;
  }
  else {
    total_error += error; //accumalates the error - integral term
  }
  
  if (total_error >= max_control/T/Ki2) total_error = max_control/T/Ki2;
  else if (total_error <= min_control/T/Ki2) total_error = min_control/T/Ki2;

  double delta_error = error - last_error; //difference of error for derivative term

  control_signal = Kp2*error + (Ki2*T)*total_error + (Kd2/T)*delta_error; //PID control compute
  if (control_signal >= max_control) control_signal = max_control;
  else if (control_signal <= min_control) control_signal = min_control;

  last_error = error;
}
