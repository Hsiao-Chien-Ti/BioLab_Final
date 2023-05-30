import numpy as np
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import interface
from keras import models
import UdpComms as U
import time
from scipy.signal import butter, filtfilt
model = models.load_model('model_2023_05_29_14_20_18.h5')
windowWidth = 2000
def filter(data):
    b, a = butter(4, 50,fs=1000, btype='low')
    y = filtfilt(b, a, data)
    y=abs(y)
    return y
class Main():    
    def __init__(self):
        self.start=0
        super().__init__()
        self.interf = interface.interface("COM42")
        print('python server running')
        self.interf.write('s')
        self.X =[np.linspace(0,0,windowWidth),np.linspace(0,0,windowWidth),np.linspace(0,0,windowWidth),np.linspace(0,0,windowWidth)]
    def run(self):
        self.count=0
        try:
            while True:
                for i in range(4):
                    self.X[i][:-1]=self.X[i][1:]   # shift data in the temporal mean 1 sample left    
                    value = float(float(self.interf.read())*5/255)               # read line (single value) from the serial port
                    self.X[i][-1] = value                 # vector containing the instantaneous values  
                self.count+=1
                if(self.count<200):
                    continue
                self.X_tmp = []
                for i in range(4):
                    self.X_tmp.append(filter(self.X[i]))
                self.X_data = np.array(self.X_tmp).reshape(-1, 2000, 4, 1)
                pred = model.predict(self.X_data,verbose = 0)
                # print(pred)
                if np.max(pred)>0.7:
                    print(np.argmax(pred))
                    # self.X =[np.linspace(0,0,windowWidth),np.linspace(0,0,windowWidth),np.linspace(0,0,windowWidth),np.linspace(0,0,windowWidth)]
                self.count=0
        finally:
            self.interf.write('e')
            while self.interf.read()!=1:
                pass
            self.interf.end_process()
            time.sleep(1)
main=Main()
main.run()