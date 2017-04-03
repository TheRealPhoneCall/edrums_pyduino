import serial
import time

from utils.settings import *

try:
    ser = serial.Serial('/dev/ttyUSB0', 31250)
except:
    ser = serial.Serial('COM5', 31250)
print "Starting serial communication."
print ser

def serial_send(ser, data):
    ser.write(data.encode())

def serial_recv(ser):
    return ser.readline()

def get_pin_val(msg_recvd):
    msg_recvd = msg_recvd.split(":")
    return int(msg_recvd[1])

def get_msgs_recvd(msgs_recvd):
    return msgs_recvd.split(",")

def main():
    try:
        while True:
            vel_obj = []
            # read serial first
            msgs_recvd = serial_recv(ser)
            msgs_recvd = get_msgs_recvd(msgs_recvd)
            print msgs_recvd

            for pin in DEFAULT_PINS:
                # initialize vel object
                msg_recvd = msgs_recvd[pin]
                val = get_pin_val(msg_recvd)
                vel_obj[pin] = Velocity(pin, val)
                
                # keep reading until the peak is reached
                max_peak_is_reached = False
                while not max_peak_is_reached:
                    val = get_pin_val(msg_recvd) 
                    vel_obj[pin].update_values(val)                   
                    
                    if vel_obj[pin].is_triggered(val) and vel_obj[pin].is_max_peak_reached(val):
                        max_peak_is_reached = True
                        velocity = vel_obj[pin].velocity()
                        fire_note(pin, velocity)
                        break
                    else:
                        if vel_obj[pin].is_peak_reached():
                            vel_obj[pin].update_values(val) 

                        max_peak_is_reached = False
                    
                    # delay for next reading
                    time.sleep(0.010)
                    msg_recvd = serial_recv(ser)
                    print msg_recvd

    except KeyboardInterrupt:
        print "Keyboard interrupted."
        print "Serial reading is now terminated."


if __name__ == '__main__':
    main()