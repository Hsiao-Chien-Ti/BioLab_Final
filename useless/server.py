import UdpComms as U
import time
import interface

# Create UDP socket to use for sending (and receiving)
sock = U.UdpComms(udpIP="127.0.0.1", portTX=8000, portRX=8001, enableRX=True, suppressWarnings=True)
start=0
print('python server running')
while True:
    data = sock.ReadReceivedData() # read data
    if data=='start':
        print('connect BT')
        # interf = interface.interface()
        sock.SendData('BT connected')
        start=1
    if data=='home':
        start=0
    if data != None: # if NEW data has been received since last ReadReceivedData function call
        print(data) # print new received data
    # if start:
    #     cmd=input()
    #     sock.SendData(cmd)
        # start=0
    # time.sleep(1)