/*
	Pyduino MIDI Drums

	An arduino MIDI drum project that is configurable with python.
    ------ more descriptions -------

	The circuit:
	* piezo sensors to input drum signals
	* serial communication to the raspberry pi.

	Created 25/03/2017
	Revised by Daryl Pongcol

    Resources:
        Main algorithm -  By Evan Kale
        Another algorithm -  By NotesAndVolts.com

*/

#include "Arduino.h"

//Piezo defines
#define NUM_PIEZOS 6
#define START_SLOT 0     //first analog slot of piezos

//Pad defines
// pads:
#define PAD0 0    //top left
#define PAD1 1    //top right
#define PAD2 2    //middle left
#define PAD3 3    //middle right
#define PAD4 4    //lower left
#define PAD5 5    //lower right
// thresholds:
#define PAD0_THRESHOLD 25    
#define PAD1_THRESHOLD 25
#define PAD2_THRESHOLD 20
#define PAD3_THRESHOLD 40
#define PAD4_THRESHOLD 20
#define PAD5_THRESHOLD 20
// min readings:
#define PAD0_MIN 10   
#define PAD1_MIN 10
#define PAD2_MIN 0
#define PAD3_MIN 10
#define PAD4_MIN 0
#define PAD5_MIN 0
// max readings:
#define PAD0_MAX 1024   
#define PAD1_MAX 1024
#define PAD2_MAX 900
#define PAD3_MAX 400
#define PAD4_MAX 800
#define PAD5_MAX 800

// special pads:
#define KICK_PAD 2
#define LTOM_PAD 3
#define CYM_PAD 6
#define SNARE1_PAD 0
#define SNARE2_PAD 1 

//MIDI defines
#define NOTE_ON_CMD 1
#define NOTE_OFF_CMD 0
#define MAX_MIDI_VELOCITY 127
#define DEFAULT_MIN_READING 0
#define DEFAULT_MAX_READING 1024

//MIDI baud rate
#define SERIAL_RATE 115200

//Program defines
//ALL TIME MEASURED IN MILLISECONDS
#define SIGNAL_BUFFER_SIZE 100
#define PEAK_BUFFER_SIZE 30
#define MAX_TIME_BETWEEN_PEAKS 20
#define MIN_TIME_BETWEEN_NOTES 50

//map that holds the mux slots of the piezos
unsigned short slotMap[NUM_PIEZOS];

//map that holds the respective pad to each piezo
unsigned short padMap[NUM_PIEZOS];

//map that holds the respective threshold to each piezo
unsigned short thresholdMap[NUM_PIEZOS];

//map that holds the respective min & max reading to each piezo
unsigned short minReadingMap[NUM_PIEZOS];
unsigned short maxReadingMap[NUM_PIEZOS];

//Ring buffers to store analog signal and peaks
short currentSignalIndex[NUM_PIEZOS];
short currentPeakIndex[NUM_PIEZOS];
unsigned short signalBuffer[NUM_PIEZOS][SIGNAL_BUFFER_SIZE];
unsigned short peakBuffer[NUM_PIEZOS][PEAK_BUFFER_SIZE];

boolean padReady[NUM_PIEZOS];
unsigned short padReadyVelocity[NUM_PIEZOS];
boolean isLastPeakZeroed[NUM_PIEZOS];

unsigned long lastPeakTime[NUM_PIEZOS];
unsigned long lastNoteTime[NUM_PIEZOS];

void midiNoteOn(byte pad, byte midiVelocity)
{
    String strNoteOnCmd = String(NOTE_ON_CMD);  
    String strPad = String(pad);  
    String strVelocity = String(midiVelocity);
    Serial.println(strNoteOnCmd + "." + strPad + "." + strVelocity);
}

void midiNoteOff(byte pad, byte midiVelocity)
{
    String strNoteOffCmd = String(NOTE_OFF_CMD);  
    String strPad = String(pad);  
    String strVelocity = String(midiVelocity);
    Serial.println(strNoteOffCmd + "." + strPad + "." + strVelocity);
}

void padFire(unsigned short pad, unsigned short velocity)
{
  if(velocity > MAX_MIDI_VELOCITY)
    velocity = MAX_MIDI_VELOCITY;
  
  midiNoteOn(pad, velocity);
  midiNoteOff(pad, velocity);
}

