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
    # do time
    t = pygame.time.get_ticks() * 0.001
    dt = t - t0
    t0 = t

    # do events
    pygame.event.pump()

    mouse_x, mouse_y = pygame.mouse.get_pos()

    events = pygame.event.get()

    for event in events:
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            new_sel_cell = gameboard.get_square(mouse_x, mouse_y)
            gameboard.selected_cell = new_sel_cell if gameboard.selected_cell != new_sel_cell else None
            gameboard.grab_piece()

        if event.type == pygame.MOUSEBUTTONUP:
            gameboard.drop_piece(mouse_x, mouse_y)

    keys = pygame.key.get_pressed()

    if keys[pygame.K_ESCAPE]:
        running = False

    # update screen
    scr.fill(parameters.white)
    gameboard.draw(scr, mouse_x, mouse_y)

    pygame.display.flip()

pygame.quit()