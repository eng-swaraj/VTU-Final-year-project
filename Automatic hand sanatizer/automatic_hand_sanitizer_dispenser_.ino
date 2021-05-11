#include<Servo.h>
Servo s1;
float t; 
float d;
void setup () 
{
  Serial.begin(9600); 
  s1.attach(6);
  pinMode (9, OUTPUT);
  pinMode (10, INPUT);
  }

void loop ()
{
digitalWrite (9, LOW) ; 
  delayMicroseconds (10);
  digitalWrite (9, HIGH);
  delayMicroseconds (10);
  digitalWrite (9, LOW);
  t=pulseIn (10, HIGH);

d=(t*0.0343)/2;
  Serial.println (d);
  if(d<=20)
  {
   s1.write(90);
   delay(1000);
   }
  else
  {
  s1.write(0);
  delay(1000);
}
}