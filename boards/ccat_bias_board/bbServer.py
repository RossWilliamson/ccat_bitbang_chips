#!/usr/bin/env python
import bbCommunicator as bb
#import ftdi.tpi.tpiCommunicator as tpi
#import minicircuits.zx76_31 as atten
#import simplejson as json #Because JSON SUCKS
import struct #Binary is the only way
import logging
from numpy import zeros

""" We will also include in here options for setting
The variable attenuators and the Roach clock source"""

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
            data = ""
            bb_data = self.factory.bbc.collect_single_adc_data()
            
            data_f = zeros(24)
            for i in xrange(4):
                data_f[0+i] = self.factory.bbc.drain[i]["V"]
                data_f[4+i] = self.factory.bbc.drain[i]["I"]
                data_f[8+i] = self.factory.bbc.gatea[i]["V"]
                data_f[12+i] = self.factory.bbc.gatea[i]["I"]
                data_f[16+i] = self.factory.bbc.gateb[i]["V"]
                data_f[20+i] = self.factory.bbc.gateb[i]["I"]

            data = struct.pack("!24f",*data_f)
            self.transport.write(data)

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
        self.tpi = tpi.

if __name__ == '__main__':
    reactor.listenTCP(50001, bbServer())
    reactor.run()
        
