// analog-plot
// 
// Read analog values from A0 and A1 and print them to serial port.
//
// electronut.in

#include "Arduino.h"

#define NUM_PIEZOS 6

void setup(){
  // initialize serial comms
  Serial.begin(9600); 
}

void loop(){
  
  for(unsigned short i=0; i<NUM_PIEZOS; i++){
    // read piezo pin
    unsigned short piezoVal = analogRead(i);
    Serial.print(piezoVal);
    Serial.print(" ");
  }

  // wait 
  delay(5);
}