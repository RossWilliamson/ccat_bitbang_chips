import ftdi1 as ftdi
from numpy import *
from fractions import gcd
from bitstring import BitArray
from tpiRegisters import *
import logging


logging.basicConfig()


class tpiCommunicator:
    def __init__(self, freq = 2000.0, power = 0,
                 idVendor=0x0403, idProduct=0x6001):
        self.idVendor = idVendor
        self.idProduct = idProduct
        self.freq = freq
        self.power = power
        self.logger = logging.getLogger('tpiCommunicator')
        self.logger.setLevel(logging.DEBUG)
        
        self.refselect = "internal"
        self.refselectMode = {"internal" : 0,
                              "external" : 1}

        self.ftdi_bits = {"atten2" : 0,
                          "atten1" : 3,
                          "data" : 4,
                          "clk"  : 5,
                          "synth" : 6,
                          "ref_sel" : 7}

        self.refFreq = 10

        self.open_comms()
        self.setup_registers()

    def __del__(self):
        self.close_comms()

    def open_comms(self):
        self.ftdic = ftdi.new()
        ret = ftdi.usb_open(self.ftdic, self.idVendor, self.idProduct)
        print ret
        ret = ftdi.usb_purge_buffers(self.ftdic)
        print ret
        ret = ftdi.set_bitmode(self.ftdic, 0xFF, ftdi.BITMODE_BITBANG)
        print ret

    def close_comms(self):
        print ftdi.disable_bitbang(self.ftdic)
        print ftdi.usb_close(self.ftdic)

    def setup_registers(self):
        """This grabs the registers classes and sets them up
        The defaults are in the reg classes so edit there if you need to
        change or pass new arguments here - We also set a loadup frequency
        We then load thoses onto the TPI synth
        """

        self.reg0 = register0()
        self.reg1 = register1()
        self.reg2 = register2()
        self.reg3 = register3()
        self.reg4 = register4()
        self.reg5 = register5()
        
        self.writeConfigReg("synth", self.reg5.reg) #not sent in update freq
        self.setFreq(self.freq) # Also sets default power

    def setrfOn(self,state):
        self.reg2.set_pdwn(not state)
        self.writeConfigReg("synth", self.reg2.reg) 
        self.writeConfigReg("synth", self.reg0.reg) 
        self.rfon = state


        
    def setFreq(self,freq):
        if freq == 0:
            self.logger.warn("Frequency is called with 0!")
        if freq > 4200:
            self.logger.warn("Freqeuncy is > 4200")
        
        self.calcPll(freq)
        
        #set lownoise ans spur mode
        if self.reg0.frac == 0:
            self.reg2.set_lnoise(0)
            self.reg3.set_csren(0)
        else:
            self.reg2.set_lnoise(3)
            self.reg3.set_csren(1)

        self.setoutpower(self.power)
        self.writeConfigReg("synth", self.reg4.reg) 
        self.writeConfigReg("synth", self.reg3.reg)
        self.writeConfigReg("synth", self.reg2.reg) 
        self.writeConfigReg("synth", self.reg1.reg)
        self.writeConfigReg("synth", self.reg0.reg) 
        
        #finaly set class freq to freq
        self.freq = freq

    def calcPll(self,setPt):
        #I think some of these inputs could be class members
        #but kept like this to be similar to the tk
        #Ok make them part of the class - just need setpoint
    
        setRatio = 2200.0/setPt
        pllRfDivider = 2**int(ceil(math.log(setRatio,2)))
        #just keep it to 64
        if pllRfDivider > 64:
            pllRfDivier = 64

        if self.reg2.refx2 == 1:
            refX2value = 2.0
        else:
            refX2value = 1.0

        if self.reg2.refdiv2 == 1:
            refdiv2val = 2.0
        else:
            refdiv2val = 1.0

        #Check tk for equation on calulating pll....
        pllPfd = (self.refFreq*refX2value)/(self.reg2.refdiv*refdiv2val)
        str1 = "pfd calc for ref frequency %f" % self.refFreq
        str2 = "pfd parameters are refX2value: %f, refdivider: %f, refdiv2: %f" % (refX2value, self.reg2.refdiv, refdiv2val) 
        str3 = "pll pfd frequency is %f" % pllPfd
        self.logger.debug(str1)
        self.logger.debug(str2)
        self.logger.debug(str3)
        
        intSetpt = pllRfDivider * setPt
        pllInt = int(intSetpt/pllPfd)

        str1 = "For target output frequency %f " % setPt
        str2 = "with pllRFDivider: %i" % pllRfDivider
        str3 = "gives VCO frequency of %f" % intSetpt
        str4 = "INT counter setting is %i" % pllInt
        self.logger.debug(str1)
        self.logger.debug(str2)
        self.logger.debug(str3)
        self.logger.debug(str4)

        if(pllInt < 75 or pllInt > 65536):
            self.logger.error("INT setting out of range")
        
        # modulus calc
        preMod = pllPfd/0.001
        preModulus = int(preMod)
        str1 = "Unreduced Modulus (real): %f (int): %i " % (preMod, preModulus)
        self.logger.debug(str1)

        v1 = intSetpt/pllPfd
        preFrac = int(round((v1-pllInt)*preMod))
        str1 = "Fractional Componenent of Frequency: %f" % v1
        str2 = "Unreduced Fractional setting: %i" % preFrac
        self.logger.debug(str1)
        self.logger.debug(str2)

        #Get Greatest common denominator (factor2)
        tmp_gcd = self.gcd_bin(preFrac, preModulus)
        pllFrac = preFrac/tmp_gcd
        pllModulus = preModulus/tmp_gcd

        str1 = "Reduced Frac and Modulus: %i %i" % (pllFrac, pllModulus)
        self.logger.debug(str1)

        if(pllModulus > 4096 and pllFrac != 0):
            self.logger.error("FRAC MODE WITH MODULUS GREATER THAN 4096")

        if(pllFrac !=0 and pllPfd > 32):
            self.logger.error("PLL PFD TOO HIGH FOR FRAC MODE (> 32 MHz)")
        
        #Ok so now we have the PLL inputs we assign them to the registers
        self.reg0.set_int(pllInt)
        self.reg0.set_frac(pllFrac)
        self.reg1.set_modulus(pllModulus)
        self.reg4.set_outdivider(pllRfDivider)

        #code also returns pllPfd but not sure where that is used
            

    def setoutpower(self,power):
        """This function just sets the regsiter as we have no 
        attenuators on the basic board - will do calibration
        table etc when recieve calibrated board
        """
        
        if power <0 or power > 3:
            self.logger.warn("Power needs to be integer between 0 and 3")
            power = 0

        self.reg4.set_rfoutpwr(int(power))
        #and send the register
        self.writeConfigReg("synth", self.reg4.reg)
        self.power = power


    def writeConfigReg(self, device, register):
        str = device + " 0b" + register.bin + " (0x" + register.hex + ")"
        self.logger.debug(str)
        trans = BitArray('0b00000000')
        #set the refselectbit but everything else is low
        trans[self.ftdi_bits["ref_sel"]] = self.refselectMode[self.refselect]
        #self.logger.debug(trans.bin)

        #keep LE 1 for "4" time to satisfy min pulse width
        for i in xrange(4):
            ftdi.write_data(self.ftdic, chr(trans.uint), 1)
            #self.logger.debug(trans.bin)

        #Note says assert now but it's just the same trans as befor
        ftdi.write_data(self.ftdic, chr(trans.uint), 1)
        #self.logger.debug(trans.bin)

        for i in xrange(len(register)):
            dbit = register[i]
            trans[self.ftdi_bits["data"]] = dbit
            trans[self.ftdi_bits["clk"]] = 0
            #self.logger.debug(trans.bin)
            ftdi.write_data(self.ftdic, chr(trans.uint), 1)
            trans[self.ftdi_bits["clk"]] = 1
            #self.logger.debug(trans.bin)
            ftdi.write_data(self.ftdic, chr(trans.uint), 1)

            #Now deal with the case of an attenuator
            #Where the clk has to be held low for another cycle
            if device is "atten1" or "atten2":
                trans[self.ftdi_bits["clk"]] = 0
                ftdi.write_data(self.ftdic, chr(trans.uint), 1)
                #self.logger.debug(trans.bin)

        #Now keep clock low for a few more cycles (copying tk code)
        trans[self.ftdi_bits["clk"]] = 0
        for i in xrange(3):
            ftdi.write_data(self.ftdic, chr(trans.uint), 1)
            #self.logger.debug(trans.bin)

        #And strobe the LE bit
        trans[self.ftdi_bits[device]] = 1
        for i in xrange(2):
            ftdi.write_data(self.ftdic, chr(trans.uint), 1)
            #self.logger.debug(trans.bin)

        trans[self.ftdi_bits[device]] = 0
        print ftdi.write_data(self.ftdic, chr(trans.uint), 1)
        #self.logger.debug(trans.bin)

    def gcd_bin(self,a,b):
        """Calculates the gcd but requires that it also be
        a factor of 2...
        These if probabably a clever way of doing this....
        """
        #First get the highest common factor
        if a == 0 :
            return 1
        ff = gcd(a,b)
        #and if a multiple of the hcf is 
        for i in xrange(1,ff+1):
            fa = ff*1.0/i
            ispower2 = self.isPower(fa,2)
            if ispower2 is True:
                return int(fa)

    def isPower(self,num, base):
        if base == 1 and num != 1: return False
        if base == 1 and num == 1: return True
        if base == 0 and num != 1: return False
        power = int (math.log (num, base) + 0.5)
        return base ** power == num
