import time
from ustruct import unpack

ADDR=0x39
INT_TIME_13_7_MS=0x00
INT_TIME_101_MS=0x01
INT_TIME_402_MS=0x02
GAIN_LOW=0x00
GAIN_HIGH=0x10


CONTROL_REG=0x80
TIMING_REG=0x81
THRESHLOWLOW_REG=0x82
THRESHLOWHI_REG=0x83
THRESHHILOW_REG=0x84
THRESHHIHI_REG=0x85
INTERRUPT_REG=0x86
ID_REG=0x8A
DATA0LOW_REG=0x8C
DATA0HI_REG=0x8D
DATA1LOW_REG=0x8E
DATA1HI_REG=0x8F


class myAPDS9301:
    def _read_register(self, register):
        result = unpack('BB', self._i2c.readfrom_mem(ADDR, register, 2))
        return ( (result[1] << 8) | result[0] )

    def read_reg8(self, register):
        result = self._i2c.readfrom_mem(ADDR, register, 1)
        return ( result[0])

    def write_reg8(self, register, value):
        self._i2c.writeto_mem(ADDR, register, bytes([value]))
        time.sleep(0.02)

    def set_gain(self, _gain):
        self.CONF=self.read_reg8(TIMING_REG)
        #get gain bit
        self.CONF&=(~0x10)
        if _gain==1:
            self.CONF|=(GAIN_HIGH & 0x10)
        else:
            self.CONF|=(GAIN_LOW & 0x10)
        #set GAIN
        self.write_reg8(TIMING_REG,self.CONF)
    
    def set_int_time(self, _INT_TIME):
        self.CONF=self.read_reg8(TIMING_REG)
        #get self.CONFiguration and remove INTEG bits (mask binary 0000011, reverse 1111100)
        self.CONF&=(~0x03)
        if _INT_TIME==0:
            self.CONF|=(INT_TIME_13_7_MS & 0x03)
            print("setting integration time to 13.7ms")
        elif _INT_TIME==1:
            self.CONF|=(INT_TIME_101_MS & 0x03)
            print("setting integration time to 101ms")
        else:
            self.CONF|=(INT_TIME_402_MS & 0x03)
            print("setting integration time to 402ms")
        self.write_reg8(TIMING_REG,self.CONF)
        
    def __init__(self, i2c):
        self._i2c = i2c
        #SCL_PIN=machine.Pin(1)
        #SDA_PIN=machine.Pin(0)
        print("initialize ADPS9301 i2c")
        #self._i2c=machine.I2C(0,scl=SCL_PIN, sda=SDA_PIN,freq=400000)
        self.CONF=0x00
        self.ch0=0
        self.ch1=0

        #power on chip
        self.write_reg8(CONTROL_REG, 0x3)
        #wait on power on
        time.sleep(1)
        #Integration time 13,7ms
        self.set_int_time(0)
        
        #set GAIN to LOW (LOW is by default but to be sure its low)
        self.set_gain(0)
        
        
    def get_light(self):
        self.ch0=self._read_register(0x8c)
        self.ch1=self._read_register(0x8e)
        #get gain
        if (self.CONF & 0x10) == 1:
            self.ch0*=16
            self.ch1*=16
        #get TIMING
        if (self.CONF & 0x03)==0:
            self.ch0*=1/0.034
            self.ch1*=1/0.034
        elif (self.CONF & 0x03)==1:
            self.ch0*=1/0.252
            self.ch1*=1/0.252
        elif (self.CONF & 0x03)==2:
            self.ch0*=1
            self.ch1*=1
        if (self.ch1 > 0 and self.ch0==0) or (self.ch0==0 and self.ch1==0):
            lux=0
            return 0
        
        ratio=self.ch1/self.ch0
        if ratio>1.3:
            lux=0
        elif ratio>0.8:
            lux=(0.00146*self.ch0)-(0.00112*self.ch1)
        elif ratio>0.61:
            lux=(0.0128*self.ch0)-(0.0153*self.ch1)
        elif ratio>0.5:
            lux=(0.0224*self.ch0)-(0.031*self.ch1)
        else:
            lux=(0.0304*self.ch0)-(0.062*self.ch0*((self.ch1/self.ch0)**1.4))
        return lux

    def get_raw(self,channel):
        if channel==0:
            return self.ch0
        else:
            return self.ch1

    def power(self,state):
        if state==0:
            PWR=0x00
            self.write_reg8(CONTROL_REG, PWR)
        else:
            PWR=0x03
            self.write_reg8(CONTROL_REG, PWR)
            self.write_reg8(TIMING_REG,self.CONF)
            time.sleep(1)
            
