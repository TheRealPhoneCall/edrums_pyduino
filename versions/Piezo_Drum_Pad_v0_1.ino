/* Midi Piezoelecric Drum Pads
 * Version: 0.1
 * by Notes and Volts
 * www.notesandvolts.com
 * 
 * This software is an ALPHA version
 * and is unsupported.
 * Use at your own risk!
 */


#include <MIDI.h> // Requires Arduino Midi Library

#define LED 13
#define PADS 3 // How many drum pads?
#define CHANNEL 1 // MIDI Channel
#define DEBOUNCE 30 // Debounce time (in milli-seconds)

// Connect pads in order starting at A0

MIDI_CREATE_DEFAULT_INSTANCE();

int sensitivity = 100; // Maximum input range
int threshold = 10; // Minimum input range

unsigned long timer[PADS];
bool playing[PADS];
int highScore[PADS];
byte note[PADS] = {36, 40, 53}; // Set drum pad notes here


void setup() {
  //Serial.begin(38400);
  MIDI.begin(MIDI_CHANNEL_OFF);
  for (int x = 0; x < PADS; x++) {
    playing[x] = false;
    highScore[x] = 0;
    timer[x] = 0;
  }
}

void loop() {
  for (int x = 0; x < PADS; x++) {
    int volume = analogRead(x);
    if (volume >= threshold && playing[x] == false) {
      if (millis() - timer[x] >= DEBOUNCE) {
        playing[x] = true;
        playNote(x, volume);
      }
    }
    else if (volume >= threshold && playing[x] == true) {
      playNote(x, volume);
    }
    else if (volume < threshold && playing[x] == true) {
      MIDI.sendNoteOn(note[x], highScore[x], CHANNEL);
      MIDI.sendNoteOff(note[x], 0, CHANNEL);
      highScore[x] = 0;
      playing[x] = false;
      timer[x] = millis();
    }
  }
}

void playNote (int pad, int volume) {
  float velocity = ((volume) / float(sensitivity - threshold)) * 127;
  if (velocity > 127) velocity = 127;
  if (velocity > highScore[pad]) highScore[pad] = velocity;
}

