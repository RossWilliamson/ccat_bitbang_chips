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
       pass

    def lineReceived(self,line):
        sline = line.split()
        if sline[0] == "read":
            bb_data = self.factory.bbc.collect_single_adc_data()
            data = json.dumps(self.factory.bbc.drain)
            self.transport.write(data)
            data = json.dumps(self.factory.bbc.gatea)
            self.transport.write(data)
            data = json.dumps(self.factory.bbc.gateb)
        elif sline[0] == "set":
            if sline[1] == "amp":
                self.factory.bbc.set_dac(int(sline[2]), sline[3], float(sline[4]))
            elif sline[1] == "power":
                self.factory.bbc.set_power(int(sline[2]), int(sline[3]))
        elif sline[0] == "latch":
            self.factory.bbc.latch()

class bbServer(ServerFactory):
    protocol = bbReceiver

    def __init__(self):
        self.bbc = bb.bbCommunicator()

if __name__ == '__main__':
    reactor.listenTCP(50001, bbServer())
    reactor.run()
        
y
