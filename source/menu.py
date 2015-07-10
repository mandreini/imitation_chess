__author__ = 'Matt'

import copy
import pygame
import parameters

class Menu(object):
    """The menu object for imitation_chess"""

    def __init__(self, in_menu):
        # indices
        self.ind_txt = 0
        self.ind_txt_pos = 1
        self.ind_background = 2
        self.ind_back_pos = 3

        # buttons
        title_button = self._create_button(parameters.title_font, 'Imitation Chess', parameters.white,
                                           (parameters.xmax/2, parameters.ymax/4))
        start_button = self._create_button(parameters.start_font, "Play Game", parameters.white,
                                           (parameters.xmax/2, 2*parameters.xmax/3), parameters.gold_hl)
        continue_button = self._create_button(parameters.start_font, "Continue", parameters.white,
                                           (parameters.xmax/2, 2*parameters.ymax/3 + 30), parameters.silver_hl)
        exit_button = self._create_button(parameters.start_font, "Exit game", parameters.white,
                                          (parameters.xmax/2, 2*parameters.ymax/3 + 75), parameters.red)
        theme_title = self._create_button(parameters.start_font, "Theme", parameters.white,
                                          (parameters.xmax/2, parameters.ymax/2 - 25))

        default_theme = self._create_button(parameters.start_font, "default", parameters.white,
                                            (parameters.xmax/2, parameters.ymax/2), parameters.blue)
        simple_theme = self._create_button(parameters.start_font, "simple", parameters.white,
                                           (parameters.xmax/2, parameters.ymax/2), parameters.blue)
        flipped_theme = self._create_button(parameters.start_font, "flipped", parameters.white,
                                            (parameters.xmax/2, parameters.ymax/2), parameters.blue)
        vibrant_theme = self._create_button(parameters.start_font, "vibrant", parameters.white,
                                            (parameters.xmax/2, parameters.ymax/2), parameters.blue)
        movement_theme = self._create_button(parameters.start_font, "movement", parameters.white,
                                             (parameters.xmax/2, parameters.ymax/2), parameters.blue)

        self.themes = ['default', 'simplistic', 'flipped', 'vibrant', 'movement']
        self.theme_buttons = [default_theme, simple_theme, flipped_theme, vibrant_theme, movement_theme]
        self.curr_theme_ind = 0
        self.curr_theme_button = self.theme_buttons[self.curr_theme_ind]

        self.buttons = [title_button, start_button, continue_button, exit_button, self.theme_buttons[self.curr_theme_ind], theme_title]
        self.rects = [b[self.ind_txt_pos] for b in self.buttons]
        self.backs = [b[self.ind_background] for b in self.buttons]

        self.background_color = parameters.black
        self.in_menu = in_menu
        self.start_new_game = True
        self.exit = False
        self.choice_made = False

    @staticmethod
    def _create_button(font, words, color, position, background_color=None, background_offset=(10, 4)):
        txt = font.render(words, 1, color)
        rect = txt.get_rect()
        rect.center = position

        if background_color is not None:
            background_size = (rect.width + background_offset[0], rect.height + background_offset[1])
            background = pygame.Surface(background_size)
            background.fill(background_color)
            back_rect = background.get_rect()
            back_rect.center = position

        else:
            background, back_rect = None, None

        return txt, rect, background, back_rect

    def do_event(self, event, mousex, mousey):
        """
        Processes events for in the menu
        :param event: pygame.Event object
        :param mousex: int - x position of the mouse
        :param mousey: int - y position of the mouse
        """
        start_rect = self.rects[1]
        continue_rect = self.rects[2]
        exit_rect = self.rects[3]
        theme_rect = self.rects[4]

        start_back = self.backs[1]
        continue_back = self.backs[2]
        exit_back = self.backs[3]
        theme_back = self.backs[4]

        in_start = start_rect.collidepoint((mousex, mousey))
        in_continue = continue_rect.collidepoint((mousex, mousey))
        in_exit = exit_rect.collidepoint((mousex, mousey))
        in_theme = theme_rect.collidepoint((mousex, mousey))

        if event.type == pygame.MOUSEBUTTONDOWN:
            if in_start: start_back.set_alpha(128)
            if in_continue: continue_back.set_alpha(128)
            if in_exit: exit_back.set_alpha(128)
            if in_theme: theme_back.set_alpha(128)

        if event.type == pygame.MOUSEBUTTONUP:
            self.choice_made = True

            if in_start:
                self.start_new_game = True
                self.in_menu = False
                self.choice_made = True
            if in_continue:
                self.in_menu = False
                self.start_new_game = False
                self.choice_made = True
            if in_exit: self.exit = True
            if in_theme:
                self.curr_theme_ind = self.curr_theme_ind + 1 if self.curr_theme_ind < len(self.themes)-1 else 0
                self.buttons[4] = self.theme_buttons[self.curr_theme_ind]  # feels ugly, but can't manage a pointer-abuse :/

            for back in self.backs:
                if back is not None:
                    back.set_alpha(255)

    def draw(self, screen):
        """
        Draws the menu to the screen
        :param screen: pygame.Surface object to draw things to
        """
        screen.fill(self.background_color)

        for button in self.buttons:
            if button[self.ind_background] is not None:
                screen.blit(button[self.ind_background], button[self.ind_back_pos])

            screen.blit(button[self.ind_txt], button[self.ind_txt_pos])
