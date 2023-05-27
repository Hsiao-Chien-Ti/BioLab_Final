import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt
def filter(data):
    b, a = butter(4, 100,fs=1000, btype='low')
    y = filtfilt(b, a, data)
    y=abs(y)
    return y
path = "training_data"
files=os.listdir(path)
Y_data = np.array([]) 
X_data = np.zeros((0,1000,4))
prev_class=-1
for f in files:
    path_txt = os.path.join(path, f)
    df = pd.read_csv(path_txt, delimiter = "\t")
    if df['class'][0]!=prev_class:
        prev_class=df['class'][0]
        count=0
    if count>5: 
        continue
    count+=1
    Y_data=np.append(Y_data,df['class'][0])
    df=df.drop(columns=['time'])
    df=df.drop(columns=['class'])
    for k in df.keys():
        df[k]=filter(df[k])
        plt.plot(df[k],label=k)
    df=df.to_numpy().reshape(1,1000,4)
    X_data = np.concatenate((X_data,df) )
    plt.title(f)
    plt.legend(loc='lower right')
    plt.ylabel('V(V)')
    plt.xlabel('time(ms)')
    plt.savefig('training_data/plot/{}.png'.format(f))
    plt.figure()
