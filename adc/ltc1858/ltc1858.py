import RPi.GPIO as GPIO
from numpy import arange
import time

class ltc1858:
    def __init__(self):
        #define pins
        self.SDI = 11
        self.SCK = 13
        self.CONV = 15
        self.BUSY = 19
        self.RD = 21
        self.SDO = 23
        
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


        self.single_ended = 0b1 << 15

        self.setup_pins()
        self.setup_chip()

    def setup_pins(self):
        GPIO.setmode(GPIO.BOARD) #use board numbering
        #Set output pins
        GPIO.setup(self.SDI, GPIO.OUT)
        GPIO.setup(self.SCK, GPIO.OUT)
        GPIO.setup(self.CONV, GPIO.OUT)
        GPIO.setup(self.RD, GPIO.OUT)
        #Set input pins
        GPIO.setup(self.BUSY, GPIO.IN) #Wrong chip for this....Don't use
        GPIO.setup(self.SDO, GPIO.IN)

    def setup_chip(self):
        GPIO.output(self.RD, True)
        GPIO.output(self.CONV, False)
        GPIO.output(self.SDI, False)
        GPIO.output(self.SCK, False)

    def construct_word(self, chan_no, vrange):
        t_word = self.single_ended
        t_word += (self.chans[chan_no] << 12)
        t_word += (self.vrange[vrange] << 10)
        #Ignore nap and sleep

        return t_word

    def single_read(self, chan_no, v_range):
        #Need to set command and then read back so 
        #two words - Just send the same word twice
        self.send_data(self.construct_word(chan_no, v_range))
        data_out = self.send_data(self.construct_word(chan_no, v_range))
        data_conv  = self.convert_to_v(data_out, v_range)
        return data_conv

    def send_data(self,data):
        GPIO.output(self.SCK, False)
        GPIO.output(self.RD, False) 

        data_in = 0
        for i in arange(15,-1,-1):
            dbit = ((data >> i) & 0x01)
            print dbit
            GPIO.output(self.SDI,dbit)
            GPIO.output(self.SCK,True)
            #let's read the data
            data_in += GPIO.input(self.SDO) << i
            GPIO.output(self.SCK,False)
        #Now take conv high
        GPIO.output(self.CONV,True)
        time.sleep(10e-6)
        GPIO.output(self.CONV,False)
        data_in = (data_in >> 2) #only 14 bits
        print bin(data_in)
        return data_in

    def convert_to_v(self,num, v_range):  
        if v_range == "+5V":
            return 5.0*num/2**14
        elif v_range == "+10V":
            return 10.0*num/2**14
        elif v_range == "+-5V":
            if ((num & 0x2000) >> 13) == 1:
                return num*10.0/2**14 - 10
            else:
                return num*10.0/2**14
        elif v_range == "+-10V":
            if ((num & 0x2000) >> 13) == 1:
                return num*20.0/2**14 - 20
            else:
                return num*20.0/2**14
        else:
            return -69
        
    def two_comp(self,val):
        if ( (val&(1<<(14-1))) != 0 ):
            val = val - (1<<14)
        return val