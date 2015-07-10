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
dark_green   = (  0, 100,   0)
brown        = (139,  69,  19)
gold_hl      = (150, 150,   0)
silver_hl    = (192, 192, 192)

# display settings
xmax = ymax = 600
txt = font.Font(None, 75)
title_font = font.SysFont(None, 75)
start_font = font.SysFont(None, 30)
undo_font = font.SysFont(None, 45)
win_font = font.SysFont(None, 60)
heaven_font = font.SysFont(None, 25)

# game settings
units = 8
