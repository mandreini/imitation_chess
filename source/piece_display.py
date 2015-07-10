__author__ = 'Matt'

import math
import pygame
import parameters

class PieceDisplay(object):

    def __init__(self, width, height, position, pieces_to_not_use, is_team2, theme='default'):
        self.theme = theme
        self.is_team2 = is_team2

        self.piece_options = ['pawn', 'rook', 'knight', 'bishop', 'queen', 'king']

        if not isinstance(pieces_to_not_use, list):
            pieces_to_not_use = [pieces_to_not_use]

        sorted_inds = sorted(pieces_to_not_use, reverse=True)
        for p in sorted_inds:
            self.piece_options.pop(p)

        self.surface = pygame.Rect(position, (width, height))
        self.background_color, self.outline, self.font_color = self._determine_theme_colors()
        self.piece_images = self._load_images()

    def _determine_theme_colors(self):
        """
        Determines the colors corresponding to the theme chosen (currently only supports color changes)
        :return:
        """
        # { key: [background_color, outline, font_color], ... }
        theme_parameters = {
            'default': [parameters.gold_hl, parameters.black, parameters.black],
            'simplistic': [parameters.grey, parameters.black, parameters.black],
            'flipped': [parameters.gold_hl, parameters.black, parameters.black],
            'vibrant': [parameters.silver_hl, parameters.gold_hl, parameters.blue],
            'movement': [parameters.gold_hl, parameters.black, parameters.black],
        }

        if theme_parameters.has_key(self.theme):
            curr_theme = theme_parameters[self.theme]
        else:
            curr_theme = theme_parameters['default']

        return curr_theme

    def _load_images(self):
        """
        load the image associated with the pieces
        :return:
          piece_img: pygame.Surface - image to draw
        """

        piece_names = self.piece_options
        piece_imgs = []
        theme = self.theme
        teamcolor = 'black' if self.is_team2 else 'white'

        for piece_name in piece_names[::-1]:
            if piece_name == 'default':
                theme = '../images'  # loc -> ../images/../images/== ../images/
                teamcolor = 'none'

            loc = "../images/%s/%s-%s.png" % (theme, piece_name, teamcolor)
            piece_img = pygame.image.load(loc)
            piece_imgs.append(piece_img)

        return piece_imgs

    def refresh_theme(self, new_theme):
        """
        This will change the layout of the board without needing to call __init__
        :param new_theme: str - new theme
        :return:
        """
        self.theme = new_theme
        self.background_color, self.outline, self.font_color = self._determine_theme_colors()
        self.piece_images = self._load_images()

