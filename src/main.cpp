/*
	Pyduino MIDI Drums

	An arduino MIDI drum project that is configurable with python.
  This is primarily benchmarked to communicate with the raspberry pi.
  This program assumes the Arduino Nano is used, with 8 analog inputs.
  If other boards are used, you can set the size of the program variables'
  arrays to be equal to how many analog inputs the board can take.

	The circuit:
	* piezo sensors to input drum signals
	* serial communication to the raspberry pi.

	Created 04/03/2017
	By Daryl Pongcol

*/

#include "Arduino.h"

#define NUM_PIEZOS 6 //nano can be 8, mega can be 16

// Initialize serial comm values 
unsigned long BAUD_RATE=31250;
unsigned long TIME_OUT=1000;

// Initialize config arrays, their default values are 
// set in the next block
char drumPadArray[] = {'SNARE', 'LTOM', 'RTOM', 'LCYM', 'RCYM', 'KICK'};
unsigned short ledPinsArray[NUM_PIEZOS] = {0, 1, 2, 3, 4, 5};
unsigned short piezoPinsArray[NUM_PIEZOS] = {3, 5, 6, 9, 10, 11};

void setup(){
  Serial.begin(BAUD_RATE);

  while (!Serial) {
    ; // wait for serial port to connect. Needed for native USB
  }
  
  for(short i=0; i<NUM_PIEZOS; ++i){
    pinMode(piezoPinsArray[i], INPUT);
    pinMode(ledPinsArray[i], OUTPUT);
  }
}

void loop(){  
  unsigned short piezoPin, piezoVal;
  String strPiezoPin, strPiezoVal, strSerialMsg="";

  for(short i=0; i<NUM_PIEZOS; ++i) {
    piezoPin = piezoPinsArray[i];
    piezoVal = analogRead(piezoPin);
    strPiezoPin = String(piezoPin);
    strPiezoVal = String(piezoVal);
    if (strSerialMsg == "") {
      strSerialMsg = strPiezoPin + ":" + strPiezoVal;
    } else {
      strSerialMsg = strSerialMsg + "," strPiezoPin + ":" + strPiezoVal;
    }
  }
  Serial.println(strSerialMsg);
  delay(10);
}