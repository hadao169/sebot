import math

class Encoder():
  encoder_min =  -32768
  encoder_max =  32768
  encoder_range = encoder_max - encoder_min

  encoder_low_wrap = (encoder_range * 0.3) + encoder_min
  encoder_high_wrap = (encoder_range * 0.7) + encoder_min


  def __init__(self, wheel_radius, ticks_per_revolution):

    self.wheel_radius = wheel_radius
    self.ticks_per_revolution = ticks_per_revolution

    # renkaan säde R = 0.1m
    # enkooderin resoluutio E = 1000 tick / kierros

    # renkaan kehä: 2 * pi * R
    # kierrokset per metri = 1m / renkaan kehä
    # ticks per metri = E * (1m / (2 * pi * R)) = E / (2 * pi * R)
    
    self.ticks_per_meter = self.ticks_per_revolution / (2 * math.pi * self.wheel_radius)

    self.offset = None
    self.encoder = None
    self.prev_encoder = None

    self.position = 0
    self.prev_position = None

    self.multiplier = 0


  def update(self, encoder):
    if self.encoder == None:
      self.offset = encoder
      self.prev_encoder = encoder

    self.encoder = encoder

    # enkoodereissa, jotka mittaavat rotaatiota, on usein rajallinen arvoalue (esim. 0–4095 12-bittisellä enkooderilla).
    # Kun enkooderin arvo "kääntyy ympäri" (esim. 4095 -> 0 tai päinvastoin), tämä logiikka varmistaa, että oikea 
    # sijainti säilyy seuraamalla täysiä kierroksia.
    #
    # self.encoder: Nykyinen enkooderin lukema.
    # self.prev_encoder: Edellisen kierroksen enkooderin lukema.
    # self.encoder_low_wrap: Alarajan lähellä oleva kynnysarvo (0 + marginaali)
    # self.encoder_high_wrap: Ylärajan lähellä oleva kynnysarvo (4095 − marginaali)
    # self.multiplier: Laskuri, joka seuraa täysiä kierroksia
    #
    # eli kun edellinen arvo on ylä alueella (esim: 4090-4095) ja nykyinen ala alueella 
    # (esim: 0-5) niin silloin absoluuttinen asema lisääntyy ja toiseen suuntaan taas 
    # absoluuttinen asema vähenee. Kaikissa muissa tapauksissa ollaan samalla kierroksella

    if (self.encoder < self.encoder_low_wrap) and (self.prev_encoder > self.encoder_high_wrap): 
      self.multiplier += 1
    if (self.encoder > self.encoder_high_wrap) and (self.prev_encoder < self.encoder_low_wrap): 
      self.multiplier -= 1

    self.position = self.encoder + self.multiplier * self.encoder_range - self.offset

    self.prev_encoder = self.encoder


  def deltam(self):
    if self.prev_position == None:
      self.prev_position = self.position
      return 0
    else:
      d = (self.prev_position - self.position) / self.ticks_per_meter
      self.prev_position = self.position
      return d
