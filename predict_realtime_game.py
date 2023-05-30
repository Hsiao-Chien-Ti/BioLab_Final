import numpy as np
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import interface
from keras import models
import time
import os
import pandas as pd
import sys
from scipy.signal import butter, filtfilt
from datetime import datetime
import UdpComms as U
model = models.load_model('model_2023_05_29_17_52_08.h5')
rest_model = models.load_model('exist_model_2023_05_29_17_13_57.h5')
windowWidth = 1500
subWindowWidth = 100
sock = U.UdpComms(udpIP="127.0.0.1", portTX=8000, portRX=8001,
                enableRX=True, suppressWarnings=True)
class Main():    
    def __init__(self):
        self.start=0
        super().__init__()
        self.interf = interface.interface("COM42")
        print('python server running')
        self.interf.write('s')
        self.X =[np.linspace(0,0,windowWidth),np.linspace(0,0,windowWidth),np.linspace(0,0,windowWidth),np.linspace(0,0,windowWidth)]
    def save(self,gesture,count):
            with open('realtime/'+str(gesture)+'_'+datetime.strftime(datetime.now(),'%Y_%m_%d_%H_%M_%S')+'.txt','w') as f:
                f.write('time\tchannel1\tchannel2\tchannel3\tchannel4\tclass\n')
                for i in range(windowWidth):
                    f.write(str(i))
                    f.write('\t')
                    for j in range(4):
                        f.write(str(round(self.X[j][i], 3)))
                        f.write('\t')
                    f.write(str(gesture))
                    f.write('\n')
                f.write(str(count))
    def run(self):
        self.count=0
        self.rest=1
        try:
            while True:
                data = sock.ReadReceivedData() # read data
                if data != None: # if NEW data has been received since last ReadReceivedData function call
                    print(data) # print new received data
                if data=='start':
                    sock.SendData('BT connected')
                    self.start=1
                if data=='home':
                    self.start=0
                for i in range(4):
                    self.X[i][:-1]=self.X[i][1:]   # shift data in the temporal mean 1 sample left    
                    value = float(float(self.interf.read())*5/255)               # read line (single value) from the serial port
                    self.X[i][-1] = value                 # vector containing the instantaneous values  
                self.count+=1
                if(self.start==0):
                    continue
                if(self.rest==1 and self.count<100):
                    continue
                if(self.rest==2 and self.count<1500):
                    continue
                if(self.rest==2):
                    self.rest=1
                if(self.rest==1):
                    # print(666)
                    self.X_data=self.X[0:subWindowWidth]
                    self.X_data = np.array(self.X_data).reshape(-1, subWindowWidth, 4, 1)
                    pred = rest_model.predict(self.X_data, verbose = 0)
                    if(np.argmax(pred)==1 or (np.argmax(pred)==0 and np.max(pred)<0.95)):
                        # print("aaa")
                        self.rest=0
                if(self.rest==0):
                    # print()
                    self.X_data=self.X[0:windowWidth]
                    self.X_data = np.array(self.X_data).reshape(-1, windowWidth, 4, 1)
                    pred = model.predict(self.X_data, verbose = 0)
                    # 
                    if np.max(pred)>0.7:
                        # self.save(np.argmax(pred),self.count)
                        # print(pred)
                        sock.SendData(str(np.argmax(pred)))
                        print(np.argmax(pred))
                    self.rest=2
                self.count=0
        finally:
            self.interf.write('e')
            while self.interf.read()!=1:
                pass
            self.interf.end_process()
            time.sleep(1)
main=Main()
main.run()