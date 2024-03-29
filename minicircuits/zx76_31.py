#import RPi.GPIO as GPIO
import Adafruit_BBIO.GPIO as GPIO
from bitstring import BitArray

import logging

logging.basicConfig()
GPIO.setwarnings(False)

class zx76_31:
    def __init__(self,LE="P8_41",
                 CLK="P8_42",
                 DATA="P8_43",
                 name="zx76_31"):
        self.logger = logging.getLogger("ZX76_31")
        self.logger.setLevel(logging.DEBUG)

        self.LE = LE
        self.CLK = CLK
        self.DATA = DATA
        self.name = name

        self.setup_pins()
        
    def setup_pins(self):
        #GPIO.setmode(GPIO.BCM) #use BCM numbering from breakout board

        GPIO.setup(self.LE, GPIO.OUT)
        GPIO.setup(self.CLK, GPIO.OUT)
        GPIO.setup(self.DATA, GPIO.OUT)

    #We just round to nearest whole atten
    def set_atten(self,value):
        GPIO.output(self.CLK, False)
        GPIO.output(self.LE, False)
        if value < 0 or value > 31:
            self.logger.error("Atten has to be between 0 and 31")
            return -1
        
        
        tmp_bit = BitArray(6)
        tmp_bit[0:5] = int(round(value))
        
        self.logger.debug(tmp_bit.bin)
        for bit in tmp_bit:
            GPIO.output(self.DATA,bit)
            GPIO.output(self.CLK,True)
            GPIO.output(self.CLK,False)

        GPIO.output(self.LE, True)
