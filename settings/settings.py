'''
    Config file for the drum pad
    Calibrate these values for better pad response

'''
import json

# Defaults
NUM_PIEZOS = 6
PADS = []
NOTE_ON = 90
NOTE_OFF = 80
MAX_VELOCITY = 127
TIME_DIFF = 0.010
SERIAL_RATE = 115200
COM_PORT = "COM5"
MIDI_PORT = "berdrums"

def pads(pad_json_path="settings\pad_maps\basic.json"):
    # Initialize values
    try:
        with open(pad_json_path) as config_file:
            pads = json.loads(config_file)
            
            for pad in pads:
                PADS.append(pad)

    except Exception as e:
        print type(e).__name__ + ': ' + str(e)

    return PADS

def pad_map(pad_id, pads):
    for pad in pads:
        if pad_id == pad.id:
            return pad
    return None


