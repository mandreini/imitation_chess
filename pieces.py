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
        """
        load the image associated with the piece given
        :param piece: string - name of the piece for the image
        :return:
          piece_img: pygame.Surface - image to draw
          piece_rect: pygame.Rect - rect object to position image
        """
        loc = "pieces/%s.png" % piece
        piece_img = pygame.image.load(loc)
        piece_rect = piece_img.get_rect()
        return piece_img, piece_rect

    def draw(self, screen, xloc, yloc):
        """
        Draws the piece to the given screen at the given x and y coordinates
        Currently draws the piece_num
        :param screen: pygame.Surface - screen to draw the piece to
        :param xloc: int - x location for the center
        :param yloc: int - y location for the center
        """
        # will just put numbers corresponding to the piece until I get images
        piecetxt = parameters.txt.render(str(self.piece_num), 0, self.piece_color)
        piecetxt_rect = piecetxt.get_rect()
        piecetxt_rect.center = (xloc, yloc)

        screen.blit(piecetxt, piecetxt_rect)

class Pawn(Piece):
    """The pawn piece"""
    piece_num = 1


class Rook(Piece):
    """The rook piece"""
    piece_num = 2

class Knight(Piece):
    """The knight piece"""
    piece_num = 3

class Bishop(Piece):
    """The bishop piece"""
    piece_num = 4

class Queen(Piece):
    """The queen piece"""
    piece_num = 5

class King(Piece):
    """The king piece"""
    piece_num = 6