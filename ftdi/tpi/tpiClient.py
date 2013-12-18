#!/usr/bin/env python
import network.tcpClient as tp
import simplejson as json
import logging
import struct
import argparse
import sys

from tpiGui import *
logging.basicConfig()

class tpiClient():
    def __init__(self, hostname="bbone", port=50010):
        self.logger = logging.getLogger('tpiClient')
        self.logger.setLevel(logging.DEBUG)
        self.conn = tp.tcpClient(hostname,port,terminator="\r\n")
        self.local_terminator = "\r\n"

    def send(self,msg):
        self.conn.send(msg)
        
    def setPower(self,power):
        self.checkPower(power)
        if power is not None:
            msg = "set power %i" % (power)
            self.send(msg)

    def setFreq(self,freq):
        msg = "set freq %f" % (freq)
        self.send(msg)
        
    def setRfOn(self,state):
        if state is True:
            st = 1
        else:
            st = 0

        msg = "set rfon %i" % (st)
        self.send(msg)

    def checkPower(self,power):
        if power < 0 or  power > 3:
            self.logger.error("Power has to be integer between 0 and 3")
            return None
        return power

    def launch_gui(self):
        self.app = QtGui.QApplication(sys.argv)
        self.gui = tpiGui(self)
        self.gui.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--hostname", help="Hostname to connect to",
                        default="bbone")
    parser.add_argument("-p", "--port", help="Port number to connect to",
                        default=50010, type=int)
    args = parser.parse_args()

    gg = tpiClient(args.hostname, args.port)
    gg.launch_gui()
    sys.exit(gg.app.exec_())
