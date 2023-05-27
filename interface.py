import BT
import sys

# hint: You may design additional functions to execute the input command, which will be helpful when debugging :)

class interface:
    def __init__(self,port="COM40"):
        print("")
        print("Arduino Bluetooth Connect Program.")
        print("")
        self.ser = BT.bluetooth()
        while(not self.ser.do_connect(port)):
            self.ser.do_connect(port)
        # self.write('s')

    def read(self):
        return self.ser.SerialReadInt()

    def end_process(self):
        self.ser.disconnect()
        # sys.exit(0)

    def write(self, input):
        # print("write")
        return self.ser.SerialWrite(input)