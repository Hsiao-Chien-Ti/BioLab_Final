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
def filter(data):
    b, a = butter(4, 100,fs=1000, btype='low')
    y = filtfilt(b, a, data)
    return data
# np.set_printoptions(threshold=sys.maxsize)
model = models.load_model('model_2023_05_29_17_52_08.h5')
rest_model = models.load_model('exist_model_2023_05_30_17_00_19.h5')
windowWidth = 1500
subWindowWidth = 100
path = "training_data/hidden_new"
path_rest = "gesture6_2023_05_29_07_53_18.txt"
files=os.listdir(path)
Y_data = np.array([])
rest = pd.read_csv(path_rest, delimiter = "\t")
Y_data=np.append(Y_data,rest['class'][0])
rest=rest.drop(columns=['time'])
rest=rest.drop(columns=['class'])
for k in rest.keys():
    rest[k]=filter(rest[k])
# rest=rest.to_numpy()[250:1750].reshape(1500,4)
rest=rest.to_numpy().reshape(2000,4)

path_txt = os.path.join(path, files[0])
X_data = pd.read_csv(path_txt, delimiter = "\t")
Y_data=np.append(Y_data,X_data['class'][0])
X_data=X_data.drop(columns=['time'])
X_data=X_data.drop(columns=['class'])
for k in X_data.keys():
    X_data[k]=filter(X_data[k])
# X_data=X_data.to_numpy()[250:1750].reshape(1500,4)
X_data=X_data.to_numpy().reshape(2000,4)

for f in files:
    if f == files[0]:
        continue
    X_data = np.concatenate((X_data,rest))
    path_txt = os.path.join(path, f)
    df = pd.read_csv(path_txt, delimiter = "\t")
    Y_data=np.append(Y_data,df['class'][0])
    df=df.drop(columns=['time'])
    df=df.drop(columns=['class'])
    for k in df.keys():
        df[k]=filter(df[k])    
    df=df.to_numpy().reshape(2000,4)
    # df=df.to_numpy()[250:1750].reshape(1500,4)
    X_data = np.concatenate((X_data,df))
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
                pred = rest_model.predict(self.X_data, verbose = 0)
                if(np.argmax(pred)==1 or (np.argmax(pred)==0 and np.max(pred)<0.9)):
                    self.rest=0
                    nxt-=subWindowWidth
            else:
                if(nxt+windowWidth>=X_data.shape[0]):
                    break
                self.X=X_data[nxt:nxt+windowWidth]
                print(nxt)
                nxt+=windowWidth
                self.X_data = np.array(self.X).reshape(-1, windowWidth, 4, 1)
                pred = model.predict(self.X_data, verbose = 0)
                # print(pred)
                # if np.max(pred)>0.8:
                print(np.argmax(pred))
                self.rest=1

main=Main()
main.run()