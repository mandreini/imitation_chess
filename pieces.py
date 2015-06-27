from abc import ABCMeta, abstractmethod
import pygame
import parameters

__author__ = 'Matt'

class Piece(object):

    __metaclass__ = ABCMeta

    piece_num = 0

    def __init__(self, is_team2):
        if is_team2:
            self.piece_color = parameters.white
        else:
            self.piece_color = parameters.black

    def load_image(self, piece):
        loc = "pieces/%s.png" % piece
        self.piece_img = pygame.image.load(loc)
        self.piece_rect = self.piece_img.get_rect()

    def draw(self, screen, xloc, yloc):
        # will just put numbers corresponding to the piece until I get images
        piecetxt = parameters.txt.render(str(self.piece_num), 0, self.piece_color)
        piecetxt_rect = piecetxt.get_rect()
        piecetxt_rect.center = (xloc, yloc)

        screen.blit(piecetxt, piecetxt_rect)

class Pawn(Piece):

    piece_num = 1


class Rook(Piece):

    piece_num = 2

class Knight(Piece):

    piece_num = 3

class Bishop(Piece):

    piece_num = 4

class Queen(Piece):

    piece_num = 5

class King(Piece):

    piece_num = 6