import serial
import time
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
    msg_recvd = msg_recvd.split(": ")
    return int(msg_recvd[0]), int(msg_recvd[1])

def main():
    try:
        while True:
            for pin in DEFAULT_PINS:
                # read serial first
                msg_recvd = serial_recv(ser)
                print msg_recvd

                # initialize vel object
                pin, val = get_pin_val(msg_recvd)
                vel = Velocity(pin, velocity)
                
                # keep reading until the peak is reached
                max_peak_is_reached = False
                while not max_peak_is_reached:
                    pin, val = get_pin_val(msg_recvd) 
                    vel.update_values(val)                   
                    
                    if vel.is_triggered(val) and vel.is_max_peak_reached(val):
                        max_peak_is_reached = True
                        velocity = vel.velocity()
                        fire_note(pin, velocity)
                        break
                    else:
                        if vel.is_peak_reached():
                            vel.update_values(val) 
                        else:

                        max_peak_is_reached = True
                    
                    # delay for next reading
                    time.sleep(0.010)
                    msg_recvd = serial_recv(ser)
                    print msg_recvd

    except KeyboardInterrupt:
        print "Keyboard interrupted."
        print "Serial reading is now terminated."


if __name__ == '__main__':
    main()