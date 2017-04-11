# 1 "c:\\Users\\Lenovo\\Documents\\_BERDWARE\\7.0_BerDrums\\version_pyduino\\src\\main.cpp"
# 1 "c:\\Users\\Lenovo\\Documents\\_BERDWARE\\7.0_BerDrums\\version_pyduino\\src\\main.cpp"
/* Midi Piezoelecric Drum Pads

 * Version: 0.1

 * by Notes and Volts

 * www.notesandvolts.com

 * 

 * This software is an ALPHA version

 * and is unsupported.

 * Use at your own risk!

 */
# 11 "c:\\Users\\Lenovo\\Documents\\_BERDWARE\\7.0_BerDrums\\version_pyduino\\src\\main.cpp"
# 12 "c:\\Users\\Lenovo\\Documents\\_BERDWARE\\7.0_BerDrums\\version_pyduino\\src\\main.cpp" 2
// #include "MIDI.h" // Requires Arduino Midi Library
# 21 "c:\\Users\\Lenovo\\Documents\\_BERDWARE\\7.0_BerDrums\\version_pyduino\\src\\main.cpp"
// Connect pads in order starting at A0

// MIDI_CREATE_DEFAULT_INSTANCE();

int sensitivity = 120; // Maximum input range
int threshold = 20; // Minimum input range




unsigned long timer[6 /* How many drum pads?*/];
bool playing[6 /* How many drum pads?*/];
int highScore[6 /* How many drum pads?*/];

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

byte SNARE_NOTE = 70;
byte LTOM_NOTE = 71;
byte RTOM_NOTE = 72;
byte LCYM_NOTE = 73;
byte RCYM_NOTE = 74;
byte KICK_NOTE = 75;

byte DRUM_CHANNEL = 0;
byte note[6 /* How many drum pads?*/] = {SNARE_NOTE, LTOM_NOTE, RTOM_NOTE,
                   LCYM_NOTE, RCYM_NOTE, KICK_NOTE};

void midiSendNote(byte note, int highScore, byte channel){
    String strMidiMsg = "";
    String strNote = String(note, 10);
    String strHighScore = String(highScore, 10);
    String strChannel = String(channel, 10);
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

void sendMidiMsg_toLoopMidi(byte command, byte note, byte velocity) {
  Serial.print(command);
  Serial.print(note);
  Serial.print(velocity);
}

void updateVelocity (int pad, int volume) {
  float velocity = ((volume) / float(sensitivity - threshold)) * 127;
  if (velocity > 127) velocity = 127;
  if (velocity > highScore[pad]) highScore[pad] = velocity;
}

void setup() {
  Serial.begin(9600);
  while (!Serial); // wait for serial to connect
  // MIDI.begin(MIDI_CHANNEL_OFF);
  for (int x = 0; x < 6 /* How many drum pads?*/; x++) {
    playing[x] = false;
    highScore[x] = 0;
    timer[x] = 0;
  }
  Serial.setTimeout(1000);
  Serial.println("Starting...");
}

void loop() {
  for (int x = 0; x < 6 /* How many drum pads?*/; x++) {
    int volume = analogRead(x);
    if (volume >= threshold && playing[x] == false) {
      if (millis() - timer[x] >= 50 /* Debounce time (in milli-seconds)*/) {
        playing[x] = true;
        updateVelocity(x, volume);
      }
    }
    else if (volume >= threshold && playing[x] == true) {
      updateVelocity(x, volume);
    }
    else if (volume < threshold && playing[x] == true) {
//      MIDI.sendNoteOn(note[x], highScore[x], CHANNEL);
//      MIDI.sendNoteOff(note[x], 0, CHANNEL);
      sendMidiMsg_toLoopMidi(0x90, note[x], highScore[x]);
      delay(5);
      sendMidiMsg_toLoopMidi(0x80, note[x], 0);
      highScore[x] = 0;
      playing[x] = false;
      timer[x] = millis();
    }
  }
  delay(50);
}
