/*
  ===========================================================================================
  Example used in Quick-Start
  -------------------------------------------------------------------------------------------
  Plotter
  v2.3.0
  https://github.com/devinaconley/arduino-plotter
  by Devin Conley
  ===========================================================================================
*/

#include "Arduino.h"
#include "Plotter.h"

double x;

Plotter p;

void setup()
{
    p.Begin();

    p.AddTimeGraph( "piezo sensor", 500, "label for x", x );
}

void loop() {
    x = analogRead(0);

    p.Plot(); // usually called within loop()
}