class PieceGraveyard(PieceDisplay):
    """This is to display the pieces that have been taken off in the game"""
    def __init__(self, width, height, position, pieces_to_not_use, is_team2, theme='default'):
        super(PieceGraveyard, self).__init__(width, height, position, pieces_to_not_use, is_team2, theme)

        units = len(self.piece_options)
        self.unit_y_poses = [position[1] + unit*height/units for unit in range(1, units+1)]

        self.pieces_taken_off = [0]*5

        self.dead_piece_num = None
        self.dead_piece_img = None
        self.dead_piece_end_pos = None
        self.dead_piece_curr_pos = None

    def add_piece(self, piece_num):
        """
        This will add a piece that was taken off
        :param piece_num: int - piece_num of the piece taken off (see pieces.py)
        :return:
        """
        # ind_piece_num = len(self.pieces_taken_off) - piece_num
        self.pieces_taken_off[piece_num] += 1

    def move_piece(self, curr_pos):
        """
        Determines the next position for the piece to move
        :param curr_pos: tuple - (x, y) coordinates of the piece to move
        """
        curr_x, curr_y = curr_pos
        end_x, end_y = self.dead_piece_end_pos
        b, h = end_x - curr_x, end_y - curr_y
        c = math.sqrt(b*b + h*h)
        theta = math.atan2(h, b)
        ds = 5.

        dx = ds * math.cos(theta)
        dy = ds * math.sin(theta)

        if c > ds:
            self.dead_piece_curr_pos = (curr_x + dx, curr_y + dy)
        else:
            self.add_piece(self.dead_piece_num)
            self.dead_piece_num = None
            self.dead_piece_img = None
            self.dead_piece_end_pos = None
            self.dead_piece_curr_pos = None

    def set_dead_piece(self, piece_name, pos):
        """
        This sets the image, and end_pos for the dead piece as well as initializes the curr_pos
        :param piece_name: string - pieces.Piece.name of the piece
        :param pos: tuple - (row, col) grid coordinates
        :return:
        """
        if piece_name not in self.piece_options:
            self.dead_piece_num = None
            self.dead_piece_img = None
            self.dead_piece_curr_pos = None
            self.dead_piece_end_pos = None
            return

        ind = self.piece_options.index(piece_name)
        img = self.piece_images[ind]

        end_x = self.surface.left
        end_y = self.surface.top + ind*self.surface.height/len(self.piece_options)

        self.dead_piece_num = ind
        self.dead_piece_img = img
        self.dead_piece_curr_pos = pos
        self.dead_piece_end_pos = (end_x, end_y)

    def draw(self, screen):
        """
        Draws to the screen
        :param screen: pygame.Surface object to draw to
        :return:
        """
        pygame.draw.rect(screen, self.background_color, self.surface)
        pygame.draw.rect(screen, self.outline, self.surface, 2)

        left = self.surface.left
        right = self.surface.right
        cell_size = (self.surface.width*2/3, self.surface.height/len(self.pieces_taken_off)*2/3)

        for ind in range(len(self.pieces_taken_off)):
            img = self.piece_images[ind]
            val = self.pieces_taken_off[ind]
            y_pos = self.unit_y_poses[ind]

            img = pygame.transform.scale(img, cell_size)
            img_rect = img.get_rect()
            img_rect.bottomleft = (left+2, y_pos)

            words = 'x%i' % val
            h_txt = parameters.heaven_font.render(words, 1, self.font_color)
            txt_rect = h_txt.get_rect()
            txt_rect.bottomright = (right-2, y_pos)

            screen.blit(img, img_rect)
            screen.blit(h_txt, txt_rect)

        if self.dead_piece_img is not None:
            self.dead_piece_img = pygame.transform.scale(self.dead_piece_img, cell_size)
            dead_piece_rect = self.dead_piece_img.get_rect()
            dead_piece_rect.topleft = self.dead_piece_curr_pos
            screen.blit(self.dead_piece_img, dead_piece_rect)

            # move piece for next frame
            self.move_piece(self.dead_piece_curr_pos)


class PieceMenu(PieceDisplay):
    """The menu object to choose which piece you want to upgrade"""
    def __init__(self, width, height, position, pieces_to_not_use, is_team2, theme='default'):
        super(PieceMenu, self).__init__(width, height, position, pieces_to_not_use, is_team2, theme)

        self.choice = None

    def do_event(self, event, mousex, mousey):
        """
        Processes the event
        :param event: pygame.Event object
        :param mousex: int - x position of the mouse
        :param mousey: int - y position of the mouse
        :return:
        """
        if event.type == pygame.MOUSEBUTTONUP:
            self.get_choice((mousex, mousey))

    def get_choice(self, mouse_pos):
        """
        This will return which piece has been chosen based on where the mouse is.
        Based on: Xi = xL + a / units * width rearranged for a: a = units * (Xi - xL) / width
        :param mouse_pos: tuple - (x-position, y-position) of the mouse at time of click
        :return:
        """
        surface = self.surface
        top = surface.top
        bottom = surface.bottom
        left = surface.left
        right = surface.right
        width = right - left
        units = len(self.piece_options)

        if top < mouse_pos[1] < bottom and left < mouse_pos[0] < right:
            curr_square = units * (right - mouse_pos[0]) / width
            self.choice = curr_square

        else:
            self.choice = None

    def set_position(self, mouse_x, mouse_y):
        """
        This will determine the position of the box based on which team and within the screen
        :param mouse_x: int - x position of the mouse
        :param mouse_y: int - y position of the mouse
        :return:
        """
        width = self.surface.width
        xmax = parameters.xmax

        if self.is_team2:
            self.surface.bottom = mouse_y
        else:
            self.surface.top = mouse_y

        if mouse_x + width >= xmax:
            self.surface.right = mouse_x
        else:
            self.surface.left = mouse_x

        self.choice = None

    def draw(self, screen):
        """
        Draws the menu display to the screen
        :param screen: pygame.Surface object to draw to
        :return:
        """
        pygame.draw.rect(screen, self.background_color, self.surface)
        pygame.draw.rect(screen, self.outline, self.surface, 2)

        left = self.surface.left
        top = self.surface.top
        width = self.surface.width
        height = self.surface.height
        units = len(self.piece_options)

        for ind in range(len(self.piece_options)):
            img = self.piece_images[ind]
            img = pygame.transform.scale(img, (height, width / units))

            rect = img.get_rect()
            img_pos = left + ind*width/units
            rect.topleft = (img_pos, top)

            screen.blit(img, rect)
