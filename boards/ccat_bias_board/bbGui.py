#!/usr/bin/env python
from PyQt4 import QtCore, QtGui
from bbampui import *

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s


class bbGui(QtGui.QDialog):
    def __init__(self,parent,gui_parent=None):
        QtGui.QDialog.__init__(self, gui_parent)
        self.p = parent
        self.update_timer = QtCore.QTimer()
        
        self.setupUi()
        self.setup_slots()

        self.update_timer.start(500)

    def setupUi(self):
        self.setWindowTitle("MMIC Amplifier Control")
        self.amp1_frame = QtGui.QGroupBox("AMP 1",self)
        self.amp2_frame = QtGui.QGroupBox("AMP 2",self)
        self.amp3_frame = QtGui.QGroupBox("AMP 3",self)
        self.amp4_frame = QtGui.QGroupBox("AMP 4",self)

        self.amp1_layout = QtGui.QVBoxLayout()
        self.amp2_layout = QtGui.QVBoxLayout()
        self.amp3_layout = QtGui.QVBoxLayout()
        self.amp4_layout = QtGui.QVBoxLayout()

        self.amp1_widget = amp_widget(self.p, 0)
        self.amp2_widget = amp_widget(self.p, 1)
        self.amp3_widget = amp_widget(self.p, 2)
        self.amp4_widget = amp_widget(self.p, 3)
        
        self.amp1_layout.addWidget(self.amp1_widget)
        self.amp2_layout.addWidget(self.amp2_widget)
        self.amp3_layout.addWidget(self.amp3_widget)
        self.amp4_layout.addWidget(self.amp4_widget)

        self.amp1_frame.setLayout(self.amp1_layout)
        self.amp2_frame.setLayout(self.amp2_layout)
        self.amp3_frame.setLayout(self.amp3_layout)
        self.amp4_frame.setLayout(self.amp4_layout)

        self.amp_layout = QtGui.QGridLayout()
        self.amp_layout.addWidget(self.amp1_frame,0,0,1,1)
        self.amp_layout.addWidget(self.amp2_frame,0,1,1,1)
        self.amp_layout.addWidget(self.amp3_frame,1,0,1,1)
        self.amp_layout.addWidget(self.amp4_frame,1,1,1,1)

        self.latch_button = QtGui.QPushButton("Set Biases")
        self.amp_layout.addWidget(self.latch_button,2,1,1,1)

        self.setLayout(self.amp_layout)

    def setup_slots(self):
        QtCore.QObject.connect(self.update_timer, QtCore.SIGNAL("timeout()"), self.update_data)
        QtCore.QObject.connect(self.latch_button,QtCore.SIGNAL("clicked()"), self.p.latchDaq)

    def update_data(self):
        self.p.fetchDict()
        self.amp1_widget.update_monitor()
        self.amp2_widget.update_monitor()
        self.amp3_widget.update_monitor()
        self.amp4_widget.update_monitor()

        #self.p.printData()
