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
MIDI_PORT = "berdrums 1"

def pads(pad_json="basic.json"):
    # Initialize values
    pad_json_path = "settings\pad_maps\%s" %str(pad_json)
    try:
        with open(pad_json_path) as config_file:
            json_file = json.load(config_file)
            # print config_file
            # print json_file
            pads = json_file['pads']

            return pads

    except Exception as e:
        print type(e).__name__ + ': ' + str(e)

    return PADS

def pad_map(pad_id, pads):
    for pad in pads:
        print pad
        if pad_id == pad['id']:
            return pad
    return {}


