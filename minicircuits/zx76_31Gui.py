#!/usr/bin/env python
from PyQt4 import QtCore, QtGui
import sys

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class zx76_31Gui(QtGui.QWidget):
    def __init__(self,parent,gui_parent=None):
        QtGui.QDialog.__init__(self, gui_parent)
        self.p = parent    
        self.setupUi()
        self.setup_slots()

    def setupUi(self):
        self.setWindowTitle(self.p.getName())
        
        self.layout = QtGui.QHBoxLayout()
        self.layout.addWidget(QtGui.QLabel("Attenuation (dB)"))
        self.atten_val = QtGui.QSpinBox()
        self.atten_val.setRange(0,31)
        self.layout.addWidget(self.atten_val)
        
        self.frame = QtGui.QFrame()
        self.frame.setFrameStyle(QtGui.QFrame.Panel | QtGui.QFrame.Raised);
        self.frame.setLayout(self.layout)
        #self.final_layout = QtGui.QVBoxLayout()
        #self.final_layout.addWidget(self.fs_frame)

        self.setLayout(self.frame.layout())

    def setup_slots(self):
        QtCore.QObject.connect(self.atten_val,QtCore.SIGNAL("valueChanged(int)"), self.p.setatten)
        
