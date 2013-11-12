from bitstring import BitArray
import math

###########################################################################
#
# REGISTER 0
#
# Control Bits
# With Bits [C3:C1] set to 0, 0, 0, Register 0 is programmed. 
# 
# 16-Bit INT Value
#
# These sixteen bits set the INT value, which determines the integer 
# part of the feedback division factor. 
# It is used in Equation 1 (see the INT, FRAC, MOD, and R Counter Relationship section). 
# All integer values from 23 to 65,535 are allowed for 4/5 prescaler. 
# For 8/9 prescaler, the minimum integer value is 75.
# 
# 12-Bit FRAC Value
#
# The 12 FRAC bits set the numerator of the fraction that is input to the modulator. 
# This, along with INT, specifies the new frequency channel that the synthesizer locks to, 
# as shown in the RF Synthesizer-A Worked Example section.
# FRAC values from 0 to MOD  1 cover channels over a frequency range equal 
# to the PFD reference frequency.
#
# DB31 | DB30 - DB15 | DB14 - DB3 | DB2 - DB0
# RESRV| INT         | FRAC       | Control (000)
#
###########################################################################
class register0:
    def __init__(self):
        self.reg = BitArray(32)
        self.reg[-3:] = 0b000 #Control bits
        
        self.frac = 0
        self.int = 0

    def set_frac(self,frac):
        self.frac = frac
        self.reg[-15:-3] = self.frac

    def set_int(self,int):
        self.int = int
        self.reg[-31:-15] = self.int

###########################################################################
#
# REGISTER 1
#
# Control Bits
# With Bits [C3:C1] set to 0, 0, 1, Register 1 is programmed. 
# 
# Prescaler Value
# The dual modulus prescaler (P/P + 1), along with the INT, FRAC, and MOD counters, 
# determines the overall division ratio from the VCO output to the PFD input.
# 
# Operating at CML levels, the prescaler takes the clock from the VCO output and 
# divides it down for the counters. It is based on a synchronous 4/5 core. 
# When set to 4/5, the maximum RF frequency allowed is 3 GHz. 
# 
# Therefore, when operating the ADF4350 above 3 GHz, this must be 
# set to 8/9. The prescaler limits the INT value, where P is 4/5, 
# NMIN is 23 and P is 8/9, NMIN is 75.  In the ADF4350, PR1 in Register 1 sets the 
# prescaler values.
# 
# 12-Bit Phase Value
# These bits control what is loaded as the phase word. 
# The word must be less than the MOD value programmed in Register 1. 
# 
# The word is used to program the RF output phase from 0 to 360  with a resolution of 360/MOD. 
# See the Phase Resync section for more information. 
# 
# In most applications, the phase relationship between the RF 
# signal and the reference is not important. In such applications, the phase value 
# can be used to optimize the fractional and subfractional spur levels. 
# See the Spur Consistency and Fractional Spur Optimization section for more information.
# If neither the phase resync nor the spurious optimization functions are being used, 
# it is recommended the PHASE word be set to 1.
# 
# 12-Bit Interpolator MOD Value
# This programmable register sets the fractional modulus. This is the ratio of the PFD 
# frequency to the channel step resolution on the RF output. 
# See the RF Synthesizer-A Worked Example section for more information.
#
# DB31 - DB29 | DB28    | DB27   | DB26 - DB15 | DB14 - DB3 | DB2 - DB0
# RESRVED     | PHASEAJ | PRESCL | PHASE DBR   | MODULUS    | CNTRL C3-C1  (001)
#
###########################################################################
class register1:
    def __init__(self,
                 phaseadjust = 0,
                 phase = 1,
                 prescale = 1):
    
        self.reg = BitArray(32)
        self.reg[-3:] = 0b001 #Control bits
        self.modulus = 0

        self.set_phase(phase)
        self.set_prescl(prescale)
        self.set_phaseaj(phaseadjust)

    def set_modulus(self,modulus):
        self.modulus = modulus
        self.reg[-15:-3] = self.modulus

    def set_phase(self,phase):
        self.phase = phase
        self.reg[-27:-15] = self.phase

    def set_prescl(self,prescale):
        self.prescale = prescale
        self.reg[-28] = self.prescale

    def set_phaseaj(self,phaseaj):
        self.phaseaj = phaseaj
        self.reg[-29] = self.phaseaj

        
