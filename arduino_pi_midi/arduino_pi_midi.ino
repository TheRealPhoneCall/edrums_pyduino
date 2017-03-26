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
#define SNARE_NOTE "70"
#define LTOM_NOTE 71
#define RTOM_NOTE 72
#define LCYM_NOTE 73
#define RCYM_NOTE 74
#define KICK_NOTE "75"

//MIDI defines
#define NOTE_ON_CMD "0x90"
#define NOTE_OFF_CMD "0x80"
#define MAX_MIDI_VELOCITY 127
#define VELOCITY "64"

//MIDI baud rate
#define SERIAL_RATE 9600

void setup()
{
  Serial.begin(SERIAL_RATE);
  while (!Serial) ;  // wait for Serial to become active
  Serial.println ("Starting");
}

void loop()
{
  unsigned short velocity = 64;

  // fire kick
  noteFire(KICK_NOTE, VELOCITY);
  delay(1000);
  flashGreen(velocity*3);
  
  // fire snare
  noteFire(SNARE_NOTE, VELOCITY);
  delay(1000);
  flashRed(velocity*3);
}

void noteFire(unsigned short note, unsigned short velocity)
{
  if(velocity > MAX_MIDI_VELOCITY)
    velocity = MAX_MIDI_VELOCITY;
  
  midiNoteOn(note, velocity);
  midiNoteOff(note, velocity);
}

void midiNoteOn(byte note, byte midiVelocity)
{
  Serial.println(NOTE_ON_CMD);
  Serial.println(note);
  Serial.println(midiVelocity);
  
}

void midiNoteOff(byte note, byte midiVelocity)
{
  Serial.println(NOTE_OFF_CMD);
  Serial.println(note);
  Serial.println(midiVelocity);
}

void flashGreen(int val)
{
  analogWrite(greenPin, val);
}

void flashRed(int val)
{
  analogWrite(redPin, val);
}
