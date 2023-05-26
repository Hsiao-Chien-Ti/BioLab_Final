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
gestures = ['gesture0','gesture1','gesture2','gesture3','gesture4','gesture5','gesture6']
gesture = int(input("Gesture: ")) # use integer for gesture type
interf = interface.interface("COM42")

windowWidth = 1000                      # width of the window displaying the curve
X =[np.linspace(0,0,windowWidth),np.linspace(0,0,windowWidth),np.linspace(0,0,windowWidth),np.linspace(0,0,windowWidth)]

class Worker(QThread):
    global X
    data1 = pyqtSignal(object)
    data2 = pyqtSignal(object)
    data3 = pyqtSignal(object)
    data4 = pyqtSignal(object)
    def __init__(self):
        super().__init__()
        interf.write('s')
    def run(self):
        while(1):
            for i in range(4):
                X[i][:-1]=X[i][1:]   # shift data in the temporal mean 1 sample left    
                value = float(float(interf.read())*5/255)               # read line (singl value) from the serial port
                X[i][-1] = value
            self.data1.emit(X[0])
            self.data2.emit(X[1])
            self.data3.emit(X[2])
            self.data4.emit(X[3])
class Graph(QWidget):
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
        self.saveBtn.clicked.connect(saveData)
        self.layout.addWidget(self.saveBtn)
        endBtn = QPushButton('end')
        endBtn.clicked.connect(end)
        self.layout.addWidget(endBtn)
        self.show()

    def make_connection(self, data_object):
        data_object.data1.connect(self.grab_data1)
        data_object.data2.connect(self.grab_data2)
        data_object.data3.connect(self.grab_data3)
        data_object.data4.connect(self.grab_data4)

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
def saveData():
    global X
    with open('training_data/'+gestures[gesture]+'_'+datetime.strftime(datetime.now(),'%Y_%m_%d_%H_%M_%S')+'.txt','w') as f:
        f.write('time\tchannel1\tchannel2\tchannel3\tchannel4\tclass\n')
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
    worker.terminate()
    interf.end_process()
    sys.exit(0)
app = QApplication(sys.argv)
widget = Graph()
worker = Worker()
widget.make_connection(worker)
worker.start()
sys.exit(app.exec_())