###########################################################################
#
# REGISTER 2
#
# Control Bits
# With Bits [C3:C1] set to 0, 1, 0, Register 2 is programmed. 
# 
# Low Noise and Low Spur Modes
# The noise modes on the ADF4350 are controlled by DB30 and DB29 in 
# Register 2 (see Figure 26). The noise modes allow the user to optimize a 
# design either for improved spurious perfor-mance or for improved phase noise performance.
# 
# When the lowest spur setting is chosen, dither is enabled. This randomizes 
# the fractional quantization noise so it resembles white noise rather than 
# spurious noise. As a result, the part is optimized for improved spurious performance. 
# This operation would normally be used when the PLL closed-loop bandwidth is wide, 
# for fast-locking applications. Wide loop bandwidth is seen as a loop bandwidth 
# greater than 1/10 of the RFOUT channel step resolution (fRES). A wide loop 
# filter does not attenuate the spurs to the same level as a narrow loop bandwidth.
# For best noise performance, use the lowest noise setting option. As well as 
# disabling the dither, this setting also ensures that the charge pump is operating 
# in an optimum region for noise performance. This setting is extremely useful 
# where a narrow loop filter bandwidth is available. The synthesizer ensures extremely 
# low noise and the filter attenuates the spurs. The typical performance 
# characteristics give the user an idea of the trade-off in a typical W-CDMA setup 
# for the different noise and spur settings.
# 
# MUXOUT
# 
# The on-chip multiplexer is controlled by Bits [DB28:DB26] (see Figure 26).
# 
# Reference Doubler
# 
# Setting DB25 to 0 feeds the REFIN signal directly to the 10-bit R 
# counter, disabling the doubler. Setting this bit to 1 multiplies the REFIN 
# frequency by a factor of 2 before feeding into the 10-bit R counter. When the doubler 
# is disabled, the REFIN falling edge is the active edge at the PFD input to the 
# fractional synthesizer. When the doubler is enabled, both the rising and falling edges 
# of REFIN become active edges at the PFD input.
# 
# When the doubler is enabled and the lowest spur mode is chosen, the in-band phase 
# noise performance is sensitive to the REFIN duty cycle. The phase noise degradation can 
# be as much as 5 dB for the REFIN duty cycles outside a 45% to 55% range. The phase 
# noise is insensitive to the REFIN duty cycle in the lowest noise mode and when the 
# doubler is disabled.  The maximum allowable REFIN frequency when the doubler is enabled is 30 MHz.
# 
# RDIV2
# 
# Setting the DB24 bit to 1 inserts a divide-by-2 toggle flip-flop between the R 
# counter and PFD, which extends the maximum REFIN input rate. This function allows 
# a 50% duty cycle signal to appear at the PFD input, which is necessary for cycle slip reduction.
# 
# 10-Bit R Counter
# The 10-bit R counter allows the input reference frequency (REFIN) to be divided down to 
# produce the reference clock to the PFD. Division ratios from 1 to 1023 are allowed.
# 
# Double Buffer
# DB13 enables or disables double buffering of Bits [DB22:DB20] in Register 4. The Divider Select 
# section explains how double buffering works.
# 
# Charge Pump Current Setting
# Bits [DB12:DB09] set the charge pump current setting. This should be set to the charge 
# pump current that the loop filter is designed with (see Figure 26).
# 
# LDF
# Setting DB8 to 1 enables integer-N digital lock detect, when the FRAC part of the divider 
# is 0; setting DB8 to 0 enables fractional-N digital lock detect.
# 
# Lock Detect Precision (LDP)
# When DB7 is set to 0, 40 consecutive PFD cycles of 10 ns must occur before digital lock detect 
# is set. When this bit is programmed to 1, 40 consecutive reference cycles of 6 ns must occur 
# before digital lock detect is set. This refers to fractional-N digital lock detect (set DB8 to 0). 
# With integer-N digital lock detect activated (set DB8 to 1), and DB7 set to 0, then five 
# consecutive cycles of 6 ns need to occur before digital lock detect is set. When DB7 
# is set to 1, five consecutive cycles of 10 ns must occur.
# 
# Phase Detector Polarity
# DB6 sets the phase detector polarity. When a passive loop filter, or noninverting 
# active loop filter is used, this should be set to 1. If an active filter with an inverting 
# characteristic is used, it should be set to 0.
# 
# Power-Down
# DB5 provides the programmable power-down mode. Setting this bit to 1 performs a 
# power-down. Setting this bit to 0 returns the synthesizer to normal operation. When in 
# software power-down mode, the part retains all information in its registers. Only if 
# the supply voltages are removed are the register contents lost.
# 
# When a power-down is activated, the following events occur:
# * The synthesizer counters are forced to their load state conditions.
# * The VCO is powered down.
# * The charge pump is forced into three-state mode.
# * The digital lock detect circuitry is reset.
# * The RFOUT buffers are disabled.
# * The input register remains active and capable of loading and latching data.
# 
# Charge Pump Three-State
# DB4 debug_puts the charge pump into three-state mode when programmed to 1. It should 
# be set to 0 for normal operation
# 
# Counter Reset
# DB3 is the R counter and N counter reset bit for the ADF4350. When this is 1, the 
# RF synthesizer N counter and R counter are held in reset. For normal operation, 
# this bit should be set to 0
#
# DB31 | DB30 - DB29 | DB28 - DB26 | DB25 | DB24  | DB23 - DB14 | DB13 | DB12 - DB 9 | 
# RES  | LNOISE/SPR  | MUXOUT      | RDBL | RDIV2 | REF DIVIDER | DBEN | CP CURRENT  |
#
# DB8 | DB7 | DB6 | DB5 | DB4 | DB3 | DB2 - DB0
# LDF | LDP | PDP | PDWN| CP3 | CRST| CONTROL c3-c1 (010)
#
###########################################################################
class register2:
    def __init__(self,
                 lnoise = 0,
                 muxout = "Digital_LD",
                 refx2 = 1,
                 refdiv2 = 0,
                 refdiv = 5,
                 dblbufen = 0,
                 cpcurrent = 15,
                 pdwn = 1,
                 ldf = 0,
                 ldp = 0,
                 pdp = 1,
                 cp3 = 0,
                 creset = 0):

        self.reg = BitArray(32)
        self.reg[-3:] = 0b010 #Control bits
        
        self.modeval = {"3_State" : 0,
                   "Vcc" : 1,
                   "GND" : 2,
                   "REF_/_R" : 3,
                   "RF_/_N" : 4,
                   "Analog_LD" : 5,
                   "Digital_LD" : 6}


        self.set_creset(creset)
        self.set_cp3(cp3)
        self.set_pdwn(pdwn)
        self.set_pdp(pdp)
        self.set_ldp(ldp)
        self.set_ldf(ldf)
        self.set_cpcurrent(cpcurrent)
        self.set_dblbufen(dblbufen)
        self.set_refdiv(refdiv)
        self.set_refdiv2(refdiv2)
        self.set_refx2(refx2)
        self.set_muxout(muxout)
        self.set_lnoise(lnoise)

    def set_creset(self,creset):
        self.creset = creset
        self.reg[-4] = self.creset

    def set_cp3(self,cp3):
        self.cp3 = cp3
        self.reg[-5] = self.cp3

    def set_pdwn(self,pdwn):
        self.pdwn = pdwn
        self.reg[-6] = self.pdwn
 
    def set_pdp(self,pdp):
        self.pdp = pdp
        self.reg[-7] = self.pdp

    def set_ldp(self,ldp):
        self.ldp = ldp
        self.reg[-8] = self.ldp

    def set_ldf(self,ldf):
        self.ldf = ldf
        self.reg[-9] = self.ldf

    def set_cpcurrent(self,cpcurrent):
        self.cpcurrent = cpcurrent
        self.reg[-13:-9] = self.cpcurrent

    def set_dblbufen(self, dblbufen):
        self.dblbufen = dblbufen
        self.reg[-14] = self.dblbufen

    def set_refdiv(self,refdiv):
        self.refdiv = refdiv
        self.reg[-24:-14] = self.refdiv

    def set_refdiv2(self,refdiv2):
        self.refdiv2 = refdiv2
        self.reg[-25] = self.refdiv2

    def set_refx2(self, refx2):
        self.refx2 = refx2
        self.reg[-26] = refx2

    def set_muxout(self,muxout):
        self.muxout = muxout
        self.reg[-29:-26] = self.modeval[self.muxout]

    def set_lnoise(self,lnoise):
        self.lnoise = lnoise
        self.reg[-31:-29] = self.lnoise

