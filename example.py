from myAPDS9301 import *
import machine


SCL_PIN=machine.Pin(1)
SDA_PIN=machine.Pin(0)
i2c=machine.I2C(0,scl=SCL_PIN, sda=SDA_PIN,freq=400000)


sensor=myAPDS9301(i2c)
for e in range(10):
   lux=sensor.get_light()
   print("LUX:", lux)
   time.sleep(1)

#default integration time 13.7ms
sensor.set_int_time(0)

for e in range(10):
   lux=sensor.get_light()
   print("LUX:", lux)
   time.sleep(1)
#default integration time 13.7ms --> 0
#integration time 101ms --> 1
#integration time 407ms --> 2 or any other value

sensor.set_int_time(1)

for e in range(10):
   lux=sensor.get_light()
   print("LUX:", lux)
   time.sleep(1)

#integration time 13,7ms
sensor.set_int_time(1)
#set high gain
#high gain=1
#low gain=0
sensor.set_gain(1)

for e in range(10):
   lux=sensor.get_light()
   print("LUX:", lux)
   time.sleep(1)
