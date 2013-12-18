#!/usr/bin/env python
import ftdi.tpi.tpiCommunicator as tpi
import argparse
import logging

""" We will also include in here options for setting
The variable attenuators and the Roach clock source"""

from twisted.protocols.basic import LineReceiver
from twisted.internet.protocol import ServerFactory
from twisted.internet import reactor

logging.basicConfig()

class tpiReceiver(LineReceiver):
    def __init__(self):
       self.logger = logging.getLogger('tpiClient')
       self.logger.setLevel(logging.INFO)

    def lineReceived(self,line):
        sline = line.split()
        if sline[0] == "set":
            if sline[1] == "freq":
                self.logger.debug("Setting freq %s ",sline[2])
                self.factory.tpi.setFreq(float(sline[2]))
            elif sline[1] == "power":
                self.logger.debug("Setting Power %s",sline[2])
                self.factory.tpi.setoutpower(int(sline[2]))
            elif sline[1] == "rfon":
                self.logger.debug("Setting rfon %s",sline[2])
                self.factory.tpi.setrfOn(int(sline[2]))

class tpiServer(ServerFactory):
    protocol = tpiReceiver

    def __init__(self):
        self.tpi = tpi.tpiCommunicator()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", help="Port number to listen on",
                        default=50010, type=int)
    args = parser.parse_args()

    reactor.listenTCP(args.port, tpiServer())
    reactor.run()
        
