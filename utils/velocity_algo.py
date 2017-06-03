from .settings import *
from .utils import map

class Velocity(object):
    def __init__(self, pin, val):
        self.pin = pin        
        self.threshold = THRESHOLDS[pin]
        self.max_velocity = MAX_VELOCITY
        self.val = map(val, 0, 1023, self.threshold, self.max_velocity)
        self.velocity = self.val
        self.peak = None
        self.max_peak = None

    def get_velocity_routine