###########################################################################
#
# REGISTER 3
#
# Control Bits
# With Bits [C3:C1] set to 0, 1, 1, Register 3 is programmed. 
# 
# CSR Enable
# Setting DB18 to 1 enables cycle slip reduction. This is a method for improving 
# lock times. Note that the signal at the phase fre-quency detector (PFD) must 
# have a 50% duty cycle for cycle slip reduction to work. The charge pump current 
# setting must also be set to a minimum. See the Cycle Slip Reduction for Faster 
# Lock Times section for more information.
# 
# Clock Divider Mode
# Bits [DB16:DB15] must be set to 1, 0 to activate PHASE resync or 0, 1 to activate 
# fast lock. Setting Bits [DB16:DB15] to 0, 0 disables the clock divider. See Figure 27.
# 
# 12-Bit Clock Divider Value
# The 12-bit clock divider value sets the timeout counter for activation of PHASE 
# resync. See the Phase Resync section for more information. It also sets the timeout 
# counter for fast lock. See the Fast-Lock Timer and Register Sequences section for more information.
#
# DB31 - DB24 |DB23 | DB22 | DB21 | DB20 - DB19 | DB18 | DB17 | DB16 - DB15 | DB14 - DB3 | DB2 - DB0
# RESERVED    |BSELC| ABP  | CHGC | RESERVED    | CSREN| RSVD | CLK DIV MODE| CLK DIVIDER| CNTR C3-C1 (011)
# 
###########################################################################
class register3:
    def __init__(self,
                 bandsel = 0,
                 abpw = 0,
                 chargecan = 0,
                 csren = 0,
                 cdivmode = 0,
                 cdiv = 0x87):

        self.reg = BitArray(32)
        self.reg[-3:] = 0b011 #Control bits

        self.set_cdiv(cdiv)
        self.set_cdivmode(cdivmode)
        self.set_csren(csren)
        self.set_chargecan(chargecan)
        self.set_abpw(abpw)
        self.set_bandsel(bandsel)

    def set_cdiv(self,cdiv):
        self.cdiv = cdiv
        self.reg[-15:-3] = self.cdiv
        
    def set_cdivmode(self,cdivmode):
        self.cdivmode = cdivmode
        self.reg[-17:-15] = self.cdivmode

    def set_csren(self,csren):
        self.csren = csren
        self.reg[-19] = self.csren

    def set_chargecan(self,chargecan):
        self.chargecan = chargecan
        self.reg[-22] = self.chargecan

    def set_abpw(self,abpw):
        self.abpw = abpw
        self.reg[-23] = self.abpw

    def set_bandsel(self,bandsel):
        self.bandsel = bandsel
        self.reg[-24] = bandsel

