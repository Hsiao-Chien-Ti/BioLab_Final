from PyQt5.QtCore import QObject
import numpy as np
import pyqtgraph as pg
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import interface
from PyQt5.QtWidgets import QApplication
from datetime import datetime
import sys
from keras import models
import UdpComms as U
import time
model = models.load_model('model_2023_05_27_10_44_09.h5')
sock = U.UdpComms(udpIP="127.0.0.1", portTX=8000, portRX=8001,
                enableRX=True, suppressWarnings=True)
start = 0
turn=1
# interf = [interface.interface("COM17")]
skillSequence=[[0,1,2,3],[1,3,0,2],[1,2,0,1]]
skills=['attack1','attack2','attack3']
windowWidth = 1000 
skillLength = 4
class Worker(QThread):    
    data1 = pyqtSignal(object)
    data2 = pyqtSignal(object)
    data3 = pyqtSignal(object)
    data4 = pyqtSignal(object)
    leave = pyqtSignal(object)
    def __init__(self):
        super().__init__()
        self.interf = [interface.interface("COM17")]
        self.interf[turn-1].write('s')
        self.X =[np.linspace(0,0,windowWidth),np.linspace(0,0,windowWidth),np.linspace(0,0,windowWidth),np.linspace(0,0,windowWidth)]
        self.running=1
        self.gestureResult=[]
    def run(self):
        self.count=0
        while(self.running):
            self.X_all=[]
            flag=1
            for i in range(4):
                self.X[i][:-1]=self.X[i][1:]   # shift data in the temporal mean 1 sample left    
                value = float(float(self.interf[turn-1].read())*5/255)               # read line (single value) from the serial port
                self.X[i][-1] = value                 # vector containing the instantaneous values  
                self.X_all.append(self.X[i])
                if self.X[i][500]==0:
                    flag=0
            self.count+=1
            self.X_data = np.array(self.X_all).reshape(-1, 1000, 4, 1)
            # print(self.X_data.shape)
            if(flag):
                # print(self.X_data)
                pred = model.predict(self.X_data,verbose = 0)
                # print(pred)
                if np.max(pred)>0.7:
                    print(np.argmax(pred))
                    # self.X =[np.linspace(0,0,windowWidth),np.linspace(0,0,windowWidth),np.linspace(0,0,windowWidth),np.linspace(0,0,windowWidth)]
                    # self.X_all=[]
                    # if np.argmax(pred)!=6:
                    #     self.gestureResult.append(np.argmax(pred))
                    #     if len(self.gestureResult)==skillLength:
                    #         self.autoCalibration()
            if(self.count<5):
                continue
            self.data1.emit(self.X[0])
            self.data2.emit(self.X[1])
            self.data3.emit(self.X[2])
            self.data4.emit(self.X[3])
            self.count=0
        
        self.interf[turn-1].write('e')
        self.interf[turn-1].end_process()
        print('worker leave')
        time.sleep(1)
        self.leave.emit(1)
        # sys.exit(0)
        # self.exit()
    def autoCalibration(self):
        skill=0
        maxSimilarity=0
        for i in range(len(skillSequence)):
            similarity=0
            for j in range(skillLength):
                if skills[i][j]==self.gestureResult[j]:
                    similarity+=1
            if similarity>maxSimilarity:
                maxSimilarity=similarity
                skill=i
        sock.SendData(str(turn)+skills[skill])
    # interf[turn-1].write('e')
    # turn = (2 if turn==1 else 1)
    # interf[turn-1].write('s')
    gestureResult=[]
    def make_connection(self, data_object):
        data_object.end.connect(self.end)
    @pyqtSlot(object)
    def end(self, end):
        if end == 1:
            self.running=0
            
    
class Graph(QWidget):
    end=pyqtSignal(object)
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.graph1 = pg.PlotWidget()
        self.graph2 = pg.PlotWidget()
        self.graph3 = pg.PlotWidget()
        self.graph4 = pg.PlotWidget()
        self.graph1.setYRange(0,5)
        self.graph2.setYRange(0,5)
        self.graph3.setYRange(0,5)
        self.graph4.setYRange(0,5)
        self.plot1 = self.graph1.plot()
        self.plot2 = self.graph2.plot()
        self.plot3 = self.graph3.plot()
        self.plot4 = self.graph4.plot()
        self.layout.addWidget(self.graph1)
        self.layout.addWidget(self.graph2)
        self.layout.addWidget(self.graph3)
        self.layout.addWidget(self.graph4)
        endBtn = QPushButton('end')
        endBtn.clicked.connect(self.endProgram)
        self.layout.addWidget(endBtn)
        self.show()

    def make_connection(self, data_object):
        data_object.data1.connect(self.grab_data1)
        data_object.data2.connect(self.grab_data2)
        data_object.data3.connect(self.grab_data3)
        data_object.data4.connect(self.grab_data4)
        data_object.leave.connect(self.terminate)
    def endProgram(self):
        print('click end')
        self.end.emit(1)
    @pyqtSlot(object)
    def grab_data1(self, data):
        self.plot1.setData(data)
    @pyqtSlot(object)
    def grab_data2(self, data):
        self.plot2.setData(data)
    @pyqtSlot(object)
    def grab_data3(self, data):
        self.plot3.setData(data)
    @pyqtSlot(object)
    def grab_data4(self, data):
        self.plot4.setData(data)
    @pyqtSlot(object)
    def terminate(self, data):
        if data==1:
            sys.exit(0)
app = QApplication(sys.argv)
widget = Graph()
worker = Worker()
widget.make_connection(worker)
worker.make_connection(widget)
worker.start()
sys.exit(app.exec_())