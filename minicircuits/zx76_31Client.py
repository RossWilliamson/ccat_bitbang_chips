import network.tcpClient as tp
import logging

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

