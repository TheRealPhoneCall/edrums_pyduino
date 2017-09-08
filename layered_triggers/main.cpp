/*
	Pyduino Layered Trigger Controller

	An arduino MIDI controller for the layered triggering system 
  of acoustic Cajons. It listens to the slap made by the cajon
  player, determines the frequency of the slap, then triggers 
  midi notes assigned to the frequency range of the slap.

	The circuit:
	* push buttons to trigger next and back of the slap frequency 
    map configuration. 
	* potentiometers to control the volumn of the acoustic sound
    and the layered electronic sound.

	Created 25/03/2017
	Revised by Daryl Pongcol

*/

#include "Arduino.h"

// MIDI baud rate
#define SERIAL_RATE 31250

// pitch bend
#define PBEND_PIN 0
#define PBEND_CMD 3
#define PBEND_STEP 100

// control change
#define CC_CMD 2
#define CC_NEXT_PIN 2
#define CC_NEXT_NUMBER 20
#define CC_BACK_PIN 4
#define CC_BACK_NUMBER 21

// led pins
#define RED_PIN 11
#define GREEN_PIN 6

// buffers
unsigned short oldPbendVal;
bool btnNextPadMap_isClicked = false;
bool btnBackPadMap_isClicked = false;

//Program defines
//ALL TIME MEASURED IN MILLISECONDS
#define SIGNAL_BUFFER_SIZE 100
#define PEAK_BUFFER_SIZE 30
#define MAX_TIME_BETWEEN_PEAKS 20
#define MIN_TIME_BETWEEN_NOTES 50

void midiPitchBend(byte pitchLow, byte pitchHigh)
{
    Serial.println(PBEND_CMD);
    Serial.println(pitchLow);
    Serial.println(pitchHigh);
}

void midiControlChange(byte ccNumber, byte val)
{
    Serial.println(CC_CMD);
    Serial.println(ccNumber);
    Serial.println(val);
}

void readPitchBends(){
  //get pitch bend value
  unsigned short newPbendVal = analogRead(PBEND_PIN);
  if ((newPbendVal - oldPbendVal == PBEND_STEP) || (oldPbendVal - newPbendVal == PBEND_STEP)) {
    long pitchLow, pitchHigh;
    if (newPbendVal < 512) {
      pitchLow = map(newPbendVal, 0, 511, -8192, 0);
      pitchHigh = 0;
    } else {
      pitchLow = 0;
      pitchHigh = map(newPbendVal, 512, 1023, 0, 8192);
    }
    
    midiPitchBend(pitchLow, pitchHigh);
    
    oldPbendVal = newPbendVal;
  } 
}

void readControlChanges(){
  //get control change values
  unsigned short ccNumber, ccVal;
  int btnNextPadMap = digitalRead(CC_NEXT_PIN);
  int btnBackPadMap = digitalRead(CC_BACK_PIN);

  // fire "next pad map" cc msg after button press
  if ((btnNextPadMap_isClicked) && (btnNextPadMap == LOW)){
    ccNumber = CC_NEXT_NUMBER;
    ccVal = 0;
    midiControlChange(ccNumber, ccVal);
    digitalWrite(GREEN_PIN, HIGH);
    delay(10);
    btnNextPadMap_isClicked = false;
  } else {
    if (btnNextPadMap == HIGH) btnNextPadMap_isClicked = true;
  }

  // fire "previous pad map" cc msg after button press
  if ((btnBackPadMap_isClicked) && (btnBackPadMap == HIGH)){
    ccNumber = CC_BACK_NUMBER;
    ccVal = 0;
    midiControlChange(ccNumber, ccVal);
    digitalWrite(RED_PIN, HIGH);
    delay(10);
    btnBackPadMap_isClicked = false;
  } else {
    if (btnBackPadMap == LOW) btnBackPadMap_isClicked = true;
  }  
}

void setup()
{
  Serial.begin(SERIAL_RATE);

  while (!Serial);
  
  //initialize globals
  pinMode(CC_BACK_PIN, INPUT);
  pinMode(CC_NEXT_PIN, INPUT);
  pinMode(PBEND_PIN, INPUT);
  pinMode(RED_PIN, OUTPUT);
  pinMode(GREEN_PIN, OUTPUT);
}

void loop()
{  
  readPitchBends();
  readControlChanges();  
}