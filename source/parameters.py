__author__ = 'Matt'

from pygame import font

font.init()

# colors
white        = (255, 255, 255)
grey         = (128, 128, 128)
black        = (  0,   0,   0)
red          = (255,   0,   0)
green        = (  0, 255,   0)
blue         = (  0,   0, 255)

dark_blue    = (  0,   0, 128)
gold_hl      = (150, 150,   0)
silver_hl    = (192, 192, 192)

# display settings
xmax = ymax = 600
txt = font.Font(None, 75)

# game settings
units = 8
