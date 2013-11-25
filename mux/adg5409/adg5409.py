import RPi.GPIO as GPIO
from bitstring import BitArray

import logging

logging.basicConfig()
GPIO.setwarnings(False)

class adg5409:
    def __init__(self):
        self.logger = logging.getLogger("AD5409")
        self.logger.setLevel(logging.INFO)

        self.A0 = 22
        self.A1 = 25
        
        self.setup_pins()
        
    def setup_pins(self):
        GPIO.setmode(GPIO.BCM) #use BCM numbering from breakout board

        GPIO.setup(self.A0, GPIO.OUT)
        GPIO.setup(self.A1, GPIO.OUT)
 
    def set_mux(self,value):
        if value < 0 or value > 3:
            self.logger.error("Mux has to be between 0 and 3")
            return -1
            
        tmp_bit = BitArray(2)
        tmp_bit[:] = value
        GPIO.output(self.A1, tmp_bit[0])
        GPIO.output(self.A0, tmp_bit[1])
        
        self.logger.debug(tmp_bit.bin)
        return value

