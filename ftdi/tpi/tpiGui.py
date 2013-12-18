#!/usr/bin/env python
from PyQt4 import QtCore, QtGui
import sys

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class freq_doubleInput(QtGui.QDoubleSpinBox):
    def __init__(self,gui_parent=None):
        QtGui.QDoubleSpinBox.__init__(self, gui_parent)
        self.setRange(35,4400)
        self.setDecimals(3)
        self.setSingleStep(1.0)
        self.setProperty("value",2000)

class scan_widget(QtGui.QWidget):
    def __init__(self,gui_parent=None):
        QtGui.QWidget.__init__(self,gui_parent)

        self.setupUI()

    def setupUI(self):
        self.input_layout = QtGui.QGridLayout()
        self.input_layout.addWidget(QtGui.QLabel("From"),0,0,1,1)
        self.input_layout.addWidget(QtGui.QLabel("To"),0,1,1,1)
        self.input_layout.addWidget(QtGui.QLabel("By"),0,2,1,1)
        self.input_layout.addWidget(QtGui.QLabel("delay(sec)"),0,3,1,1)
        
        self.freq_from = freq_doubleInput()
        self.freq_to = freq_doubleInput()
        self.freq_by = QtGui.QDoubleSpinBox()
        self.freq_by.setProperty("value",10)
        self.freq_delay = QtGui.QDoubleSpinBox()
        self.freq_delay.setProperty("value",.5)
                               
        self.input_layout.addWidget(self.freq_from,1,0,1,1)
        self.input_layout.addWidget(self.freq_to,1,1,1,1)
        self.input_layout.addWidget(self.freq_by,1,2,1,1)
        self.input_layout.addWidget(self.freq_delay,1,3,1,1)

        self.scanButton = QtGui.QPushButton("Scan")
        self.onceButton = QtGui.QPushButton("Once")
        self.stepButton = QtGui.QPushButton("Step")

        self.button_layout = QtGui.QHBoxLayout()
        self.button_layout.addWidget(self.scanButton)
        self.button_layout.addWidget(self.onceButton)
        self.button_layout.addWidget(self.stepButton)
        
        self.comb_layout = QtGui.QVBoxLayout()
        self.comb_layout.addLayout(self.input_layout)
        self.comb_layout.addLayout(self.button_layout)
        
        self.setLayout(self.comb_layout)

class tpiGui(QtGui.QWidget):
    def __init__(self,parent,gui_parent=None):
        QtGui.QDialog.__init__(self, gui_parent)
        self.p = parent       
        self.setupUi()
        self.setup_slots()

    def setupUi(self):
        self.setWindowTitle("TPI Control")
        self.setupFreqUi()
        
        self.fscan_layout = QtGui.QVBoxLayout()
        self.fscan_layout.addWidget(QtGui.QLabel("Frequency Scan (MHz)"))
        self.fscan_widget = scan_widget()
        self.fscan_layout.addWidget(self.fscan_widget)
        
        self.fscan_frame = QtGui.QFrame()
        self.fscan_frame.setFrameStyle(QtGui.QFrame.Panel | QtGui.QFrame.Raised);
        self.fscan_frame.setEnabled(False)
        self.fscan_frame.setLayout(self.fscan_layout)

        self.pscan_layout = QtGui.QVBoxLayout()
        self.pscan_layout.addWidget(QtGui.QLabel("Power Scan (dBm)"))
        self.pscan_widget = scan_widget()
        self.pscan_layout.addWidget(self.pscan_widget)
        
        self.pscan_frame = QtGui.QFrame()
        self.pscan_frame.setFrameStyle(QtGui.QFrame.Panel | QtGui.QFrame.Raised);
        self.pscan_frame.setEnabled(False)
        self.pscan_frame.setLayout(self.pscan_layout)

        self.scan_layout = QtGui.QVBoxLayout()
        self.scan_layout.addWidget(self.fscan_frame)
        self.scan_layout.addWidget(self.pscan_frame)

        self.control_layout = QtGui.QHBoxLayout()
        self.control_layout.addWidget(self.rfcontrol_frame)
        self.control_layout.addLayout(self.scan_layout)

        self.final_layout = QtGui.QVBoxLayout()
        self.final_layout.addWidget(QtGui.QLabel("TPI Control (more info here soon)"))
        self.final_layout.addLayout(self.control_layout)

        self.setLayout(self.final_layout)

    def setupFreqUi(self):
        self.rfcontrol_layout = QtGui.QVBoxLayout()
        self.rfcontrol_layout.addStretch()
        self.rfcontrol_layout.addWidget(QtGui.QLabel("Center Frequency (MHz)"))
        
        self.freq = freq_doubleInput()
        self.rfcontrol_layout.addWidget(self.freq)
        self.rfcontrol_layout.addStretch()

        self.rfcontrol_layout.addWidget(QtGui.QLabel("Output Power"))
        
        self.power = QtGui.QComboBox()
        self.power.addItem("0")
        self.power.addItem("1")
        self.power.addItem("2")
        self.power.addItem("3")
        self.power.setCurrentIndex(3)
        self.rfcontrol_layout.addWidget(self.power)
        self.rfcontrol_layout.addStretch()

        self.rfbutton_layout = QtGui.QHBoxLayout()
        self.rfonButton = QtGui.QPushButton("RF On")
        self.rfonPallete = self.rfonButton.palette().color(1)
        self.rfoffButton = QtGui.QPushButton("RF Off")
        self.rfbutton_layout.addWidget(self.rfonButton)
        self.rfbutton_layout.addWidget(self.rfoffButton)
        
        self.rfcontrol_layout.addLayout(self.rfbutton_layout)
        self.rfcontrol_frame = QtGui.QFrame()
        self.rfcontrol_frame.setFrameStyle(QtGui.QFrame.Panel | QtGui.QFrame.Raised);
        self.rfcontrol_frame.setLayout(self.rfcontrol_layout)
    
    def setup_slots(self):
        QtCore.QObject.connect(self.freq,QtCore.SIGNAL("valueChanged(double)"), self.p.setFreq)
        QtCore.QObject.connect(self.power,QtCore.SIGNAL("currentIndexChanged(int)"), self.p.setPower)
        QtCore.QObject.connect(self.rfonButton,QtCore.SIGNAL("pressed()"), self.rfon_power)
        QtCore.QObject.connect(self.rfoffButton,QtCore.SIGNAL("pressed()"), self.rfoff_power)
        
    def rfon_power(self):
        self.p.setRfOn(True)
        self.rfonButton.setStyleSheet('QPushButton {background-color: yellow}')
        self.rfonButton.setEnabled(False)
        self.rfoffButton.setEnabled(True)

    def rfoff_power(self):
        self.p.setRfOn(False)
        self.rfonButton.setStyleSheet('QPushButton {background-color: self.rfonPallete}')
        self.rfonButton.setEnabled(True)
        self.rfoffButton.setEnabled(False)

