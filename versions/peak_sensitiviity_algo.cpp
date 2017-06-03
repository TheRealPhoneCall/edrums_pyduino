/* Midi Piezoelecric Drum Pads
 * Version: 0.1
 * by Notes and Volts
 * www.notesandvolts.com
 * 
 * This software is an ALPHA version
 * and is unsupported.
 * Use at your own risk!
 */

#include "Arduino.h"
// #include "MIDI.h" // Requires Arduino Midi Library

#define LED 13
#define PADS 6 // How many drum pads?
#define CHANNEL 1 // MIDI Channel
#define DEBOUNCE 20 // Debounce time (in milli-seconds)
#define SERIAL_RATE 115200
#define TIME_OUT 1000

// Connect pads in order starting at A0

// MIDI_CREATE_DEFAULT_INSTANCE();

int sensitivity = 120; // Maximum input range
// int threshold = 30; // Minimum input range

#define NOTE_ON 0x90
#define NOTE_OFF 0x80

unsigned long timer[PADS];
bool playing[PADS];
int maxVelocity[PADS];

// notes:
#define PAD0_NOTE 72    //top left
#define PAD1_NOTE 73    //top right
#define PAD2_NOTE 70    //middle left
#define PAD3_NOTE 71    //middle right
#define PAD4_NOTE 75    //lower left
#define PAD5_NOTE 74    //lower right

// thresholds:
#define PAD0_THRESHOLD 25    
#define PAD1_THRESHOLD 40
#define PAD2_THRESHOLD 20
#define PAD3_THRESHOLD 20
#define PAD4_THRESHOLD 20
#define PAD5_THRESHOLD 20

// max readings:
#define PAD0_MAX 1024   
#define PAD1_MAX 1024
#define PAD2_MAX 900
#define PAD3_MAX 400
#define PAD4_MAX 800
#define PAD5_MAX 800

byte DRUM_CHANNEL = 0;
byte note[PADS] = {PAD0_NOTE, PAD1_NOTE, PAD2_NOTE, PAD3_NOTE, PAD4_NOTE, PAD5_NOTE};
unsigned short threshold[PADS] = {PAD0_THRESHOLD, PAD1_THRESHOLD, PAD2_THRESHOLD, PAD3_THRESHOLD, PAD4_THRESHOLD, PAD5_THRESHOLD};
unsigned short max[PADS] = {PAD0_MAX, PAD1_MAX, PAD2_MAX, PAD3_MAX, PAD4_MAX, PAD5_MAX}; 

void midiSendNote(byte note, int maxVelocity, byte channel){
    String strMidiMsg = "";
    String strNote = String(note, DEC);
    String strmaxVelocity = String(maxVelocity, DEC);
    String strChannel = String(channel, DEC);
    strMidiMsg = strNote + "." + strmaxVelocity + "." + strChannel;
    Serial.println(strMidiMsg);
    // Serial.println(strNote);
    // Serial.println(strmaxVelocity);
    // Serial.println(strChannel);
}

void sendMidiMsg_toPython(byte command, byte note, byte velocity) {
  String strNoteOnCmd = String(command);  
  String strNote = String(note);  
  String strVelocity = String(velocity);
  Serial.println(strNoteOnCmd + "." + strNote + "." + strVelocity);
}

void sendMidiMsgOn_toLoopMidi(byte note, byte velocity) {
  Serial.write(NOTE_ON);  
  Serial.write(note);  
  Serial.write(velocity);
}

void sendMidiMsgOff_toLoopMidi(byte note, byte velocity) {
  Serial.write(NOTE_OFF);  
  Serial.write(note);  
  Serial.write(velocity);
}

void updateVelocity (int pad, int piezoVal) {
  float velocity = ((piezoVal) / float(sensitivity - threshold[pad])) * 127;
  if (velocity > 127) velocity = 127;
  if (velocity > maxVelocity[pad]) maxVelocity[pad] = velocity;
}

void setup() {
  Serial.begin(SERIAL_RATE);
  while (!Serial); // wait for serial to connect
  // MIDI.begin(MIDI_CHANNEL_OFF);
  for (int x = 0; x < PADS; x++) {
    playing[x] = false;
    maxVelocity[x] = 0;
    timer[x] = 0;
  }
  Serial.setTimeout(TIME_OUT);
  // Serial.println("Starting...");
}

void loop() {
  for (int x = 0; x < PADS; x++) {
    int piezoVal = analogRead(x);
    if (piezoVal >= threshold[x] && playing[x] == false) {
      if (millis() - timer[x] >= DEBOUNCE) {
        playing[x] = true;
        updateVelocity(x, piezoVal);
      }
    }
    else if (piezoVal >= threshold[x] && playing[x] == true) {
      updateVelocity(x, piezoVal);
    }
    else if (piezoVal < threshold[x] && playing[x] == true) {
      // MIDI.sendNoteOn(note[x], maxVelocity[x], CHANNEL);
      // MIDI.sendNoteOff(note[x], 0, CHANNEL);
      sendMidiMsgOn_toLoopMidi(note[x], maxVelocity[x]);
      delay(5);
      sendMidiMsgOff_toLoopMidi(note[x], maxVelocity[x]);
      maxVelocity[x] = 0;
      playing[x] = false;
      timer[x] = millis();
    }
  }
}


