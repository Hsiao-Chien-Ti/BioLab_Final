import UdpComms as U
import time
import interface
from keras import models
from scipy.signal import butter,iirnotch, filtfilt
import numpy as np
# model = models.load_model('model.h5')
sock = U.UdpComms(udpIP="127.0.0.1", portTX=8000, portRX=8001,
                enableRX=True, suppressWarnings=True)
start = 0
interf = [interface.interface("COM1"),interface.interface("COM2")]
windowWidth = 1000
skillLength = 3
gestureResult=[]
skillSequence=[[0,1,2,3],[1,3,0,2],[1,2,0,1]]
skills=['attack1','attack2','attack3']
turn=1
X =[np.linspace(0,0,windowWidth),np.linspace(0,0,windowWidth),np.linspace(0,0,windowWidth),np.linspace(0,0,windowWidth)]
def filter(data, notchcut,q,lowcut, highcut, fs, order=4):
    b,a=iirnotch(notchcut,q,fs)
    y = filtfilt(b, a, data)
    # print(y)
    avg = np.mean(y)
    y = y - avg
    b, a = butter(order, [lowcut, highcut],fs=fs, btype='band')
    y = filtfilt(b, a, y)
    y = abs(y)
    # b, a = butter(order, 3,fs=fs, btype='low')
    # y = filtfilt(b, a, y)
    # print(y)
    return y
def update():
    global X,model,gestureResult
    X_all=[]
    for i in range(4):
        X[i][:-1]=X[i][1:]   # shift data in the temporal mean 1 sample left    
        value = float(float(interf[turn-1].read())*5/255)               # read line (single value) from the serial port
        X[i][-1] = value                 # vector containing the instantaneous values  
        filtRes=filter(X[i],60,0.5,10.2,410,1000)
        X_all.append(filtRes)
    pred = model.predict(X_all)
    if np.max(pred)>0.6:
        X =[np.linspace(0,0,windowWidth),np.linspace(0,0,windowWidth),np.linspace(0,0,windowWidth),np.linspace(0,0,windowWidth)]
        gestureResult.append(np.argmax(pred))
        if len(gestureResult)==skillLength:
            autoCalibration()
def autoCalibration():
    global gestureResult
    skill=0
    maxSimilarity=0
    for i in range(len(skillSequence)):
        similarity=0
        for j in range(skillLength):
            if skills[i][j]==gestureResult[j]:
                similarity+=1
        if similarity>maxSimilarity:
            maxSimilarity=similarity
            skill=i
    sock.SendData(str(turn)+skills[skill])
    interf[turn-1].write('e')
    turn = (2 if turn==1 else 1)
    interf[turn-1].write('s')
    gestureResult=[]
print('python server running')
while True:
    data = sock.ReadReceivedData()  # read data
    if data == 'start':
        sock.SendData('BT connected')
        time.sleep(1)
        interf[turn-1].write('s')
        start = 1
    if data == 'close':
        sock.CloseSocket()
        sock = U.UdpComms(udpIP="127.0.0.1", portTX=8000,
                        portRX=8001, enableRX=True, suppressWarnings=True)
    if data != None:  # if NEW data has been received since last ReadReceivedData function call
        print(data)  # print new received data
    if data=='home':
        start=0
    if start:
        update()
        # start=0
    # time.sleep(1)