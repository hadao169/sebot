// Motor.h
#ifndef Motor_h
#define Motor_h

#include <Arduino.h>


class Motor {
  private:
    int controlPin1;
    int controlPin2;
    int enablePin;
    int encoderPin1;
    int encoderPin2;

    int motorSpeed;
    int encoderPosCount;
    int encoderPrevPosCount;

    int setSpeed;
    int encoderSpeed;
    /*
    float speedSum;
    float speedPre;
    float kp;
    float ki;
    float kd;
    
    int speedError;
*/
    static void handleInterrupt0();
    static void handleInterrupt1();
    void updateEncoderInstance();

    int clk;
    int dir;

    double control_signal=0;
    double Kp2=0.7; //proportional gain
    double Ki2=0.003; //integral gain
    double Kd2=0.0; //derivative gain
    int T=115; //sample time in milliseconds (ms)
    //unsigned long last_time=0;
    double total_error=0, last_error=0;
    int max_control = 250;
    int min_control = -250;

  public:
    Motor(int pin1, int pin2, int pin3, int pin4, int pin5);
    static Motor *instances[2];
    static int instanceCount;     // To track number of instances
    int instanceId;      

    void run(int mode, int alive);
    void begin();
    int getEncoder();
    int getSpeed();
    int getMotorSpeed();

    void setPWM(int pwm);
    void setSPD(int speed);
    void setPID(float p, float i, float d);

    void PID_Control();
    void zeroEncoder();
};

#endif