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

// Define number of piezos
#define NUM_PIEZOS 6 //nano can be 8, mega can be 16

// Initialize serial comm values 
unsigned long BAUD_RATE=9600;
unsigned long TIME_OUT=1000;

// Initialize midi values
unsigned short NOTE_ON=90;
unsigned short NOTE_OFF=80;
unsigned short MAX_VELOCITY=127;

// Initialize config arrays, their default values are set in the next block
unsigned short ledPinsArray[NUM_PIEZOS];
unsigned short piezoPinsArray[NUM_PIEZOS]; 
unsigned int thresholdArray[NUM_PIEZOS]; 
unsigned int noteArray[NUM_PIEZOS];

// Intialize machine state and config values
unsigned short state = 0; // 0 for play state
                          // 1 for configure state
unsigned int configMatrix[5][NUM_PIEZOS] = {};
char drumPadArray[] = {'SNARE', 'LTOM', 'RTOM', 'LCYM', 'RCYM', 'KICK'};
unsigned int defaultConfigMatrix[5][6] = {
  {BAUD_RATE, TIME_OUT, NOTE_ON, NOTE_OFF, MAX_VELOCITY, 0}, // main defaults
  // Array daults. Order: { Snare, LTom, RTom, LCym, RCym, Kick }
  {3, 5, 6, 9, 10, 11},       //ledPinsArray - PWM pins
  {0, 1, 2, 3, 4, 5},         //piezoPinsArray - piezo analog input pins
  {30, 30, 30, 100, 100, 50}, //thresholdArray - anything less than these
                              //                 values are considered zero
  {70, 71, 72, 73, 74, 75}    //noteArray - Snare, LTom, RTom, LCym, RCym, Kick notes 
};


/* SETUP Subroutines */
void setupInitialValues(){
  // setup config values with config defaults
  for (short i=0; i<NUM_PIEZOS; i++){
    if (i<6){
      // setup config matrix data
      configMatrix[0][i] = defaultConfigMatrix[0][i];
      configMatrix[1][i] = defaultConfigMatrix[1][i];
      configMatrix[2][i] = defaultConfigMatrix[2][i];
      configMatrix[3][i] = defaultConfigMatrix[3][i];
      configMatrix[4][i] = defaultConfigMatrix[4][i];
      
      // setup array values data
      ledPinsArray[i] = configMatrix[1][i];
      piezoPinsArray[i] = configMatrix[2][i];
      thresholdArray[i] = configMatrix[3][i];
      noteArray[i] = configMatrix[4][i];
    } else {
      // set to zero those that exceeds the number of piezos
      configMatrix[0][i] = 0;
      configMatrix[1][i] = 0;
      configMatrix[2][i] = 0;
      configMatrix[3][i] = 0;
      configMatrix[4][i] = 0;
    }
    
  }

  // setup main defaults
  BAUD_RATE = configMatrix[0][0];
  TIME_OUT = configMatrix[0][1];
  NOTE_ON = configMatrix[0][2];
  NOTE_OFF = configMatrix[0][3];
  MAX_VELOCITY = configMatrix[0][4];

  // setup analog output pins
  for (short i=0; i<NUM_PIEZOS; i++){
    pinMode(ledPinsArray, OUTPUT);
  }
}

void setup(){
  Serial.begin(BAUD_RATE);

  // wait for serial to become active
  while (!Serial){
    // do nothing
    // just wait for the serial to be live
  } 

  // setup device's initial values
  setupInitialValues();

  // Serial comm setup
  Serial.setTimeout(TIME_OUT);
  Serial.println("Starting");
}

/* LOOP Subroutines */
String getStringPartByNr(String data, char separator, int index)
{
    // spliting a string and return the part nr index
    // split by separator
    
    int stringData = 0;        //variable to count data part nr 
    String dataPart = "";      //variable to hole the return text
    
    for(int i = 0; i<data.length()-1; i++) {    //Walk through the text one letter at a time
      
      if(data[i]==separator) {
        //Count the number of times separator character appears in the text
        stringData++;
        
      }else if(stringData==index) {
        //get the text when separator is the rignt one
        dataPart.concat(data[i]);
        
      }else if(stringData>index) {
        //return text and stop if the next separator appears - to save CPU-time
        Serial.println(dataPart);
        return dataPart;
        break;
        
      }

    }
    //return text if this is the last part
    Serial.println(dataPart);
    return dataPart;
}

