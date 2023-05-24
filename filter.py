from scipy.signal import butter,iirnotch, filtfilt
from numpy import *
import pyqtgraph as pg
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import interface
from PyQt5.QtWidgets import QApplication
from datetime import datetime
import os.path
import sys
def filter(data, notchcut,q,lowcut, highcut, fs, order=4):
    b,a=iirnotch(notchcut,q,fs)
    y = filtfilt(b, a, data)
    # print(y)
    avg = mean(y)
    y = y - avg
    b, a = butter(order, [lowcut, highcut],fs=fs, btype='band')
    y = filtfilt(b, a, y)
    y = abs(y)
    # b, a = butter(order, 3,fs=fs, btype='low')
    # y = filtfilt(b, a, y)
    # print(y)
    return y
def saveData():
    global X
    with open(gestures[gesture]+'_'+datetime.strftime(datetime.now(),'%Y_%m_%d_%H_%M_%S')+'.txt','w') as f:
        f.write('time   channel1    channel2    channel3    channel4    class\n')
        for i in range(windowWidth):
            f.write(str(i))
            f.write('\t')
            for j in range(4):
                f.write(str(round(X[j][i], 3)))
                f.write('\t')
            f.write(str(gesture))
            f.write('\n')
def end():
    interf.write('e')
    interf.end_process()
    sys.exit(0)
def update():
    global curve, ptr, X
    ptr += 1                              # update x position for displaying the curve    
    for i in range(4):
        X[i][:-1]=X[i][1:]   # shift data in the temporal mean 1 sample left    
        value = float(float(interf.read())*5/255)               # read line (single value) from the serial port
        X[i][-1] = value                 # vector containing the instantaneous values  
        filtRes=filter(X[i],60,0.5,10.2,410,1000)
        curve[i].setData(filtRes)        
    QApplication.processEvents()    # you MUST process the plot now
gestures = ['gesture0','gesture1','gesture2']
gesture = int(input("Gesture: ")) # use integer for gesture type
interf = interface.interface()
app = QApplication(sys.argv)
layout = QVBoxLayout()
win = pg.GraphicsLayoutWidget(title="Signal from arduino") # creates a window
p1 = win.addPlot(title="channel1",row=0, col=0)  # creates empty space for the plot in the window
p2 = win.addPlot(title="channel2",row=1, col=0)  # creates empty space for the plot in the window
p3 = win.addPlot(title="channel3",row=2, col=0)  # creates empty space for the plot in the window
p4 = win.addPlot(title="channel4",row=3, col=0)  # creates empty space for the plot in the window
layout.addWidget(win)
saveBtn = QPushButton('save')
saveBtn.clicked.connect(saveData)
layout.addWidget(saveBtn)
endBtn = QPushButton('end')
endBtn.clicked.connect(end)
layout.addWidget(endBtn)
p1.setYRange(0, 5, padding=0)
p2.setYRange(0, 5, padding=0)
p3.setYRange(0, 5, padding=0)
p4.setYRange(0, 5, padding=0)
curve=[p1.plot(),p2.plot(),p3.plot(),p4.plot()]
windowWidth = 1000                      # width of the window displaying the curve
X =[linspace(0,0,windowWidth),linspace(0,0,windowWidth),linspace(0,0,windowWidth),linspace(0,0,windowWidth)]
# X=[np.random.uniform(low=0, high=5, size=windowWidth),np.random.uniform(low=0, high=5, size=windowWidth),np.random.uniform(low=0, high=5, size=windowWidth),np.random.uniform(low=0, high=5, size=windowWidth)]
ptr = -windowWidth                      # set first x position
interf.write('s')
window = QMainWindow()
wid = QWidget()
window.setCentralWidget(wid)
wid.setLayout(layout)
window.show()
while(1):
    update()
sys.exit(app.exec_())
