'''
    Config file for the drum pad
    Calibrate these values for better pad response

'''

# Defaults
NUM_PIEZOS = 6
DEFAULT_PINS = [0, 1, 2, 3, 4, 5] 
DEFAULT_PADS = ['SNARE', 'LTOM', 'RTOM', 'LCYM', 'RCYM', 'KICK']
DEFAULT_NOTES = [70, 71, 72, 73, 74, 75]
DEFAULT_THRESHOLDS = [30, 30, 30, 100, 100, 50]

NOTE_ON = 90
NOTE_OFF = 80
MAX_VELOCITY = 127
TIME_DIFF = 0.010

# Initialize values
PINS = DEFAULT_PINS
NOTES = DEFAULT_NOTES
THRESHOLDS = DEFAULT_THRESHOLDS
PADS = DEFAULT_PADS

SERIAL_RATE = 32150
