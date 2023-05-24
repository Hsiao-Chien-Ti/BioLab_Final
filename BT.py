from time import sleep
import serial
# these codes are for bluetooth
# hint: please check the function "sleep". how does it work?

class bluetooth:
    def __init__(self):
        self.ser = serial.Serial()

    def do_connect(self,port):
        self.ser.close()
        print("Connecting...")
        try:
            self.ser = serial.Serial(port,115200,timeout=2)
            self.ser.set_buffer_size(rx_size = 115200, tx_size = 115200)
            print("connect success")
            print("")
            # self.ser.timeout=None
        except serial.serialutil.SerialException as ex:
            print("fail to connect")
            print(ex)
            print("")
            return False
        return True


    def disconnect(self):
        self.ser.close()

    def SerialWrite(self,output):
        # send = 's'.encode("utf-8")
        if output.isdigit():
            send = int(output).to_bytes(1, 'little')
        else:
            send = output.encode("utf-8")
        self.ser.write(send)

    def SerialReadInt(self):
        waiting = self.ser.in_waiting
        if waiting >= 0:
            rv = self.ser.read(1)
            rv=int.from_bytes(rv, byteorder='big', signed=False)
            return rv
        return

    def SerialReadByte(self):
        sleep(0.005)
        waiting = self.ser.inWaiting()
        rv = self.ser.read(waiting)
        return rv


