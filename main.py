__author__ = 'Matt'
__contact__ = 'matthew@andreini.us'

import pygame
import board
import parameters

pygame.init()
xmax = parameters.xmax
ymax = parameters.ymax
reso = (xmax, ymax)
scr = pygame.display.set_mode(reso)

gameboard = board.Board(width=400, height=400)

running = True
t0 = pygame.time.get_ticks() * 0.001

while running:
    t = pygame.time.get_ticks() * 0.001
    dt = t - t0
    t0 = t

    pygame.event.pump()

    keys = pygame.key.get_pressed()

    if keys[pygame.K_ESCAPE]:
        running = False

    scr.fill(parameters.white)
    gameboard.draw(scr)
    pygame.display.flip()

pygame.quit()