/*
 * Copyright (c) 2015 Evan Kale
 * Email: EvanKale91@gmail.com
 * Website: www.ISeeDeadPixel.com
 *          www.evankale.blogspot.ca
 *
 * This file is part of ArduinoMidiDrums.
 *
 * ArduinoMidiDrums is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

#include "Arduino.h"

//Led Pin
const int greenPin = 9;
const int redPin = 10;

//Piezo defines
#define NUM_PIEZOS 6
#define SNARE_THRESHOLD 30     //anything < TRIGGER_THRESHOLD is treated as 0
#define LTOM_THRESHOLD 30
#define RTOM_THRESHOLD 30
#define LCYM_THRESHOLD 100
#define RCYM_THRESHOLD 100
#define KICK_THRESHOLD 50
#define START_SLOT 0     //first analog slot of piezos

//MIDI note defines for each trigger
#define SNARE_NOTE 70
#define LTOM_NOTE 71
#define RTOM_NOTE 72
#define LCYM_NOTE 73
#define RCYM_NOTE 74
#define KICK_NOTE 75

//MIDI defines
#define NOTE_ON_CMD 0x90
#define NOTE_OFF_CMD 0x80
#define MAX_MIDI_VELOCITY 127

//MIDI baud rate
#define SERIAL_RATE 9600

//Program defines
//ALL TIME MEASURED IN MILLISECONDS
#define SIGNAL_BUFFER_SIZE 100
#define PEAK_BUFFER_SIZE 30
#define MAX_TIME_BETWEEN_PEAKS 20
#define MIN_TIME_BETWEEN_NOTES 50

//map that holds the mux slots of the piezos
unsigned short slotMap[NUM_PIEZOS];

//map that holds the respective note to each piezo
unsigned short noteMap[NUM_PIEZOS];

//map that holds the respective threshold to each piezo
unsigned short thresholdMap[NUM_PIEZOS];

//Ring buffers to store analog signal and peaks
short signalIndexArray[NUM_PIEZOS];
short peakIndexArray[NUM_PIEZOS];
unsigned short signalBuffer[NUM_PIEZOS][SIGNAL_BUFFER_SIZE];
unsigned short peakBuffer[NUM_PIEZOS][PEAK_BUFFER_SIZE];

boolean noteReadyArray[NUM_PIEZOS];
unsigned short noteReadyVelocityArray[NUM_PIEZOS];
boolean isLastPeakZeroedArray[NUM_PIEZOS];

unsigned long lastPeakTimeArray[NUM_PIEZOS];
unsigned long lastNoteTimeArray[NUM_PIEZOS];

void midiNoteOn(byte note, byte midiVelocity)
{
  String strNoteOnCmd = String(NOTE_ON_CMD);
  Serial.println(strNoteOnCmd);
  String strNote = String(note);
  Serial.println(strNote);
  String strVelocity = String(midiVelocity);
  Serial.println(strVelocity);
}

void midiNoteOff(byte note, byte midiVelocity)
{
  String strNoteOnCmd = String(NOTE_OFF_CMD);
  Serial.println(String(NOTE_OFF_CMD));
  String strNote = String(note);
  Serial.println(strNote);
  String strVelocity = String(midiVelocity);
  Serial.println(strVelocity);
}

void noteFire(unsigned short note, unsigned short velocity)
{
  if(velocity > MAX_MIDI_VELOCITY)
    velocity = MAX_MIDI_VELOCITY;
  
  midiNoteOn(note, velocity);
  midiNoteOff(note, velocity);

  analogWrite(greenPin, val);
}

void recordNewPeak(short slot, short newPeak)
{
  isLastPeakZeroedArray[slot] = (newPeak == 0);
  
  unsigned long currentTime = millis();
  lastPeakTimeArray[slot] = currentTime;
  
  //new peak recorded (newPeak)
  peakBuffer[slot][peakIndexArray[slot]] = newPeak;
  
  //1 of 3 cases can happen:
  // 1) note ready - if new peak >= previous peak
  // 2) note fire - if new peak < previous peak and previous peak was a note ready
  // 3) no note - if new peak < previous peak and previous peak was NOT note ready
  
  //get previous peak
  short prevPeakIndex = peakIndexArray[slot]-1;
  if(prevPeakIndex < 0) prevPeakIndex = PEAK_BUFFER_SIZE-1;        
  unsigned short prevPeak = peakBuffer[slot][prevPeakIndex];
   
  if(newPeak > prevPeak && (currentTime - lastNoteTimeArray[slot])>MIN_TIME_BETWEEN_NOTES)
  {
    noteReadyArray[slot] = true;
    if(newPeak > noteReadyVelocityArray[slot])
      noteReadyVelocityArray[slot] = newPeak;
  }
  else if(newPeak < prevPeak && noteReadyArray[slot])
  {
    noteFire(noteMap[slot], noteReadyVelocityArray[slot]);
    noteReadyArray[slot] = false;
    noteReadyVelocityArray[slot] = 0;
    lastNoteTimeArray[slot] = currentTime;
  }
  
  peakIndexArray[slot]++;
  if(peakIndexArray[slot] == PEAK_BUFFER_SIZE) peakIndexArray[slot] = 0;  
}

void setup()
{
  Serial.begin(SERIAL_RATE);
  
  //initialize globals
  for(short i=0; i<NUM_PIEZOS; ++i)
  {
    signalIndexArray[i] = 0;
    peakIndexArray[i] = 0;
    memset(signalBuffer[i],0,sizeof(signalBuffer[i]));
    memset(peakBuffer[i],0,sizeof(peakBuffer[i]));
    noteReadyArray[i] = false;
    noteReadyVelocityArray[i] = 0;
    isLastPeakZeroedArray[i] = true;
    lastPeakTimeArray[i] = 0;
    lastNoteTimeArray[i] = 0;    
    slotMap[i] = START_SLOT + i;
  }
  
  thresholdMap[0] = KICK_THRESHOLD;
  thresholdMap[1] = RTOM_THRESHOLD;
  thresholdMap[2] = RCYM_THRESHOLD;
  thresholdMap[3] = LCYM_THRESHOLD;
  thresholdMap[4] = SNARE_THRESHOLD;
  thresholdMap[5] = LTOM_THRESHOLD;  
  
  noteMap[0] = KICK_NOTE;
  noteMap[1] = RTOM_NOTE;
  noteMap[2] = RCYM_NOTE;
  noteMap[3] = LCYM_NOTE;
  noteMap[4] = SNARE_NOTE;
  noteMap[5] = LTOM_NOTE;  

  pinMode(greenPin, OUTPUT);
  pinMode(redPin, OUTPUT);
}

void loop()
{
  unsigned long currentTime = millis();
  
  for(short i=0; i<NUM_PIEZOS; ++i)
  {
    //get a new signal from analog read
    unsigned short newSignal = analogRead(slotMap[i]);
    signalBuffer[i][signalIndexArray[i]] = newSignal;
    
    //if new signal is 0
    if(newSignal < thresholdMap[i])
    {
      if(!isLastPeakZeroedArray[i] && (currentTime - lastPeakTimeArray[i]) > MAX_TIME_BETWEEN_PEAKS)
      {
        recordNewPeak(i,0);
      }
      else
      {
        //get previous signal
        short prevSignalIndex = signalIndexArray[i]-1;
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
        
    signalIndexArray[i]++;
    if(signalIndexArray[i] == SIGNAL_BUFFER_SIZE) signalIndexArray[i] = 0;
  }
}
