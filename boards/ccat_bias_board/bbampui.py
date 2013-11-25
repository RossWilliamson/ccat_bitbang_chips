from PyQt4 import QtCore, QtGui,Qt
import QLed
import sys

class drain_doubleInput(QtGui.QDoubleSpinBox):
    def __init__(self,gui_parent=None):
        QtGui.QDoubleSpinBox.__init__(self, gui_parent)

        self.setRange(0,5)
        self.setDecimals(2)
        self.setSingleStep(0.01)

class gate_doubleInput(QtGui.QDoubleSpinBox):
    def __init__(self,gui_parent=None):
        QtGui.QDoubleSpinBox.__init__(self, gui_parent)

        self.setRange(-5,5)
        self.setDecimals(2)
        self.setSingleStep(0.01)


class amp_widget(QtGui.QWidget):
    def __init__(self,data_class,index,gui_parent=None):
        QtGui.QWidget.__init__(self,gui_parent)

        self.p = data_class
        self.index = index

        self.setupUI()
        self.setup_slots()

    def setupUI(self):
        self.amp_layout = QtGui.QGridLayout()
        
        self.set_label = QtGui.QLabel("Setpoint")
        self.v_label = QtGui.QLabel("Volts (V)")
        self.i_label = QtGui.QLabel("I (mA)")

        self.amp_layout.addWidget(self.set_label,0,1,1,1)
        self.amp_layout.addWidget(self.v_label,0,2,1,1)
        self.amp_layout.addWidget(self.i_label,0,3,1,1)

        self.drain_label = QtGui.QLabel("Drain")
        self.drain_set = drain_doubleInput()
        self.drain_v_val = QtGui.QLabel("0")
        self.drain_i_val = QtGui.QLabel("0")
        self.amp_layout.addWidget(self.drain_label,1,0,1,1)
        self.amp_layout.addWidget(self.drain_set,1,1,1,1)
        self.amp_layout.addWidget(self.drain_v_val,1,2,1,1)
        self.amp_layout.addWidget(self.drain_i_val,1,3,1,1)


        self.gatea_label = QtGui.QLabel("GA")
        self.gatea_set = gate_doubleInput()
        self.gatea_v_val = QtGui.QLabel("0")
        self.gatea_i_val = QtGui.QLabel("0")
        self.amp_layout.addWidget(self.gatea_label,2,0,1,1)
        self.amp_layout.addWidget(self.gatea_set,2,1,1,1)
        self.amp_layout.addWidget(self.gatea_v_val,2,2,1,1)
        self.amp_layout.addWidget(self.gatea_i_val,2,3,1,1)

        self.gateb_label = QtGui.QLabel("GB")
        self.gateb_set = gate_doubleInput()
        self.gateb_v_val = QtGui.QLabel("0")
        self.gateb_i_val = QtGui.QLabel("0")
        self.amp_layout.addWidget(self.gateb_label,3,0,1,1)
        self.amp_layout.addWidget(self.gateb_set,3,1,1,1)
        self.amp_layout.addWidget(self.gateb_v_val,3,2,1,1)
        self.amp_layout.addWidget(self.gateb_i_val,3,3,1,1)

        self.amp_layout.setRowMinimumHeight(4,15)
        self.amp_layout.setRowStretch(4,1)

        self.power_button = QtGui.QPushButton("Power")
        self.power_button.setCheckable(True)

        self.amp_led  = QLed.QLed(self,onColour=QLed.QLed.Green, offColour=QLed.QLed.Red)
        self.amp_layout.addWidget(self.power_button,5,1,1,2)
        self.amp_layout.addWidget(self.amp_led,5,3,1,1)
        
        self.setLayout(self.amp_layout)
        #self.show()

    def setup_slots(self):
        QtCore.QObject.connect(self.drain_set,QtCore.SIGNAL("valueChanged(double)"), self.call_drain_set)
        QtCore.QObject.connect(self.gatea_set,QtCore.SIGNAL("valueChanged(double)"), self.call_gatea_set)
        QtCore.QObject.connect(self.gateb_set,QtCore.SIGNAL("valueChanged(double)"), self.call_gateb_set)
        QtCore.QObject.connect(self.power_button,QtCore.SIGNAL("toggled(bool)"), self.call_power)

    def call_drain_set(self,val):
        self.p.setAmp(self.index,"drain",val)

    def call_gatea_set(self,val):
        self.p.setAmp(self.index,"gatea",val)

    def call_gateb_set(self,val):
        self.p.setAmp(self.index,"gateb",val)

    def call_power(self,state):
        self.p.setPower(self.index, state)
        self.amp_led.setValue(state)

    def update_monitor(self):
        self.drain_v_val.setText(QtCore.QString.number(self.p.drains[self.index]["V"],"f",3))
        self.drain_i_val.setText(QtCore.QString.number(self.p.drains[self.index]["I"],"f",3))
        self.gatea_v_val.setText(QtCore.QString.number(self.p.gatea[self.index]["V"],"f",3))
        self.gatea_i_val.setText(QtCore.QString.number(self.p.gatea[self.index]["I"],"f",3))
        self.gateb_v_val.setText(QtCore.QString.number(self.p.gateb[self.index]["V"],"f",3))
        self.gateb_i_val.setText(QtCore.QString.number(self.p.gateb[self.index]["I"],"f",3))

def main():
    app = QtGui.QApplication(sys.argv)
    ex = amp_widget()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
