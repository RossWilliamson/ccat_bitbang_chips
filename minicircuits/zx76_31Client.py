#!/usr/bin/env python
import network.tcpClient as tp
import logging
import argparse
import sys

from zx76_31Gui import *
logging.basicConfig()

class zx76_31Client():
    def __init__(self, hostname="bbone", port=50020):
        self.logger = logging.getLogger('zx76_31Client')
        self.logger.setLevel(logging.DEBUG)
        self.conn = tp.tcpClient(hostname,port,terminator="\r\n")
        self.local_terminator = "\r\n"

    def send(self,msg):
        self.conn.send(msg)
        
    def setatten(self,atten):
        if atten is not None:
            msg = "set atten %i" % (atten)
            self.send(msg)

    def getName(self):
        self.send("get name")
        self.conn.recv_term()
        return self.conn.data_message

    def launch_gui(self):
        self.app = QtGui.QApplication(sys.argv)
        self.gui = zx76_31Gui(self)
        self.gui.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--hostname", help="Hostname to connect to",
                        default="bbone")
    parser.add_argument("-p", "--port", help="Port number to connect to",
                        default=50020, type=int)
    args = parser.parse_args()

    gg = zx76_31Client(args.hostname, args.port)
    gg.launch_gui()
    sys.exit(gg.app.exec_())
