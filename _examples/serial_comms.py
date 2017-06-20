import serial
try:
    ser = serial.Serial('/dev/ttyUSB0', 9600)
except:
    ser = serial.Serial('COM5', 9600)
print "Starting serial communication."
print ser

def serial_send(ser, data):
    ser.write(data.encode())

def serial_recv(ser):
    return ser.readline()

def main():
    try:
        while True:
            msg_recvd = serial_recv(ser)
            print msg_recvd
    except KeyboardInterrupt:
        print "Keyboard interrupted."
        print "Serial reading is now terminated."


if __name__ == '__main__':
    main()