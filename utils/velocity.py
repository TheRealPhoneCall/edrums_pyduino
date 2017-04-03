from .settings import *
from .utils import map

class Velocity(object):
    def __init__(self, pin, val):
        self.pin = pin
        self.val = val
        self.threshold = THRESHOLD[pin]
        self.velocity = None
        self.max_velocity = MAX_VELOCITY
        self.peak = None
        self.max_peak = None

    def is_triggered(self):
        if self.val >= self.threshold:
            return True 
        else:
            return False
    
    def get_current_velocity(self, val):
        return map(val, 0, 1023, self.threshold, MAX_VELOCITY)

    def get_max_velocity(self, val):
        self.val = val        

    def is_peak_reached(self, val):
        previous_val = self.val
        current_val = val

        # if the piezo val is dropping, means the peak is reached
        if current_val >= previous_val:
            self.peak = current_val
            return True
        else:
            self.peak = self.peak
            return False

    def is_max_peak_reached(self, val):
        previous_peak = self.peak
        current_peak = val

        # if the piezo peak is dropping, means the max peak is reached
        if current_peak >= previous_peak:
            self.max_peak = current_peak
            return True
        else:
            self.max_peak = self.max_peak
            return False

    def velocity(self):
        velocity = self.max_peak
        return self.get_current_velocity(velocity)

    def __str__(self):
        return "piezo #%s velocity - %d" 