void recordNewPeak(short slot, short newPeak)
{
  isLastPeakZeroed[slot] = (newPeak == 0);
  
  unsigned long currentTime = millis();
  lastPeakTime[slot] = currentTime;
  
  //new peak recorded (newPeak)
  peakBuffer[slot][currentPeakIndex[slot]] = newPeak;
  
  //1 of 3 cases can happen:
  // 1) pad ready - if new peak >= previous peak
  // 2) pad fire - if new peak < previous peak and previous peak was a pad ready
  // 3) no pad - if new peak < previous peak and previous peak was NOT pad ready
  
  //get previous peak
  short prevPeakIndex = currentPeakIndex[slot]-1;
  if(prevPeakIndex < 0) prevPeakIndex = PEAK_BUFFER_SIZE-1;        
  unsigned short prevPeak = peakBuffer[slot][prevPeakIndex];
   
  if(newPeak > prevPeak && (currentTime - lastNoteTime[slot])>MIN_TIME_BETWEEN_NOTES)
  {
    padReady[slot] = true;
    if(newPeak > padReadyVelocity[slot])
      padReadyVelocity[slot] = newPeak;
  }
  else if(newPeak < prevPeak && padReady[slot])
  {
    // if (slot == LTOM_PAD)
    //   padFire(padMap[slot], 2*padReadyVelocity[slot]); //tom low velocity fix
    // else
    //   padFire(padMap[slot], padReadyVelocity[slot]);
    padFire(padMap[slot], padReadyVelocity[slot]);
    padReady[slot] = false;
    padReadyVelocity[slot] = 0;
    lastNoteTime[slot] = currentTime;
  }
  
  currentPeakIndex[slot]++;
  if(currentPeakIndex[slot] == PEAK_BUFFER_SIZE) currentPeakIndex[slot] = 0;  
}

void setup()
{
  Serial.begin(SERIAL_RATE);
  
  //initialize globals
  for(short i=0; i<NUM_PIEZOS; ++i)
  {
    currentSignalIndex[i] = 0;
    currentPeakIndex[i] = 0;
    memset(signalBuffer[i],0,sizeof(signalBuffer[i]));
    memset(peakBuffer[i],0,sizeof(peakBuffer[i]));
    padReady[i] = false;
    padReadyVelocity[i] = 0;
    isLastPeakZeroed[i] = true;
    lastPeakTime[i] = 0;
    lastNoteTime[i] = 0;    
    slotMap[i] = START_SLOT + i;
  }
  
  thresholdMap[0] = PAD0_THRESHOLD;
  thresholdMap[1] = PAD1_THRESHOLD;
  thresholdMap[2] = PAD2_THRESHOLD;
  thresholdMap[3] = PAD3_THRESHOLD;
  thresholdMap[4] = PAD4_THRESHOLD;
  thresholdMap[5] = PAD5_THRESHOLD; 

  minReadingMap[0] = PAD0_MIN;
  minReadingMap[1] = PAD1_MIN;
  minReadingMap[2] = PAD2_MIN;
  minReadingMap[3] = PAD3_MIN;
  minReadingMap[4] = PAD4_MIN;
  minReadingMap[5] = PAD5_MIN; 

  maxReadingMap[0] = PAD0_MAX;
  maxReadingMap[1] = PAD1_MAX;
  maxReadingMap[2] = PAD2_MAX;
  maxReadingMap[3] = PAD3_MAX;
  maxReadingMap[4] = PAD4_MAX;
  maxReadingMap[5] = PAD5_MAX;
  
  padMap[0] = PAD0;
  padMap[1] = PAD1;
  padMap[2] = PAD2;
  padMap[3] = PAD3;
  padMap[4] = PAD4;
  padMap[5] = PAD5;  
}

void loop()
{
  unsigned long currentTime = millis();
  
  for(short i=0; i<NUM_PIEZOS; ++i)
  {
    //get a new signal from analog read
    unsigned short newSignal = analogRead(slotMap[i]);
    newSignal = map(newSignal, DEFAULT_MIN_READING, maxReadingMap[i], 0, 127);
    signalBuffer[i][currentSignalIndex[i]] = newSignal;
    //if new signal is 0
    if(newSignal < thresholdMap[i])
    {
      if(!isLastPeakZeroed[i] && (currentTime - lastPeakTime[i]) > MAX_TIME_BETWEEN_PEAKS)
      {
        recordNewPeak(i,0);
      }
      else
      {
        //get previous signal
        short prevSignalIndex = currentSignalIndex[i]-1;
        if(prevSignalIndex < 0) prevSignalIndex = SIGNAL_BUFFER_SIZE-1;        
        unsigned short prevSignal = signalBuffer[i][prevSignalIndex];
        
        unsigned short newPeak = 0;
        
        //find the wave peak if previous signal was not 0 by going
        //through previous signal values until another 0 is reached
        while(prevSignal >= thresholdMap[i])
        {
          if(signalBuffer[i][prevSignalIndex] > newPeak)
          {
            newPeak = signalBuffer[i][prevSignalIndex];        
          }
          
          //decrement previous signal index, and get previous signal
          prevSignalIndex--;
          if(prevSignalIndex < 0) prevSignalIndex = SIGNAL_BUFFER_SIZE-1;
          prevSignal = signalBuffer[i][prevSignalIndex];
        }
        
        if(newPeak > 0)
        {
          recordNewPeak(i, newPeak);
        }
      }
  
    }
        
    currentSignalIndex[i]++;
    if(currentSignalIndex[i] == SIGNAL_BUFFER_SIZE) currentSignalIndex[i] = 0;
  }
}