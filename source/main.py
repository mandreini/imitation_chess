__author__ = 'Matt'
__contact__ = 'matthew@andreini.us'

import pygame

import board
import parameters
import menu
import piece_display

pygame.init()
xmax = parameters.xmax
ymax = parameters.ymax
reso = (xmax, ymax)
scr = pygame.display.set_mode(reso)

# display objects
gamemenu = menu.Menu(in_menu=True)
gameboard = board.Board(width=400, height=400)
cell_width = gameboard.surface.width/parameters.units
cell_height = gameboard.surface.height/parameters.units

team_1_graveyard = piece_display.PieceGraveyard(width=cell_width+25,
                                                height=cell_height*5,
                                                position=(xmax/6 - 90, ymax/6),
                                                pieces_to_not_use=5,
                                                is_team2=False)

team_2_graveyard = piece_display.PieceGraveyard(width=cell_width+25,
                                                height=cell_height*5,
                                                position=(5*xmax/6+10, 2*ymax/6),
                                                pieces_to_not_use=5,
                                                is_team2=True)

team_1_pawn_upgrade_menu = piece_display.PieceMenu(width=cell_width*4,
                                                   height=cell_height,
                                                   position=(xmax/2, ymax/4),
                                                   pieces_to_not_use=[0, 5],
                                                   is_team2=False)

team_2_pawn_upgrade_menu = piece_display.PieceMenu(width=cell_width*4,
                                                   height=cell_height,
                                                   position=(xmax/2, ymax/4),
                                                   pieces_to_not_use=[0, 5],
                                                   is_team2=True)

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
            gamemenu.do_event(event, mouse_x, mouse_y)

            if gamemenu.choice_made:
                theme = gamemenu.themes[gamemenu.curr_theme_ind]

                if gamemenu.start_new_game:
                    gameboard.__init__(width=400, height=400, theme=theme)

                if theme != gameboard.theme:
                    gameboard.refresh_theme(theme)
                    team_1_graveyard.refresh_theme(theme)
                    team_2_graveyard.refresh_theme(theme)
                    team_1_pawn_upgrade_menu.refresh_theme(theme)
                    team_2_pawn_upgrade_menu.refresh_theme(theme)

                running = not gamemenu.exit
                gamemenu.choice_made = False

        elif not gameboard.pawn_at_end:
            graveyard = team_1_graveyard if gameboard.turn_player_2 else team_2_graveyard
            gameboard.do_event(event, mouse_x, mouse_y, graveyard)

            if gameboard.pawn_at_end:
                # *gameboard.turn_player_2 was switched before this is called
                team_pawn_upgrade = team_2_pawn_upgrade_menu if not gameboard.turn_player_2 else team_1_pawn_upgrade_menu
                team_pawn_upgrade.set_position(mouse_x, mouse_y)

        elif gameboard.pawn_at_end:
            team_pawn_upgrade.do_event(event, mouse_x, mouse_y)

            if team_pawn_upgrade.choice is not None:
                gameboard.pawn_upgrade(gameboard.pawn_to_upgrade, is_team2=team_pawn_upgrade.is_team2,
                                       choice=team_pawn_upgrade.choice)

        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    if keys[pygame.K_ESCAPE]:
        gamemenu.in_menu = True
        # gameboard.pawn_at_end = False
        #
        # if gameboard.can_undo:
        #     gameboard.undo()
        #     gameboard.past_moves = []

    # update screen
    if gamemenu.in_menu:
        gamemenu.draw(scr)
    else:
        if gameboard.pawn_at_end:
            team_pawn_upgrade.draw(scr)
        else:
            gameboard.draw(scr, mouse_x, mouse_y)
            team_1_graveyard.draw(scr)
            team_2_graveyard.draw(scr)

    pygame.display.flip()

pygame.quit()
