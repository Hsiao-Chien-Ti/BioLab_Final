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
import matplotlib.pyplot as plt
def filter(data):
    b, a = butter(4, 100,fs=1000, btype='low')
    y = filtfilt(b, a, data)
    return data
# np.set_printoptions(threshold=sys.maxsize)
model = models.load_model('model_2023_05_30_22_56_52.h5')
rest_model = models.load_model('exist_model_2023_05_30_23_04_12.h5')
windowWidth = 1500
subWindowWidth = 100
path = '2023_05_31_01_06_01.txt'
X_data = pd.read_csv(path, delimiter = "\t")
# X_data=X_data.drop(columns=['time'])
X_data=X_data.drop(columns=['class'])
for k in X_data.keys():
    plt.plot(X_data[k],label=k)
X_data=X_data.to_numpy()
print(X_data.shape)
class Main():    
    def __init__(self):
        self.start=0
        super().__init__()
        self.X =[np.linspace(0,0,windowWidth),np.linspace(0,0,windowWidth),np.linspace(0,0,windowWidth),np.linspace(0,0,windowWidth)]
    def run(self):
        self.count=0
        nxt=0
        self.rest=1
        while 1:
            if(self.rest):
                if(nxt+subWindowWidth>=X_data.shape[0]):
                    break
                self.X=X_data[nxt:nxt+subWindowWidth]
                # print(self.X.shape)
                nxt+=subWindowWidth
                self.X_data = np.array(self.X).reshape(-1, subWindowWidth, 4, 1)
                out=0
                for i in range(subWindowWidth):
                    if(self.X_data[0][i][0][0]>2.3 or self.X_data[0][i][0][0]<1.7):
                        out+=1
                # print(self.X_data.shape)
                # filter_arr = self.X_data[0]>2.4 or self.X_data[0]<1.6
                # out= len(self.X_data[0][filter_arr])
                # pred = rest_model.predict(self.X_data, verbose = 0)
                # if(np.argmax(pred)==1 or (np.argmax(pred)==0 and np.max(pred)<0.9)):
                if(out>5):
                    self.rest=0
                    nxt-=subWindowWidth
                    plt.scatter([nxt],[4])
            else:
                if(nxt+windowWidth>=X_data.shape[0]):
                    break
                self.X=X_data[nxt-200:nxt-200+windowWidth]
                print(nxt)
                nxt+=2500
                self.X_data = np.array(self.X).reshape(-1, windowWidth, 4, 1)
                pred = model.predict(self.X_data, verbose = 0)
                print(pred)
                # if np.max(pred)>0.8:
                print(np.argmax(pred))
                self.rest=1

main=Main()
main.run()
plt.savefig('result.png')