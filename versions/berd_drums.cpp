/*
	Pyduino MIDI Drums

	An arduino MIDI drum project that is configurable with python.
    This is primarily benchmarked to communicate with the raspberry pi.
    This program assumes the Arduino Uno is used, with 6 analog inputs.
    If other boards are used, you can set the size of the program variables'
    arrays to be equal to how many analog inputs the board can take.

	The circuit:
	* piezo sensors to input drum signals
	* serial communication to the raspberry pi.

	Created 25/03/2017
	By Daryl Pongcol

*/

#include "Arduino.h"
 
//Piezo defines
#define NUM_PIEZOS 6
#define SNARE_THRESHOLD 30     
#define LTOM_THRESHOLD 30
#define RTOM_THRESHOLD 30
#define LCYM_THRESHOLD 100
#define RCYM_THRESHOLD 100
#define KICK_THRESHOLD 50

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
#define SERIAL_RATE 115200

//TIME defines
#define MAX_TIME_BETWEEN_PEAKS 20
#define MAX_TIME_READING 50
#define MIN_TIME_BETWEEN_NOTES 50

//Maps for the slot, note & threshold of each piezos 
unsigned short mapPiezos[NUM_PIEZOS];
unsigned short mapNotes[NUM_PIEZOS];
unsigned short mapThresholds[NUM_PIEZOS];

//Ring buffers to store previous and current analog signal and peaks
// bfr - buffer
unsigned short bfrCurrentSignal[NUM_PIEZOS];
unsigned short bfrCurrentPeak[NUM_PIEZOS];
unsigned short bfrPrevSignal[NUM_PIEZOS];
unsigned short bfrPrevPeak[NUM_PIEZOS];

//Booleans for signal peak reading 
bool isCurrentlyReading[NUM_PIEZOS];
bool isLastReadingDone[NUM_PIEZOS];
bool isMaxPeakDetermined[NUM_PIEZOS];

unsigned long timeStartedReading[NUM_PIEZOS];
unsigned long timeLastPeak[NUM_PIEZOS];
unsigned long timeLastNote[NUM_PIEZOS];

void initializeBuffers(unsigned short piezo) {
    // initialize buffers
    bfrCurrentSignal[piezo] = 0;
    bfrCurrentPeak[piezo] = 0;
    bfrPrevSignal[piezo] = 0;
    bfrPrevPeak[piezo] = 0;

    // initialize logic
    isCurrentlyReading[piezo] = false;
    isLastReadingDone[piezo] = true;
    isMaxPeakDetermined[piezo] = false;
}

void setup(){
    Serial.begin(SERIAL_RATE);
  
    //initialize globals
    for(short piezo=0; piezo<NUM_PIEZOS; ++piezo){
        initializeBuffers(piezo);
    }
  
    mapThresholds[0] = KICK_THRESHOLD;
    mapThresholds[1] = RTOM_THRESHOLD;
    mapThresholds[2] = RCYM_THRESHOLD;
    mapThresholds[3] = LCYM_THRESHOLD;
    mapThresholds[4] = SNARE_THRESHOLD;
    mapThresholds[5] = LTOM_THRESHOLD;  
  
    mapNotes[0] = KICK_NOTE;
    mapNotes[1] = RTOM_NOTE;
    mapNotes[2] = RCYM_NOTE;
    mapNotes[3] = LCYM_NOTE;
    mapNotes[4] = SNARE_NOTE;
    mapNotes[5] = LTOM_NOTE;  
}

void midiNoteOn(byte note, byte midiVelocity){
    Serial.write(NOTE_ON_CMD);
    Serial.write(note);
    Serial.write(midiVelocity);
}

void midiNoteOff(byte note, byte midiVelocity){
    Serial.write(NOTE_OFF_CMD);
    Serial.write(note);
    Serial.write(midiVelocity);
}

void noteFire(unsigned short note, unsigned short velocity){
    if(velocity > MAX_MIDI_VELOCITY)
        velocity = MAX_MIDI_VELOCITY;
  
    midiNoteOn(note, velocity);
    midiNoteOff(note, velocity);
}

void recordPeak(unsigned short piezo, unsigned short peak) {
    bfrCurrentPeak[piezo] = peak;

    if((bfrCurrentPeak[piezo] < bfrPrevPeak[piezo]) && !isMaxPeakDetermined[piezo]) {
        // the previously recorded peak is maximum peak
        isMaxPeakDetermined[piezo] = true;
        noteFire(mapNotes[piezo], bfrPrevPeak[piezo]);
    }

    // set the peak to be the new prev peak for the next loop
    bfrPrevPeak[piezo] = peak;
}

void recordSignal(unsigned short piezo, unsigned short signal, unsigned long timeCurrent) {
    isCurrentlyReading[piezo] = true;
    bfrCurrentSignal[piezo] = signal;

    if(isLastReadingDone[piezo] && !isCurrentlyReading[piezo]){
        // signal is new
        isCurrentlyReading[piezo] = true;
        isLastReadingDone[piezo] = false;
        isMaxPeakDetermined[piezo] = false;
        timeStartedReading[piezo] = timeCurrent;
        bfrPrevSignal[piezo] = 0;
    } else if (!isLastReadingDone[piezo] && isCurrentlyReading[piezo]){
        // signal is not new
        isLastReadingDone[piezo] = false;

        if (bfrCurrentSignal[piezo] < bfrPrevSignal[piezo]){
            // the previously recorded signal is peak
            recordPeak(piezo, bfrPrevSignal[piezo]);
        }   
    }

    // set the signal to be the prev signal for the next loop 
    bfrPrevSignal[piezo] = signal;
}

void loop(){
    unsigned long timeCurrent = millis();

    for (short piezo=0; piezo<NUM_PIEZOS; piezo++){
        // read signal from all piezos
        unsigned short newSignal = analogRead(mapPiezos[piezo]);

        if (newSignal > mapThresholds[piezo]) {
            // signal passes threshold
            if (timeCurrent - timeStartedReading[piezo] < MAX_TIME_READING){
                // record signal when time lapsed reading is not yet maxed
                recordSignal(piezo, newSignal, timeCurrent);
            } else {
                // else, re-initialize buffers 
                initializeBuffers(piezo);
            }
        }
    }
}

