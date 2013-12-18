#!/usr/bin/env python
import minicirbuits.zx76_31 as vatten
import argparse
import logging


from twisted.protocols.basic import LineReceiver
from twisted.internet.protocol import ServerFactory
from twisted.internet import reactor

logging.basicConfig()

class zx76_31Receiver(LineReceiver):
    def __init__(self):
       self.logger = logging.getLogger('zx76_31Server')
       self.logger.setLevel(logging.INFO)

    def lineReceived(self,line):
        sline = line.split()
        if sline[0] == "set":
            if sline[1] == "atten":
                self.logger.debug("Setting atten %s ",sline[2])
                self.zx76_31.set_atten(int(sline[2]))

class zx76_31_Server(ServerFactory):
    protocol = zx76_31Receiver

    def __init__(self,LE,CLK,DATA,name):
        self.zx76_31 = vatten.zx76_31()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", help="Port number to listen on",
                        default=50020, type=int)
    parser.add_argument("-l", "--le", help="LE Pin",
                        default="P8_44")
    parser.add_argument("-c", "--clk", help="CLK Pin",
                        default="P8_45")
    parser.add_argument("-d", "--data", help="DATA Pin",
                        default="P8_46")
    parser.add_argument("-n", "--name", help="Instance Name",
                        default="zx76_31")

    args = parser.parse_args()

    reactor.listenTCP(args.port, tpiServer(args.le,
                                           args.clk,
                                           args.data,
                                           args.name))
    reactor.run()
        