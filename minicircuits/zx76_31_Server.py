#!/usr/bin/env python
import minicircuits.zx76_31 as vatten
import argparse
import logging


from twisted.protocols.basic import LineReceiver
from twisted.internet.protocol import ServerFactory
from twisted.internet import reactor

logging.basicConfig()

class zx76_31Receiver(LineReceiver):
    def __init__(self):
       self.logger = logging.getLogger('zx76_31Server')
       self.logger.setLevel(logging.DEBUG)

    def lineReceived(self,line):
        sline = line.split()
        if sline[0] == "set":
            if sline[1] == "atten0":
                self.logger.debug("Setting atten0 %s ",sline[2])
                self.factory.zx76_31[0].set_atten(int(sline[2]))
            elif sline[1] == "atten1":
                self.logger.debug("Setting atten1 %s ",sline[2])
                self.factory.zx76_31[1].set_atten(int(sline[2]))    
        elif sline[0] == "get":
            if sline[1] == "name":
                self.transport.write(self.factory.zx76_31.name)
                self.transport.write("\r\n")

class zx76_31_Server(ServerFactory):
    protocol = zx76_31Receiver

    def __init__(self,LE,CLK,DATA,name):
        """OK this is a hack that should be fixed"""
        self.zx76_31 = []
        self.zx76_31.append(vatten.zx76_31(LE,CLK,DATA,name))
        self.zx76_31.append(vatten.zx76_31("P8_44", "P8_45", "P8_46"))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", help="Port number to listen on",
                        default=50020, type=int)
    parser.add_argument("-l", "--le", help="LE Pin",
                        default="P8_41")
    parser.add_argument("-c", "--clk", help="CLK Pin",
                        default="P8_42")
    parser.add_argument("-d", "--data", help="DATA Pin",
                        default="P8_43")
    parser.add_argument("-n", "--name", help="Instance Name",
                        default="zx76_31")

    args = parser.parse_args()

    reactor.listenTCP(args.port, zx76_31_Server(args.le,
                                           args.clk,
                                           args.data,
                                           args.name))
    reactor.run()
        
