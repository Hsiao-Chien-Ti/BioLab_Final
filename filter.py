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
import time
gestures = ['gesture0','gesture1','gesture2','gesture3','gesture4','gesture5','gesture6','gesture7']
gesture = int(input("Gesture: ")) # use integer for gesture type
windowWidth = 1500 #2000                      # width of the window displaying the curve
savePeriod = 2750 #3000
class Worker(QThread):    
    data1 = pyqtSignal(object)
    data2 = pyqtSignal(object)
    data3 = pyqtSignal(object)
    data4 = pyqtSignal(object)
    leave = pyqtSignal(object)
    do =pyqtSignal(object)
    def __init__(self):
        super().__init__()
        self.interf = interface.interface("COM42")
        self.interf.write('s')
        self.X =[np.linspace(0,0,windowWidth),np.linspace(0,0,windowWidth),np.linspace(0,0,windowWidth),np.linspace(0,0,windowWidth)]
        self.running=1
        self.saving=0
    def run(self):
        self.count=0
        self.timer=-1
        while(self.running):
            for i in range(4):
                self.X[i][:-1]=self.X[i][1:]   # shift data in the temporal mean 1 sample left    
                value = float(float(self.interf.read())*5/255)               # read line (singl value) from the serial port
                self.X[i][-1] = value
            self.count+=1
            self.timer+=1
            if self.timer==0:
                self.do.emit('relax1')
            elif self.timer==1000:
                self.do.emit('start')
            elif self.timer==2500: 
                self.do.emit('relax2')
            elif self.timer==3499: 
                self.timer=-1
            if self.saving:
                self.save()
                self.saving=0
            # if(self.timer>2999):
            #     self.save(1)
            #     self.timer=0
            if(self.count<10):
                continue
            self.data1.emit(self.X[0])
            self.data2.emit(self.X[1])
            self.data3.emit(self.X[2])
            self.data4.emit(self.X[3])
            self.count=0
        self.interf.write('e')
        while self.interf.read()!=1:
            pass
        self.interf.end_process()
        time.sleep(1)
        self.leave.emit(1)
        # sys.exit(0)
        # self.exit()
    def make_connection(self, data_object):
        data_object.saving.connect(self.toggleSaving)
        data_object.end.connect(self.end)
    def save(self):
        with open('training_data/new/'+gestures[gesture]+'_'+datetime.strftime(datetime.now(),'%Y_%m_%d_%H_%M_%S')+'.txt','w') as f:
            f.write('time\tchannel1\tchannel2\tchannel3\tchannel4\tclass\n')
            for i in range(windowWidth):
                f.write(str(i))
                f.write('\t')
                for j in range(4):
                    f.write(str(round(self.X[j][i], 3)))
                    f.write('\t')
                f.write(str(gesture))
                f.write('\n')
    @pyqtSlot(object)
    def toggleSaving(self,tog):
        self.saving=not self.saving

    @pyqtSlot(object)
    def end(self, end):
        if end == 1:
            self.running=0
            
    
class Graph(QWidget):
    saving=pyqtSignal(object)
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
        
        self.saveBtn = QPushButton('save')
        self.saveBtn.clicked.connect(self.toggleSaving)
        self.layout.addWidget(self.saveBtn)
        # self.saveBtn = QPushButton('save')
        # self.saveBtn.clicked.connect(self.saveData)
        # self.layout.addWidget(self.saveBtn)
        
        self.instruction = QLabel('0')
        self.instruction.setFont(QFont('Arial', 20))
        # self.layout.addWidget(self.instruction)
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
        data_object.do.connect(self.do)
    def toggleSaving(self):
        # print(self.saveBtn.text())
        pass
        self.saving.emit(1)
    def endProgram(self):
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
    @pyqtSlot(object)
    def do(self, data):
        self.instruction.setText(data)
    
app = QApplication(sys.argv)
widget = Graph()
worker = Worker()
widget.make_connection(worker)
worker.make_connection(widget)
worker.start()
sys.exit(app.exec_())
