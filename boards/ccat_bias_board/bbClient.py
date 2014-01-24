#!/usr/bin/env python
import network.tcpClient as tp
import simplejson as json
import logging
import struct
import argparse
import sys

from bbGui import *
logging.basicConfig()

class bbClient():
    def __init__(self, hostname="localhost", port=50001):
        self.logger = logging.getLogger('bbClient')
        self.logger.setLevel(logging.DEBUG)
        self.conn = tp.tcpClient(hostname,port,terminator="\r\n")
        self.local_terminator = "\r\n"

        self.drain = []
        self.drain.append({"V" : 0, "I" : 0})
        self.drain.append({"V" : 0, "I" : 0})
        self.drain.append({"V" : 0, "I" : 0})
        self.drain.append({"V" : 0, "I" : 0})

        self.gatea = []
        self.gatea.append({"V" : 0, "I" : 0})
        self.gatea.append({"V" : 0, "I" : 0})
        self.gatea.append({"V" : 0, "I" : 0})
        self.gatea.append({"V" : 0, "I" : 0})

        self.gateb = []
        self.gateb.append({"V" : 0, "I" : 0})
        self.gateb.append({"V" : 0, "I" : 0})
        self.gateb.append({"V" : 0, "I" : 0})
        self.gateb.append({"V" : 0, "I" : 0})

    def send(self,msg):
        self.conn.send(msg)

    def fetchDict(self):
        self.send("read")
        self.conn.recv_nbytes(96)
        data = struct.unpack("!24f", self.conn.data_message)
        for i in xrange(4):
             self.drain[i]["V"] = data[0+i]
             self.drain[i]["I"] = data[4+i]
             self.gatea[i]["V"] = data[8+i]
             self.gatea[i]["I"] = data[12+i]
             self.gateb[i]["V"] = data[16+i]
             self.gateb[i]["I"] = data[20+i]
        
    def setPower(self,amp,state):
        self.checkAmp(amp)
        if amp is not None:
            msg = "set power %i %i" % (amp, int(state))
            self.send(msg)

    def latchDaq(self):
        self.send("latch")

    def setAmp(self,amp,type,v):
        if self.checkAmp(amp) is None:
            return None
        if type == "drain" or type == "gatea" or type == "gateb":
            msg = "set amp %i %s %f" % (amp,type,v)
            self.send(msg)
        else:
            self.logger.error("TYPE has to be drain,gatea,gateb")

    def checkAmp(self,amp):
        if amp < 0 or  amp > 3:
            self.logger.error("AMP has to be between 0 and 3")
            return None
        return amp

    def printData(self):
        #print output of data (rough)
        for i in xrange(4):
            str = "Amp %i: D: %5.3f (%5.3f), GA %5.3f (%5.3f), GB %5.3f (%5.3f)" % (i,
                                                                                    self.drain[i]["V"], self.drain[i]["I"],
                                                                                    self.gatea[i]["V"], self.gatea[i]["I"],
                                                                                    self.gateb[i]["V"], self.gateb[i]["I"])
            print str

    def launch_gui(self):
        self.app = QtGui.QApplication(sys.argv)
        self.gui = bbGui(self)
        self.gui.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--hostname", help="Hostname to connect to",
                        default="bbone")
    parser.add_argument("-p", "--port", help="Port number to connect to",
                        default=50001, type=int)
    args = parser.parse_args()

    gg = bbClient(args.hostname, args.port)
    gg.launch_gui()
    sys.exit(gg.app.exec_())
