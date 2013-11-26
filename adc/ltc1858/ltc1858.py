from Adafruit_BBIO.SPI import SPI
from bitstring import BitArray
from numpy import arange
import logging
import time

logging.basicConfig()

class ltc1858:
    def __init__(self):
        #define pins
        self.logger = logging.getLogger('LTC1858')
        self.logger.setLevel(logging.WARNING)

        self.spi_bus = 0
        self.spi_client = 0
        self.spi_freq = 1000000 #1Mhz is plenty
        self.spi_mode = 0b00
        
        """We actually send 16 bits but the SPI protocol is a bit screwy
        It's just easier currently to send two 8 bit words as protocol
        is broken"""
        self.spi_bits_per_word = 8
        self.spi_cshigh = False
        
        self.vrange = {"+-5V" : 0b00,
                     "+5V" : 0b10,
                     "+-10V" : 0b01,
                     "+10V" : 0b11}

        #Create a chan dict as not standard binary
        self.chans = {0 : 0b000,
                      1 : 0b100,
                      2 : 0b001,
                      3 : 0b101,
                      4 : 0b010,
                      5 : 0b110,
                      6 : 0b011,
                      7 : 0b111}


        self.adc_reg = {"Monitor" : True,
                        "Range" : "+5V",
                        "V" : 0}
        
        self.chip_reg = []
        for i in xrange(8):
            self.chip_reg.append(self.adc_reg.copy())

        self.single_ended = 0b1

        self.setup_spi()

    def setup_spi(self):
        #This is for BB Black
        self.spi = SPI(self.spi_bus, self.spi_client)
        self.spi.msh = self.spi_freq
        self.spi.mode = self.spi_mode
        self.bpw = self.spi_bits_per_word
        self.spi.cshigh = self.spi_cshigh
        
    def setup_chip(self):
        GPIO.output(self.RD, True)
        GPIO.output(self.CONV, False)
        GPIO.output(self.SDI, False)
        GPIO.output(self.SCK, False)

    def set_reg(self,adc,monitor,adc_range):
        self.chip_reg[adc]["Monitor"] = monitor
        self.chip_reg[adc]["Range"] = adc_range

    def construct_word(self, chan_no, vrange):
        t_word = BitArray(8)
        t_word[0] = self.single_ended
        t_word[1:4] = self.chans[chan_no]
        t_word[4:6] = self.vrange[vrange]
        
        #Ignore nap and sleep
        return t_word

    def single_read(self, chan_no, v_range):
        #Need to set command and then read back so 
        #two words - Just send the same word twice
        self.send_data(self.construct_word(chan_no, v_range))
        data_out = self.send_data(self.construct_word(chan_no, v_range))
        data_conv  = self.convert_to_v(data_out, v_range)
        return data_conv

    def register_read(self):
        #This does one pass at reading all dac inputs
        for i in xrange(8):
            if self.chip_reg[i]["Monitor"] is True:
                vv = self.single_read(i,self.chip_reg[i]["Range"])
                self.chip_reg[i]["V"] = vv
                                      
    def send_data(self,data):
        self.spi.writebytes([data.uint,0x00]) #Send data then zeros as per DS
        #at 1MHz we don't care if it's duplex read
        a,b = self.spi.readbytes(2)
        data_in = BitArray(14)
        data_in[0:8] = a 
        data_in[8:] = (b >> 2)
        return data_in

    def convert_to_v(self,num, v_range):  
        if v_range == "+5V":
            return 5.0*num.uint/2**14
        elif v_range == "+10V":
            return 10.0*num.uint/2**14
        elif v_range == "+-5V":
                return num.int*5.0/2**13
        elif v_range == "+-10V":
            return num.int*10.0/2**13
        else:
            return -69
