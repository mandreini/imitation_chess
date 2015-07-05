__author__ = 'Matt'
__contact__ = 'matthew@andreini.us'

import pygame
import board
import parameters
import menu

pygame.init()
xmax = parameters.xmax
ymax = parameters.ymax
reso = (xmax, ymax)
scr = pygame.display.set_mode(reso)

gamemenu = menu.Menu(in_menu=True)
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
        if gamemenu.in_menu:
            gamemenu.do_menu_event(event, mouse_x, mouse_y)

            if gamemenu.choice_made:
                if gamemenu.start_new_game:
                    theme = gamemenu.themes[gamemenu.curr_theme_ind]
                    gameboard.__init__(width=400, height=400, theme=theme)

                running = not gamemenu.exit
                gamemenu.choice_made = False

        else:
            gameboard.do_game_event(event, mouse_x, mouse_y)

        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    if keys[pygame.K_ESCAPE]:
        gamemenu.in_menu = True

    # update screen
    if gamemenu.in_menu:
        gamemenu.draw(scr)
    else:
        gameboard.draw(scr, mouse_x, mouse_y)

    pygame.display.flip()

pygame.quit()