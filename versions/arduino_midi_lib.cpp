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
#define DEBOUNCE 50 // Debounce time (in milli-seconds)
#define SERIAL_RATE 115200
#define TIME_OUT 1000

// Connect pads in order starting at A0

// MIDI_CREATE_DEFAULT_INSTANCE();

int sensitivity = 120; // Maximum input range
int threshold = 20; // Minimum input range

#define NOTE_ON 0x90
#define NOTE_OFF 0x80

unsigned long timer[PADS];
bool playing[PADS];
int highScore[PADS];

// byte ACOUSTIC_BASS = 35;
// byte ACOUSTIC_SNARE = 38;
// byte CLOSED_HIGH_HAT = 42;
// byte OPEN_HIGH_HAT = 46;
// byte LOW_TOM = 35;
// byte HIGH_TOM = 50;
// byte CRASH_CYMBAL1 = 49;
// byte RIDE_CYMBAL1 = 51;

// byte DRUM_CHANNEL = 10;
// byte note[PADS] = {ACOUSTIC_BASS, ACOUSTIC_SNARE, CLOSED_HIGH_HAT, 
//                    LOW_TOM, HIGH_TOM, CRASH_CYMBAL1}; 

byte SNARE_NOTE = 31;
byte LTOM_NOTE = 48;
byte RTOM_NOTE = 47;
byte LCYM_NOTE = 49;
byte RCYM_NOTE = 57;
byte KICK_NOTE = 36;

byte DRUM_CHANNEL = 0;
byte note[PADS] = {SNARE_NOTE, LTOM_NOTE, RTOM_NOTE, 
                   LCYM_NOTE, RCYM_NOTE, KICK_NOTE}; 

void midiSendNote(byte note, int highScore, byte channel){
    String strMidiMsg = "";
    String strNote = String(note, DEC);
    String strHighScore = String(highScore, DEC);
    String strChannel = String(channel, DEC);
    strMidiMsg = strNote + "." + strHighScore + "." + strChannel;
    Serial.println(strMidiMsg);
    // Serial.println(strNote);
    // Serial.println(strHighScore);
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
  float velocity = ((piezoVal) / float(sensitivity - threshold)) * 127;
  if (velocity > 127) velocity = 127;
  if (velocity > highScore[pad]) highScore[pad] = velocity;
}

void setup() {
  Serial.begin(SERIAL_RATE);
  while (!Serial); // wait for serial to connect
  // MIDI.begin(MIDI_CHANNEL_OFF);
  for (int x = 0; x < PADS; x++) {
    playing[x] = false;
    highScore[x] = 0;
    timer[x] = 0;
  }
  Serial.setTimeout(TIME_OUT);
  // Serial.println("Starting...");
}

void loop() {
  for (int x = 0; x < PADS; x++) {
    int piezoVal = analogRead(x);
    if (piezoVal >= threshold && playing[x] == false) {
      if (millis() - timer[x] >= DEBOUNCE) {
        playing[x] = true;
        updateVelocity(x, piezoVal);
      }
    }
    else if (piezoVal >= threshold && playing[x] == true) {
      updateVelocity(x, piezoVal);
    }
    else if (piezoVal < threshold && playing[x] == true) {
      // MIDI.sendNoteOn(note[x], highScore[x], CHANNEL);
      // MIDI.sendNoteOff(note[x], 0, CHANNEL);
      sendMidiMsgOn_toLoopMidi(note[x], highScore[x]);
      delay(5);
      sendMidiMsgOff_toLoopMidi(note[x], highScore[x]);
      highScore[x] = 0;
      playing[x] = false;
      timer[x] = millis();
    }
  }
  delay(10);
}


