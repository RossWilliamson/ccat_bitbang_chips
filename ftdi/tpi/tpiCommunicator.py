import ftdi1 as ftdi
from bitstring import BitArray
from tpiRegisters import *
import logging

logging.basicConfig()


class tpiCommunicator:
    def __init__(self,idVendor=0x0403, idProduct=0x6001):
        self.idVendor = idVendor
        self.idProduct = idProduct
        self.logger = logging.getLogger('tpiCommunicator')
        self.logger.setLevel(logging.INFO)
        
        self.refselect = "internal"
        self.refselectMode = {"internal" : 0,
                              "external" : 1}

        self.ftdi_bits = {"atten2" : 0,
                          "atten1" : 3,
                          "data" : 4,
                          "clk"  : 5,
                          "synth" : 6,
                          "ref_sel" : 7}

        self.open_comms()

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


    def writeConfigReg(self, device, register):
        str = device + " 0b" + register.bin + " (0x" + register.hex + ")"
        self.logger.info(str)
        trans = BitArray('0b00000000')
        #set the refselectbit but everything else is low
        trans[self.ftdi_bits["ref_sel"]] = self.refselectMode[self.refselect]
        self.logger.info(trans.bin)

        #keep LE 1 for "4" time to satisfy min pulse width
        for i in xrange(4):
            ftdi.write_data(self.ftdic, chr(trans.uint), 1)
            self.logger.info(trans.bin)

        #Note says assert now but it's just the same trans as befor
        ftdi.write_data(self.ftdic, chr(trans.uint), 1)
        self.logger.info(trans.bin)

        for i in xrange(len(register)):
            dbit = register[i]
            trans[self.ftdi_bits["data"]] = dbit
            trans[self.ftdi_bits["clk"]] = 0
            self.logger.info(trans.bin)
            ftdi.write_data(self.ftdic, chr(trans.uint), 1)
            trans[self.ftdi_bits["clk"]] = 1
            self.logger.info(trans.bin)
            ftdi.write_data(self.ftdic, chr(trans.uint), 1)

            #Now deal with the case of an attenuator
            #Where the clk has to be held low for another cycle
            if device is "atten1" or "atten2":
                trans[self.ftdi_bits["clk"]] = 0
                ftdi.write_data(self.ftdic, chr(trans.uint), 1)
                self.logger.info(trans.bin)

        #Now keep clock low for a few more cycles (copying tk code)
        trans[self.ftdi_bits["clk"]] = 0
        for i in xrange(3):
            ftdi.write_data(self.ftdic, chr(trans.uint), 1)
            self.logger.info(trans.bin)

        #And strobe the LE bit
        trans[self.ftdi_bits[device]] = 1
        for i in xrange(2):
            ftdi.write_data(self.ftdic, chr(trans.uint), 1)
            self.logger.info(trans.bin)

        trans[self.ftdi_bits[device]] = 0
        print ftdi.write_data(self.ftdic, chr(trans.uint), 1)
        self.logger.info(trans.bin)

    def quick_test(self):
        self.writeConfigReg("synth", BitArray('0x00580005'))
        self.writeConfigReg("synth", BitArray('0x0088c024'))
        self.writeConfigReg("synth", BitArray('0x0000043b'))
        self.writeConfigReg("synth", BitArray('0x1a015e62'))
        self.writeConfigReg("synth", BitArray('0x0800fd01'))
        self.writeConfigReg("synth", BitArray('0x012c0000'))

        self.writeConfigReg("synth", BitArray('0x0088c02c'))
        self.writeConfigReg("atten2", BitArray('0x00'))
        self.writeConfigReg("atten1", BitArray('0x00'))
        self.writeConfigReg("synth", BitArray('0x1a015e42'))
        self.writeConfigReg("synth", BitArray('0x012c0000'))
    
    def quick_freq(self):
        self.writeConfigReg("synth", BitArray('0x1a015e42'))
        self.writeConfigReg("synth", BitArray('0x01900000'))
        self.writeConfigReg("synth", BitArray('0x00e8c024'))
        self.writeConfigReg("synth", BitArray('0x0000043b'))
        self.writeConfigReg("synth", BitArray('0x1a015e42'))
        self.writeConfigReg("synth", BitArray('0x0800fd01'))
        self.writeConfigReg("synth", BitArray('0x01900000'))

        self.writeConfigReg("atten2", BitArray('0x00'))
        self.writeConfigReg("atten1", BitArray('0x00'))

