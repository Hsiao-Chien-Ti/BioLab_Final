#include <SoftwareSerial.h>
SoftwareSerial BTSerial(8, 9);
int adc[4]={A0,A1,A2,A3};
byte val=0;
unsigned long cTime = 0;
bool start;
void setup()
{
  BTSerial.begin(115200);
  Serial.begin(9600);
  pinMode(adc[0], INPUT);
  pinMode(adc[1], INPUT);
  pinMode(adc[2], INPUT);
  pinMode(adc[3], INPUT);
  start=false;
}

void loop()
{
  // tone(6, 400);
  if(BTSerial.available())
  {
    if(BTSerial.read()=='s')
    {
      start=true;
      cTime=micros();
    }
    if(BTSerial.read()=='e')
    {
      start=false;
    }
  }
  if (start&&cTime - micros() >= 1000)
  {
    cTime=micros();
    for(int i=0;i<4;i++)
    {
      val = map(analogRead(adc[i]), 0, 1023, 0, 255);
      // delayMicroseconds(200);
      BTSerial.write(val);
    }
  }
}
