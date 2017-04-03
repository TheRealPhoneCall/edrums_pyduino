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
        data = "{" + "{9600,1000,100,80,127,0}," + "{3,4,5,10,13,16}," + \
                    "{0,1,2,3,4,5}," + "{30,40,50,120,120,60}," + \
                    "{76,77,78,79,80,81}" + "}"
        print data
        serial_send(ser, data)
        while True:
            msg_recvd = serial_recv(ser)
            print msg_recvd
    except KeyboardInterrupt:
        print "Keyboard interrupted."
        print "Serial reading is now terminated."


if __name__ == '__main__':
    main()