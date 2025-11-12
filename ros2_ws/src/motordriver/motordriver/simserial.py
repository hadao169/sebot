import time
import threading

class SimSerial():
  def __init__(self):
    self.answer = [0,0,0,0,0,0]
    self.response = 0
    self.encoder_min = -32768
    self.encoder_max = 32768
    self.sim_odo_left = SimuOdo(self.encoder_min, self.encoder_max)
    self.sim_odo_right = SimuOdo(self.encoder_min, self.encoder_max)
 
  def write(self,message):
    try:
      a = message.decode().split(";")
      self.sim_odo_left.set_speed(int(a[1]))
      self.sim_odo_right.set_speed(int(a[2]))

      self.answer[4] = self.sim_odo_left.speed
      self.answer[5] = self.sim_odo_right.speed

    except Exception as err:
      pass
    
    self.answer[0] = self.sim_odo_left.tell_ticks()
    self.answer[1] = self.sim_odo_right.tell_ticks()
    
    self.response = 1
  
  def inWaiting(self):
    return self.response

  def readline(self):
    retval = ";".join([str(x) for x in self.answer]).encode()
    self.response = 0
    return retval


class SimuOdo():
    """Tämä luokka 'simuloi' fyysistä enkooderia, mikä mahdollistaa ROS2-koodikokonaisuuden ajamisen ilman fyysistä laitteistoa."""
    def __init__(self, encoder_min, encoder_max):
        self.speed = 0
        self.ticks = 0
        self.encoder_min = encoder_min
        self.encoder_max = encoder_max
        thread = threading.Thread(target = self.run_periodically)
        thread.start()
    def run_periodically(self):
        while True:
            self.roll()
            time.sleep(0.1)
   
    def set_speed(self, speed):
        self.speed = speed

    def roll(self):
        self.ticks = self.ticks + self.speed
        if self.ticks > self.encoder_max:
          self.ticks -= self.encoder_max-self.encoder_min
        if self.ticks < self.encoder_min:
          self.ticks += self.encoder_max-self.encoder_min

    def tell_ticks(self):
        return self.ticks