###########################################################################
#
# REGISTER 4
#
# Control Bits
# With Bits [C3:C1] set to 1, 0, 0, Register 4 is programmed. 
# 
# Feedback Select
# DB23 selects the feedback from the VCO output to the N counter. When set to 1, 
# the signal is taken from the VCO directly. When set to 0, it is taken from the 
# output of the output dividers. The dividers enable covering of the wide frequency 
# band (137.5 MHz to 4.4 GHz). When the divider is enabled and the feedback signal 
# is taken from the output, the RF output signals of two separately configured PLLs 
# are in phase. This is useful in some applications where the positive interference 
# of signals is required to increase the power.
# 
# Divider Select
# Bits [DB22:DB20] select the value of the output divider (see Figure 28).
# 
# Band Select Clock Divider Value
# Bits [DB19:DB12] set a divider for the band select logic clock input. The 
# output of the R counter, is by default, the value used to clock the band select 
# logic, but, if this value is too high (>125 kHz), a divider can be switched on 
# to divide the R counter output to a smaller value (see Figure 28).
# 
# VCO Power-Down bar
# DB11 powers the VCO down or up depending on the chosen value.
# 0 - powered up; 1 - powered down
# 
# Mute Till Lock Detect
# If DB10 is set to 1, the supply current to the RF output stage is shut down 
# until the part achieves lock as measured by the digital lock detect circuitry.
# 
# AUX Output Select
# DB9 sets the auxiliary RF output. The selection can be either the output of 
# the RF dividers or fundamental VCO frequency.
# 
# AUX Output Enable
# DB8 enables or disables auxiliary RF output, depending on the chosen value.
# 
# AUX Output Power
# Bits [DB7:DB6] set the value of the auxiliary RF output power level (see Figure 28).
# 
# RF Output Enable
# DB5 enables or disables primary RF output, depending on the chosen value.
# 0 - disable; 1 - enable
# 
# Output Power
# Bits [DB4:DB3] set the value of the primary RF output power level (see Figure 28).
# 0 = -4, 1=-1, 2=+2  3 = +5 (dbm)
#
#
# DB31 - DB24 | DB23 | DB22 - DB20 | DB19 - DB12      | DB11  | DB10 | DB9   | DB8  | 
# RESERVED    | FBSEL| RF DIV SEL  | BAND SEL CLK DIV | VCOPD | MUTE | AUXSEL| AUXEN|
#
#
# DB7 - DB6 | DB5 | DB4 - DB3  | DB2 - DB0
# AUXPWR    | RFEN| OUTPUT PWR | CONTROL C3-C1 (100)
#
###########################################################################
class register4:
    def __init__(self,
                 fbsel = 1,
                 bandseldiv = 140,
                 mute = 0,
                 auxoutsel = 0,
                 auxouten = 0,
                 auxoutpwr = 0,
                 rfouten = 1,
                 rfoutpwr = 0):
              
        self.reg = BitArray(32)
        self.reg[-3:] = 0b100 #Control bits

        self.set_fbsel(fbsel)
        self.set_bandseldiv(bandseldiv)
        self.set_mute(mute)
        self.set_auxoutsel(auxoutsel)
        self.set_auxouten(auxouten)
        self.set_auxoutpwr(auxoutpwr)
        self.set_rfouten(rfouten)
        self.set_rfoutpwr(rfoutpwr)

    def set_outdivider(self,outdivider):
        self.outdivider = outdivider
        #We calculate the log2 value for the actual reg
        tmp_val = int(math.log(outdivider,2))
        self.set_rfdivsel(tmp_val)

    def set_rfoutpwr(self,rfoutpwr):
        self.rfoutpwr = rfoutpwr
        self.reg[-5:-3] = self.rfoutpwr

    def set_rfouten(self,rfouten):
        self.rfouten = rfouten
        #we also need to negate on vcopd
        self.set_vcopd(not rfouten)
        self.reg[-6] = self.rfouten

    def set_auxoutpwr(self,auxoutpwr):
        self.auxoutpwr = auxoutpwr
        self.reg[-8:-6] = self.auxoutpwr

    def set_auxouten(self, auxouten):
        self.auxouten = auxouten
        self.reg[-9] = self.auxouten

    def set_auxoutsel(self, auxoutsel):
        self.auxoutsel = auxoutsel
        self.reg[-10] = self.auxoutsel

    def set_mute(self, mute):
        self.mute = mute
        self.reg[-11] = self.mute

    def set_vcopd(self, vcopd):
        self.vcopd = vcopd
        self.reg[-12] = self.vcopd

    def set_bandseldiv(self, bandseldiv):
        self.bandseldiv = bandseldiv
        self.reg[-20:-12] = self.bandseldiv

    def set_rfdivsel(self, rfdivsel):
        self.rfdivsel = rfdivsel
        self.reg[-23:-20] = self.rfdivsel

    def set_fbsel(self, fbsel):
        self.fbsel = fbsel
        self.reg[-24] = self.fbsel

##########################################################################
#	
# REGISTER 5		
#
# Control Bits
# With Bits [C3:C1] set to 1, 0, 1, Register 5 is programmed. 
# 
# Lock Detect Pin Operation
# Bits [DB23:DB22] set the operation of the lock detect pin (see Figure 29).
#    0 - low ; 1= diglockdet; 2= low, 3=high
#
# DB31 - DB24 | DB23 - DB22 | DB21 | DB20 - DB19 | DB18 - DB3 | DB2 - DB0
# RESERVED    | LOCKDET PIN | RES  | RESERVED    | RESERVED   | CONTROL C3-C1 (101)
#
###########################################################################
class register5:
    def __init__(self,
                 lockdet = 1):
                
        self.reg = BitArray(32)
        self.reg[-3:] = 0b101 #Control bit
        #rev1 only so need to set reserved pins
        self.reg[-21:-19] = 3

        self.set_lockdet(lockdet)

    def set_lockdet(self,lockdet):
        self.lockdet = lockdet
        self.reg[-24:-22] = self.lockdet
