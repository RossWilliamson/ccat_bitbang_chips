#!/usr/bin/env python
import bbCommunicator as bb
import simplejson as json
import logging

from twisted.protocols.basic import LineReceiver
from twisted.internet.protocol import ServerFactory
from twisted.internet import reactor

logging.basicConfig()

class bbReceiver(LineReceiver):
    def __init__(self):
       self.logger = logging.getLogger('bbClient')
       self.logger.setLevel(logging.INFO)

    def lineReceived(self,line):
        sline = line.split()
        if sline[0] == "read":
            self.logger.debug("Sending Data")
            bb_data = self.factory.bbc.collect_single_adc_data()
            data = json.dumps(self.factory.bbc.drain)
            self.transport.write(data)
            self.transport.write("\r\n")
            data = json.dumps(self.factory.bbc.gatea)
            self.transport.write(data)
            self.transport.write("\r\n")
            data = json.dumps(self.factory.bbc.gateb)
            self.transport.write(data)
            self.transport.write("\r\n")
        elif sline[0] == "set":
            if sline[1] == "amp":
                self.logger.debug("Setting amp %s %s %s",sline[2], sline[3], sline[4])
                self.factory.bbc.set_dac(int(sline[2]), sline[3], float(sline[4]))
            elif sline[1] == "power":
                self.logger.debug("Setting Power %s %s",sline[2], sline[3])
                self.factory.bbc.set_power(int(sline[2]), int(sline[3]))
        elif sline[0] == "latch":
            self.logger.debug("Latching DAQs")
            self.factory.bbc.latch()

class bbServer(ServerFactory):
    protocol = bbReceiver

    def __init__(self):
        self.bbc = bb.bbCommunicator()

if __name__ == '__main__':
    reactor.listenTCP(50001, bbServer())
    reactor.run()
        
