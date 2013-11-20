import RPi.GPIO as GPIO
from bitstring import BitArray
from numpy import *
import time
import logging

logging.basicConfig()
GPIO.setwarnings(False)

class ad5734_chained:
    def __init__(self,nchips=3):
        self.logger = logging.getLogger("AD5734_Chained")
        self.logger.setLevel(logging.DEBUG)
        self.nchips = nchips
        self.chips = []
        for i in xrange(nchips):
            self.chips.append(ad5734(single=False))


    def set_power(self,chips,dac,state):
        self.chips[0].start_transmit()

        if len(chips) < self.nchips:
            print "IDIOT"

        for i in xrange(self.nchips):
            if chips[i] is True:
                self.chips[i].power_state(dac,state)
            else:
                self.chips[i].send_nop()
                
        self.chips[0].end_transmit()

    def set_range(self,chips,dac,dac_range):
        self.chips[0].start_transmit()

        if len(chips) < self.nchips:
            print "IDIOT"

        for i in xrange(self.nchips):
            if chips[i] is True:
                self.chips[i].set_range(dac,dac_range)
            else:
                self.chips[i].send_nop()
        
        self.chips[0].end_transmit()

    def set_volts(self,chips,dac,v):
        self.chips[0].start_transmit()

        if len(chips) < self.nchips:
            print "IDIOT"

        for i in xrange(self.nchips):
            if chips[i] is True:
                self.chips[i].set_volts(dac,v)
            else:
                self.chips[i].send_nop()
        
        self.chips[0].end_transmit()