void updateConfigValues(String configMatrix0, String configMatrix1, String configMatrix2,
                        String configMatrix3, String configMatrix4){
  configMatrix[0][0] = getStringPartByNr(configMatrix0, ",", 0).toInt();
  configMatrix[0][1] = getStringPartByNr(configMatrix0, ",", 1).toInt();
  configMatrix[0][2] = getStringPartByNr(configMatrix0, ",", 2).toInt();
  configMatrix[0][3] = getStringPartByNr(configMatrix0, ",", 3).toInt();
  configMatrix[0][4] = getStringPartByNr(configMatrix0, ",", 4).toInt();

  // setup main defaults
  BAUD_RATE = configMatrix[0][0];
  TIME_OUT = configMatrix[0][1];
  NOTE_ON = configMatrix[0][2];
  NOTE_OFF = configMatrix[0][3];
  MAX_VELOCITY = configMatrix[0][4];

  // setup config values with config defaults
  for (short i=0; i<NUM_PIEZOS; i++){
    if (i<6){
      // setup config matrix data
      configMatrix[1][i] = getStringPartByNr(configMatrix1, ",", i).toInt();
      configMatrix[2][i] = getStringPartByNr(configMatrix2, ",", i).toInt();
      configMatrix[3][i] = getStringPartByNr(configMatrix3, ",", i).toInt();
      configMatrix[4][i] = getStringPartByNr(configMatrix4, ",", i).toInt();
      
      // setup array values data
      ledPinsArray[i] = configMatrix[1][i];
      piezoPinsArray[i] = configMatrix[2][i];
      thresholdArray[i] = configMatrix[3][i];
      noteArray[i] = configMatrix[4][i];
    } else {
      // set to zero those that exceeds the number of piezos
      configMatrix[0][i] = 0;
      configMatrix[1][i] = 0;
      configMatrix[2][i] = 0;
      configMatrix[3][i] = 0;
      configMatrix[4][i] = 0;
    }
    
  }

}

void setDeviceValues(String serialData){
  // Get the array parts of the serialData
  String configMatrix0 = getStringPartByNr(serialData, "},{", 0);  
  String configMatrix1 = getStringPartByNr(serialData, "},{", 1);
  String configMatrix2 = getStringPartByNr(serialData, "},{", 2);
  String configMatrix3 = getStringPartByNr(serialData, "},{", 3);
  String configMatrix4 = getStringPartByNr(serialData, "},{", 4);

  // Remove the inner and outer brackers - {{  }} of the start/end 
  // of the serial data
  // configMatrix0 = configMatrix0.replace("{{", "");
  // configMatrix4 = configMatrix4.replace("}}", "");

  // Update the config values:
  updateConfigValues(configMatrix0, configMatrix1, configMatrix2, 
                     configMatrix3, configMatrix4);
}

//send MIDI message
void sendMidiMsg(char drumPad, byte command, byte note, byte velocity) {
  String strDrumPad = String(strDrumPad);
  String strNoteOnCmd = String(command);  
  String strNote = String(note);  
  String strVelocity = String(velocity);
  Serial.println(strDrumPad + ": " + strNoteOnCmd + "." + strNote + "." + strVelocity);
}

int getMaxVal(int lastVal, int piezoPin){
  int currentVal = analogRead(piezoPin);
  while (currentVal>lastVal){
    lastVal = currentVal;
    currentVal = analogRead(piezoPin);
  }
  return lastVal;
}

void drumRoutine(){
  int piezoPin, piezoVal, threshold;
  for (short i; i<NUM_PIEZOS; i++){
    piezoPin = piezoPinsArray[i];
    piezoVal = analogRead(piezoPin);
    threshold = thresholdArray[i];
    // Check if the piezo passes threshold voltage
    if (piezoVal>threshold){
      byte noteOn = NOTE_ON;
      byte noteMidi = noteArray[i];
      char drumPad = drumPadArray[i];    

      // Get max piezoValue 
      int maxPiezoVal = getMaxVal(piezoVal, piezoPin);
      int velocity = map(maxPiezoVal, 0, 1023, threshold, 300); //300 has to be peak
                                                 //velocity between 50 and 127 
                                                 //based on max val from piezo
      
      sendMidiMsg(drumPad, noteOn, noteMidi, velocity);
      delay(500);
      sendMidiMsg(drumPad, noteOn, noteMidi, 0);
    }
  }
  
}

void loop(){
  // Check which state the current program runs
  // if (Serial.available()) {
  //   // state = 1;
  //   Serial.println("Initiating configuaration setup routine...");
  //   String serialData = Serial.readStringUntil("}}");
  //   setDeviceValues(serialData);
  //   Serial.println("Configuration updated.");
  //   state = 0;
  //   drumRoutine();
  // } else {
  //   // state = 0;
  //   drumRoutine();
  // }
  drumRoutine();
}
