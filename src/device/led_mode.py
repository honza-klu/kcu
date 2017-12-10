import random
import math
import neopixel
import time
import machine

#Neopixel
MAX_INT = 16
CLR_GRAY = (MAX_INT, MAX_INT, MAX_INT)
CLR_BLACK = (0, 0, 0,)
CLR_RED = (MAX_INT, 0, 0)
CLR_GREEN = (0, MAX_INT, 0)
CLR_BLUE = (0, 0, MAX_INT)

CLR_TRUE_WHITE = (255, 255, 255)

#LED_NUM = 300
np_pin = machine.Pin(12)

def setChan(arr, idx, ch, val):
  pnt = arr[idx]
  if(ch==0):
    pnt=(val, pnt[1], pnt[2])
  elif(ch==1):
    pnt=(pnt[0], val, pnt[2])
  elif(ch==2):
    pnt=(pnt[0], pnt[1], val)
  else:
    raise Exception("Channel out of bounds")
  arr[idx] = pnt

class LedMode():
  def __init__(self, led_num):
    self.LED_NUM = led_num
    self.np = neopixel.NeoPixel(np_pin, self.LED_NUM, timing=1)

  def _check_stop(self, until):
    if(time.time()>until):
      return True
    else:
      return False
      
  
  def sinWaves(self, until, wave_r_freq=2, wave_g_freq=3, wave_b_freq=4, r_spd=1, g_spd=2, b_spd=-1):
    x = 0
    while True:
      x = x + 1
      for i in range(0, self.LED_NUM):
        p_r = i + x*r_spd
        p_g = i + x*g_spd
        p_b = i + x*b_spd
        r_amp = int((MAX_INT*(math.sin(2*math.pi * p_r/self.LED_NUM * wave_r_freq)+1)/2))
        g_amp = int((MAX_INT*(math.sin(2*math.pi * p_g/self.LED_NUM * wave_g_freq)+1)/2))
        b_amp = int((MAX_INT*(math.sin(2*math.pi * p_b/self.LED_NUM * wave_b_freq)+1)/2))
        self.np[i] = (r_amp, g_amp, b_amp)
      self.np.write()
      if(self._check_stop(until)):
        return
  
  def randomColorBlock(self, until, col_number=4, change_perc=0.15, block_size=(5,25)):
    clrs =[]
    for i in range(0, col_number):
      clrs.append((random.randint(0, MAX_INT-1), random.randint(0, MAX_INT-1), random.randint(0, MAX_INT-1)))
    while True:
      bs = random.randint(block_size[0], block_size[1])
      start = random.randint(0, self.LED_NUM-1)
      col = clrs[random.randint(0, col_number-1)]
      for i in range(start, start + bs):
        self.np[i % self.LED_NUM] = col
      self.np.write()
      if(self._check_stop(until)):
        return
      time.sleep_ms(10)
      if(random.uniform(0, 1.0)< change_perc):
        clrs[random.randint(0, col_number-1)] = (random.randint(0, MAX_INT-1), random.randint(0, MAX_INT-1), random.randint(0, MAX_INT-1))
        
  def randomColorNoise(self, until, col_number=4, change_perc=0.15, batch_size=25):
    clrs =[]
    for i in range(0, col_number):
      clrs.append((random.randint(0, MAX_INT-1), random.randint(0, MAX_INT-1), random.randint(0, MAX_INT-1)))
    while True:
      for i in range(0, batch_size):
        self.np[random.randint(0, self.LED_NUM-1)] = clrs[random.randint(0, col_number-1)]
      self.np.write()
      if(self._check_stop(until)):
        return
      if(random.uniform(0, 1.0)< change_perc):
        clrs[random.randint(0, col_number-1)] = (random.randint(0, MAX_INT-1), random.randint(0, MAX_INT-1), random.randint(0, MAX_INT-1))
  
  def police(self, until):
    while True:
      for i in range(0, self.LED_NUM//2):
        self.np[i] = CLR_BLUE
      for i in range(self.LED_NUM//2, self.LED_NUM):
        self.np[i] = CLR_RED
      self.np.write()
      if(self._check_stop(until)):
        return
      time.sleep_ms(500)
      for i in range(0, self.LED_NUM//2):
        self.np[i] = CLR_RED
      for i in range(self.LED_NUM//2, self.LED_NUM):
        self.np[i] = CLR_BLUE
      self.np.write()
      time.sleep_ms(500)
  
  def knightrider(self, until, stripe_len=16):
    x = 0
    self.np.fill(CLR_BLACK)
    self.np.write()
    while True:
      t_start = time.ticks_ms()
      for i in range(0, self.LED_NUM):
        if(((x + i) % self.LED_NUM)==0):
          for a in range(0, stripe_len):
            setChan(self.np, (i+a) % self.LED_NUM, 0, MAX_INT//(stripe_len-a+1))
          setChan(self.np, (i+stripe_len) % self.LED_NUM, 0, 0)
          off = self.LED_NUM//2
          for a in reversed(range(0, stripe_len)):
            setChan(self.np, (-i+a+off) % self.LED_NUM, 2, MAX_INT//(stripe_len-a+1))
          setChan(self.np, (-i+stripe_len+off) % self.LED_NUM, 2, 0)

#        if(((self.LED_NUM - x + i) % self.LED_NUM)==0):
#          setChan(self.np, (i+9) % self.LED_NUM, 2, MAX_INT)
#          setChan(self.np, (i+8) % self.LED_NUM, 2, MAX_INT//2)
#          setChan(self.np, (i+7) % self.LED_NUM, 2, MAX_INT//2)
#          setChan(self.np, (i+6) % self.LED_NUM, 2, MAX_INT//4)
#          setChan(self.np, (i+5) % self.LED_NUM, 2, MAX_INT//4)
#          setChan(self.np, (i+4) % self.LED_NUM, 2, MAX_INT//8)
#          setChan(self.np, (i+3) % self.LED_NUM, 2, MAX_INT//8)
#          setChan(self.np, (i+2) % self.LED_NUM, 2, MAX_INT//16)
#          setChan(self.np, (i+1) % self.LED_NUM, 2, MAX_INT//16)
#          setChan(self.np, (i+0) % self.LED_NUM, 2, 0)
      self.np.write()
      if(self._check_stop(until)):
        return
      x += 1
      t_end = time.ticks_ms()
      print("fps:%f" % (1000/(t_end-t_start)))

  def stroboscope(self, until):
    while True:
      t_start = time.ticks_ms()
      self.np.fill(CLR_BLACK)
      self.np.write()
      self.np.fill(CLR_GRAY)
      self.np.write()
      if(self._check_stop(until)):
        return
      t_end = time.ticks_ms()
      print("fps:%f" % (1000/(t_end-t_start)))