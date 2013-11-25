import network.tcpClient as tp
import simplejson as json
import logging
 
logging.basicConfig()

class bbClient():
    def __init__(self, hostname="rtpi", port=50001):
        self.logger = logging.getLogger('bbClient')
        self.logger.setLevel(logging.DEBUG)
        self.conn = tp.tcpClient(hostname,port,terminator="\r\n")
        self.local_terminator = "\r\n"

    def send(self,msg):
        self.conn.send(msg)

    def fetchDict(self):
        self.send("read")
        self.conn.recv_term()
        self.drains = json.loads(self.conn.data_message)
        
        self.conn.recv_term()
        self.gatea = json.loads(self.conn.data_message)
        
        self.conn.recv_term()
        self.gateb = json.loads(self.conn.data_message)

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
                                                                                    self.drains[i]["V"], self.drains[i]["I"],
                                                                                    self.gatea[i]["V"], self.gatea[i]["I"],
                                                                                    self.gateb[i]["V"], self.gateb[i]["I"])
            print str
