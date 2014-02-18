#!/usr/bin/env python
import bbCommunicator as bb
import struct #Binary is the only way
import logging
import argparse
from numpy import zeros

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

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", help="Port number to listen on",
                        default=50001, type=int)

    #ADC settings
    parser.add_argument("-b", "--spibus", help="SPI Bus",
                        default="0")
    parser.add_argument("-c", "--spiclient", help="SPI Client",
                        default="0")
    parser.add_argument("-f", "--spifreq", help="SPI Frequency",
                        default="1000000")
    parser.add_argument("-m", "--spimode", help="SPI Mode",
                        default="0b00")
    parser.add_argument("-r", "--rd", help="RD Pin",
                        default="P9_12")

    #DAC settings
    parser.add_argument("-s", "--sclk", help="SCLK_DAC Pin",
                        default="P8_11")
    parser.add_argument("-d", "--din", help="DIN_DAC Pin",
                        default="P8_12")
    parser.add_argument("-y", "--sync", help="SYNC Pin",
                        default="P8_15")
    parser.add_argument("-l", "--ldac", help="LDAC Pin",
                        default="P8_16")

    args = parser.parse_args()

    reactor.listenTCP(args.port, bbServer())
    reactor.run()
        
