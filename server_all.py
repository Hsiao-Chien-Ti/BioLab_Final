import pyqtgraph as pg
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QApplication
import UdpComms as U
import time
import interface
from keras import models
import numpy as np
import sys
model = models.load_model('model_2023_05_26_16_07_54.h5')
sock = U.UdpComms(udpIP="127.0.0.1", portTX=8000, portRX=8001,
                enableRX=True, suppressWarnings=True)
start = 0
interf = [interface.interface("COM42")]
windowWidth = 1000
skillLength = 4
gestureResult=[]
skillSequence=[[0,1,2,3],[1,3,0,2],[1,2,0,1]]
skills=['attack1','attack2','attack3']
turn=1
X =[np.linspace(0,0,windowWidth),np.linspace(0,0,windowWidth),np.linspace(0,0,windowWidth),np.linspace(0,0,windowWidth)]
# class Worker(QThread):
#     global X
#     data1 = pyqtSignal(object)
#     data2 = pyqtSignal(object)
#     data3 = pyqtSignal(object)
#     data4 = pyqtSignal(object)
#     def __init__(self):
#         super().__init__()
#         interf[turn-1].write('s')
#     def run(self):
#         while(1):
#             X_all=[]
#             for i in range(4):
#                 X[i][:-1]=X[i][1:]   # shift data in the temporal mean 1 sample left    
#                 value = float(float(interf[turn-1].read())*5/255)               # read line (singl value) from the serial port
#                 X[i][-1] = value
#                 X_all.append(X[i])
#     # print(len(X_all[0]))
#             X_data = np.array(X_all).reshape(-1, 1000, 4, 1)
#             pred = model.predict(X_data)
#             print(pred)
#             self.data1.emit(X[0])
#             self.data2.emit(X[1])
#             self.data3.emit(X[2])
#             self.data4.emit(X[3])
# class Graph(QWidget):
#     def __init__(self):
#         super().__init__()
#         self.layout = QVBoxLayout(self)
#         self.graph1 = pg.PlotWidget()
#         self.graph2 = pg.PlotWidget()
#         self.graph3 = pg.PlotWidget()
#         self.graph4 = pg.PlotWidget()
#         self.graph1.setYRange(0,5)
#         self.graph2.setYRange(0,5)
#         self.graph3.setYRange(0,5)
#         self.graph4.setYRange(0,5)
#         self.plot1 = self.graph1.plot()
#         self.plot2 = self.graph2.plot()
#         self.plot3 = self.graph3.plot()
#         self.plot4 = self.graph4.plot()
#         self.layout.addWidget(self.graph1)
#         self.layout.addWidget(self.graph2)
#         self.layout.addWidget(self.graph3)
#         self.layout.addWidget(self.graph4)
#         # self.saveBtn = QPushButton('save')
#         # self.saveBtn.clicked.connect(saveData)
#         # self.layout.addWidget(self.saveBtn)
#         # endBtn = QPushButton('end')
#         # endBtn.clicked.connect(end)
#         # self.layout.addWidget(endBtn)
#         self.show()

#     def make_connection(self, data_object):
#         data_object.data1.connect(self.grab_data1)
#         data_object.data2.connect(self.grab_data2)
#         data_object.data3.connect(self.grab_data3)
#         data_object.data4.connect(self.grab_data4)

#     @pyqtSlot(object)
#     def grab_data1(self, data):
#         self.plot1.setData(data)
#     @pyqtSlot(object)
#     def grab_data2(self, data):
#         self.plot2.setData(data)
#     @pyqtSlot(object)
#     def grab_data3(self, data):
#         self.plot3.setData(data)
#     @pyqtSlot(object)
#     def grab_data4(self, data):
#         self.plot4.setData(data)
def update():
    global X,model,gestureResult
    X_all=[]
    flag=1
    for i in range(4):
        X[i][:-1]=X[i][1:]   # shift data in the temporal mean 1 sample left    
        value = float(float(interf[turn-1].read())*5/255)               # read line (single value) from the serial port
        X[i][-1] = value                 # vector containing the instantaneous values  
        X_all.append(X[i])
        if X[i][500]==0:
            flag=0
    # print(len(X_all[0]))
    X_data = np.array(X_all).reshape(-1, 1000, 4, 1)
    # print(X_data.shape)
    if(flag):
        pred = model.predict(X_data,verbose = 0)
        # print(pred)
        if np.max(pred)>0.7:
            print(np.argmax(pred))
            X =[np.linspace(0,0,windowWidth),np.linspace(0,0,windowWidth),np.linspace(0,0,windowWidth),np.linspace(0,0,windowWidth)]
            if np.argmax(pred)!=6:
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
    # interf[turn-1].write('e')
    # turn = (2 if turn==1 else 1)
    # interf[turn-1].write('s')
    gestureResult=[]
print('python server running')
# app = QApplication(sys.argv)
# widget = Graph()
# worker = Worker()
# widget.make_connection(worker)
# worker.start()
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
        # start=0
    if start:
        update()
    # time.sleep(1)
# sys.exit(app.exec_())