class ad5734:
    def __init__(self,single=True,
                 vref=2.5):
        self.logger = logging.getLogger("AD5734")
        self.logger.setLevel(logging.DEBUG)

        self.vref = vref
        self.single = single

        self.nbits = 2**14
        #define pins
        self.SCLK_DAC = 17
        self.DIN_DAC = 23
        self.SYNC = 24
        self.LDAC = 27
        
        
        self.vrange = {"+5V" : 0b000,
                       "+10V" : 0b001,
                       "+10.8V" : 0b010,
                       "+-5V" : 0b011,
                       "+-10V" : 0b100,
                       "+-10.8V" : 0b101}

        #vgain format is gain,bipolar
        self.vgain = {"+5V" : [2,False],
                       "+10V" : [4,False],
                       "+10.8V" : [4.32, False],
                       "+-5V" : [4, True],
                       "+-10V" : [8, True],
                       "+-10.8V" : [8.64,True]}

        self.dac_addr = {"DACA" : 0b000,
                         "DACB" : 0b001,
                         "DACC" : 0b010,
                         "DACD" : 0b011,
                         "DACALL" : 0b100}

        self.dac_pwr_addr = {"DACA" : 3,
                             "DACB" : 2,
                             "DACC" : 1,
                             "DACD" : 0,
                             "DACALL" : 4}

        self.dac_pwr_reg = BitArray(4)

        self.dac_reg = {"Power" : False,
                        "Range" : "+5V",
                        "Vout" : 0}

        self.chip_reg = {"DACA" : self.dac_reg,
                         "DACB" : self.dac_reg,
                         "DACC" : self.dac_reg,
                         "DACD" : self.dac_reg}

        self.reg_addr = {"DAC" : 0b000,
                         "RANGE" : 0b001,
                         "POWER" : 0b010,
                         "CTRL" : 0b011}

        self.setup_pins()
        self.setup_chip()
        self.tmp_setup_mux()

    def setup_pins(self):
        GPIO.setmode(GPIO.BCM) #use BCM numbering from breakout board
        #Set output pins
        GPIO.setup(self.SCLK_DAC, GPIO.OUT)
        GPIO.setup(self.DIN_DAC, GPIO.OUT)
        GPIO.setup(self.SYNC, GPIO.OUT)
        GPIO.setup(self.LDAC, GPIO.OUT)
       
    def setup_chip(self):
        GPIO.output(self.SCLK_DAC, True)
        GPIO.output(self.SYNC, True)
        GPIO.output(self.LDAC, True)

    def tmp_setup_mux(self):
        self.A0 = 22
        self.A1 = 25
        GPIO.setup(self.A0, GPIO.OUT)
        GPIO.setup(self.A1, GPIO.OUT)
        

    def construct_word(self, reg, dac,data):
        word = BitArray(24) #24 bits initial
        #write is zero and res is zero 
        #bitArrays count from left (at least if you are lazy)
        word[2:5] = self.reg_addr[reg]
        word[5:8] = self.dac_addr[dac]
        
        word[8:] = data

        return word

    def power_state(self,dac,state):
        data = BitArray(16)
        idx = self.dac_pwr_addr[dac]
        if idx == 4: #do all
            if state is True: 
                self.dac_pwr_reg[:] = 0b1111
            else:
                self.dac_pwr_reg[:] = 0b0000
        else:
            self.dac_pwr_reg[idx] = state

        data[-4:] = self.dac_pwr_reg
        
        word = self.construct_word("POWER", "DACA", data) #DACA because A2A1A0 are 0b000
        self.logger.debug(word.bin)
        if self.single is True:
            self.send_data(word)
        else:
            self.send_word(word)
        
    def calc_range(self,v):
        pass

    def set_range(self,dac,dac_range):
        #Just pass range, dac is sorted in the construct_word
        data = BitArray(16)
        data[-3:] = self.vrange[dac_range]

        word =  self.construct_word("RANGE", dac, data)

        if dac == "DACALL":
            self.chip_reg["DACA"]["Range"] = dac_range
            self.chip_reg["DACB"]["Range"] = dac_range
            self.chip_reg["DACC"]["Range"] = dac_range
            self.chip_reg["DACD"]["Range"] = dac_range
        else:
            self.chip_reg[dac]["Range"] = dac_range


        self.logger.debug(word.bin)
        if self.single is True:
            self.send_data(word)
        else:
            self.send_word(word)
        

    def set_volts(self,dac,v):
        #need to fix v_range with correct
        #stored parameter or logic
        data = BitArray(16)
        v_range = self.chip_reg[dac]["Range"]
        data[0:14] = self.v_to_bits(v,v_range)
        word = self.construct_word("DAC", dac, data)
        self.chip_reg[dac]["Vout"] = v

        self.logger.debug(word.bin)
        if self.single is True:
            self.send_data(word)
        else:
            self.send_word(word)

    def send_nop(self):
        #This sends a no operation command
        #Useful when chaining together chips
        #Just send zeros to ctrl reg dacA
        data = BitArray(16)
        word = self.construct_word("CTRL", "DACA", data)
        self.logger.debug(word.bin)
        if self.single is True:
            self.send_data(word)
        else:
            self.send_word(word)
            
    def send_data(self,word):
        #This is for a single chip send
        #A super class is used if chips are 
        #Daisychained together
        self.start_transmit()
        self.send_word(word)
        self.end_transmit()
        self.update_dacs()

    def send_word(self,word):
        for dbit in word:
            GPIO.output(self.DIN_DAC, dbit)
            GPIO.output(self.SCLK_DAC, False)
            GPIO.output(self.SCLK_DAC, True)

    def start_transmit(self):
        #This is here if we want to send to more
        #than one chip daisychanned together
        GPIO.output(self.LDAC, True)
        GPIO.output(self.SCLK_DAC, True)
        GPIO.output(self.SYNC, False)

    def end_transmit(self):
        #This is used to latch registers
        GPIO.output(self.SYNC,True)

    def update_dacs(self):
        #This is used to update all the dacs
        GPIO.output(self.LDAC, False)
        GPIO.output(self.LDAC, True)

        
    def v_to_bits(self,v, v_range):  
        #Need to put checks in her for correct range
        #otherwise gibberish will ensue.
        data = BitArray(14)
        gain,bipolar = self.vgain[v_range]
        bits = (v*self.nbits)/(self.vref*gain)
        bits = int(round(bits))
        if bits > (self.nbits-1):
            bits = self.nbits-1
            
        data[:] = bits #Does 2's comp which is awsome
       
        return data

