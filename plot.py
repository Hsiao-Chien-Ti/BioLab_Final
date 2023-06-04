import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt
def filter(data):
    b, a = butter(4, 50,fs=1000, btype='low')
    y = filtfilt(b, a, data)
    y=abs(y)
    # return y
    return data
path = "training_data/new/rest/"
prev_class=-1
files=os.listdir(path)
for f in files:
    plt.ylim(1.5,3,5)
    path_txt = os.path.join(path, f)
    df = pd.read_csv(path_txt, delimiter = "\t")
    # if prev_class==df['class'][0]:
    #     continue
    prev_class = df['class'][0]
    df=df.drop(columns=['time'])
    df=df.drop(columns=['class'])

    for k in df.keys():
        df[k]=filter(df[k])
        plt.plot(df[k],label=k)
    plt.title(f)
    plt.legend(loc='lower right')
    plt.ylabel('V(V)')
    plt.xlabel('time(ms)')
    plt.savefig('training_data/plot/new/rest/{}.png'.format(f))
    plt.figure()
