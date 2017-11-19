# Main application file
print("MAIN START")

import machine
from machine import I2C
import math
import neopixel
import lsm303
import time

#Neopixel
CLR_GRAY = (8, 8, 8,)
LED_NUM = 600
np_pin = machine.Pin(12)

#INS
SCL_PIN = machine.Pin(33)
SDA_PIN = machine.Pin(32)
i2c = I2C(-1,sda=SDA_PIN, scl=SCL_PIN, freq=100000)

lsm = lsm303.LSM303D(i2c)
print(i2c.scan())

def main():
  np = neopixel.NeoPixel(np_pin, LED_NUM, timing=1)
  while True:
    t_start = time.ticks_ms()
    #for i in range(0, LED_NUM):
    #  np[i] = CLR_GRAY
    np.write()
    (acc_data, mag_data) = lsm.read()
    time.sleep(1)
    a_x = acc_data[0]/1000
    a_y = acc_data[1]/1000
    a_z = acc_data[2]/1000
    roll = math.atan2(a_z, a_x) /2/3.14 * 360
    print("x=%f y=%f z=%f" % (a_x, a_y, a_z))
    print("roll=%f" % (roll))
    print("G=%f" % (math.sqrt(acc_data[0]**2 + acc_data[1]**2 + acc_data[2]**2)))
    t_end = time.ticks_ms()
    print("fps:%f" % (1000/(t_end-t_start)))

try:
  #run main app here to reset on unhandled exceptions
  main()
except Exception as e:
  print("Unhandled exception:%s" % (str(e),))
  print("Runtime error encountered. Restarting in 10s")
  time.sleep(60.0)
  print("Restarting now!")
  machine.reset()
print("MAIN END")