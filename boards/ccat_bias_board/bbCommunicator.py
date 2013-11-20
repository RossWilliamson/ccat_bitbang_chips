import logging
import threading
import time
from dac.ad5734 import ad5734
from adc.ltc1858 import ltc1858

logging.basicConfig()

class bbCommunicator():
    def __init__(self):
        self.logger = logging.getLogger('bbCommunicator')
        self.logger.setLevel(logging.DEBUG)

        self.adc = ltc1858.ltc1858()
        self.dac = ad5734.ad5734_chained(nchips=3)
        
        self.adc_event = threading.Event()
        self.mem_lock = threading.Lock()

        self.drain_sense_r = 2.0
        self.gate_sense_r = 100.0

        self.setup_dac()
        self.setup_adc()

    def __del__(self):
        self.adc_event.set()

    def setup_adc(self):
        #We will just monitor everything and see how
        #slow that is
        self.drainV = 0
        self.drainI = 1
        self.gndSense = 2
        self.auxV = 3
        self.gateaV = 4
        self.gateaI = 5
        self.gatebV = 6
        self.gatebI = 7

        self.adc.set_reg(self.drainV,True,"+5V")
        self.adc.set_reg(self.drainI,True,"+5V")
        self.adc.set_reg(self.gndSense,True,"+-5V")
        self.adc.set_reg(self.auxV,True,"+-5V") 
        self.adc.set_reg(self.gateaV,True,"+-5V") 
        self.adc.set_reg(self.gateaI,True,"+-5V") 
        self.adc.set_reg(self.gatebV,True,"+-5V")
        self.adc.set_reg(self.gatebI,True,"+-5V")

    def setup_dac(self):
        #We setup the dacs to the correct range
        #and place them in a list - It seems backwards
        #due to the way the chips work
        self.drain = []
        self.drain.append({"Chip" : 2, "daq" : "DACA", "V" : 0, "I" : 0})
        self.drain.append({"Chip" : 2, "daq" : "DACD", "V" : 0, "I" : 0})
        self.drain.append({"Chip" : 1, "daq" : "DACC", "V" : 0, "I" : 0})
        self.drain.append({"Chip" : 0, "daq" : "DACB", "V" : 0, "I" : 0})

        self.gatea = []
        self.gatea.append({"Chip" : 2, "daq" : "DACB", "V" : 0, "I" : 0})
        self.gatea.append({"Chip" : 1, "daq" : "DACA", "V" : 0, "I" : 0})
        self.gatea.append({"Chip" : 1, "daq" : "DACD", "V" : 0, "I" : 0})
        self.gatea.append({"Chip" : 0, "daq" : "DACC", "V" : 0, "I" : 0})

        self.gateb = []
        self.gateb.append({"Chip" : 2, "daq" : "DACC", "V" : 0, "I" : 0})
        self.gateb.append({"Chip" : 1, "daq" : "DACB", "V" : 0, "I" : 0})
        self.gateb.append({"Chip" : 0, "daq" : "DACA", "V" : 0, "I" : 0})
        self.gateb.append({"Chip" : 0, "daq" : "DACD", "V" : 0, "I" : 0})
        
        #And we set the daq ranges
        for i in xrange(4):
            tc = self.set_chip(self.drain[i]["Chip"])
            self.dac.set_range(tc, self.drain[i]["daq"], "+10V")

            tc = self.set_chip(self.gatea[i]["Chip"])
            self.dac.set_range(tc, self.gatea[i]["daq"], "+-10V")

            tc = self.set_chip(self.gateb[i]["Chip"])
            self.dac.set_range(tc, self.gateb[i]["daq"], "+-10V")

    def set_chip(self, chip):
        #Due to the way the ltc1858 works we need to
        #construct a list with the correct chip flag set to true
        tmp_chip = [False, False, False]
        tmp_chip[chip] = True
        return tmp_chip

    def set_dac(self,amp,tt,volts):
        #This sets the value on a particular amplifier
        if tt == "drain":
            tc = self.set_chip(self.drain[amp]["Chip"])
            self.dac.set_volts(tc,self.drain[amp]["daq"],volts)
        elif tt == "gatea":
            tc = self.set_chip(self.gatea[amp]["Chip"])
            self.dac.set_volts(tc,self.gatea[amp]["daq"],volts)
        elif tt == "gateb":
            tc = self.set_chip(self.gateb[amp]["Chip"])
            self.dac.set_volts(tc,self.gateb[amp]["daq"],volts)
        else:
            self.logger.error("BAD TYPE")
    
    def latch(self):
        self.dac.chips[0].update_dacs()

    def set_power(self,amp,state):
        #This turns on or off an amplifier
        tc = self.set_chip(self.drain[amp]["Chip"])
        self.dac.set_power(tc,self.drain[amp]["daq"],state)

        tc = self.set_chip(self.gatea[amp]["Chip"])
        self.dac.set_power(tc,self.gatea[amp]["daq"],state)

        tc = self.set_chip(self.gateb[amp]["Chip"])
        self.dac.set_power(tc,self.gateb[amp]["daq"],state)


    def start_adc(self):
        self.adc_thread = threading.Thread(target=self.collect_adc_data)
        self.adc_thread.daemon = True
        self.adc_thread.start()

    def collect_adc_data(self):
        self.adc_event.clear()
        while not self.adc_event.isSet():
            self.collect_single_adc_data()

        time.sleep(0.25)

    def collect_single_adc_data(self):
        #set the mux position
        for i in xrange(4):
            #self.mux.set(i)
            self.mem_lock.acquire()
            self.adc.register_read()
            self.mem_lock.release()
            
            self.drain[i]["V"] = self.adc.chip_reg[self.drainV]["V"]
            self.drain[i]["I"] = self.calculate_current(self.adc.chip_reg[self.drainI]["V"],
                                                        self.adc.chip_reg[self.drainV]["V"],
                                                        self.drain_sense_r)
            
            self.gatea[i]["V"] = self.adc.chip_reg[self.gateaV]["V"]
            self.gatea[i]["I"] = self.calculate_current(self.adc.chip_reg[self.gateaI]["V"],
                                                        self.adc.chip_reg[self.gateaV]["V"],
                                                        self.gate_sense_r)
                
            self.gateb[i]["V"] = self.adc.chip_reg[self.gatebV]["V"]
            self.gateb[i]["I"] = self.calculate_current(self.adc.chip_reg[self.gatebI]["V"],
                                                        self.adc.chip_reg[self.gatebV]["V"],
                                                        self.gate_sense_r)

    def calculate_current(self,v1,v2,res_val):
        #Calculates the current from the input voltages and resistances
        return (v1-v2)/res_val
