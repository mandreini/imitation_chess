__author__ = 'Matt'

import pygame
import parameters
import pieces

class Board(object):
    def __init__(self, width, height):
        self.units = 8
        self.odd_color = parameters.blue
        self.even_color = parameters.red
        self.outline = parameters.black
        self.surface = pygame.Rect( (0,0), (width, height) )
        self.surface.center = (parameters.xmax /2, parameters.ymax /2)

        row = [0] * self.units
        grid = [row[:] for j in range(self.units)]
        self.grid = self._setup_grid(grid)

    def _setup_grid(self, grid):
        """
        This will initialize the chessboard in memory. Currently only supports the traditional start
        :param grid: 8x8 list of 0's
        :return: grid populated with pieces
        """
        # row of pawns
        for i in range(self.units):
            grid[1][i] = pieces.Pawn(False)
            grid[-2][i] = pieces.Pawn(True)

        for team in range(-1, 1, 1):  # iterates -1 and 0
            side = grid[team]
            # rooks
            side[0] = pieces.Rook(-team)
            side[-1] = pieces.Rook(-team)

            # knights
            side[1] = pieces.Knight(-team)
            side[-2] = pieces.Knight(-team)

            # bishops
            side[2] = pieces.Bishop(-team)
            side[-3] = pieces.Bishop(-team)

            # queen
            side[3] = pieces.Queen(-team)

            # king
            side[4] = pieces.King(-team)

        return grid

    def draw(self, screen):
        """
        Draws the board with the pieces
        :param screen: pygame.Surface - screen to draw the board to
        """
        # outline
        pygame.draw.rect(screen, self.outline, self.surface, 5)

        # checkerboard
        surfacetop, surfaceleft = self.surface.topleft
        cellsize = self.surface.width / self.units
        cell = pygame.Rect((0,0), (cellsize, cellsize))
        for colnum in range(self.units):
            cellposy = surfaceleft + (colnum * self.surface.width / self.units)
            evencol = colnum % 2 == 0
            for rownum in range(self.units):
                cellposx = surfacetop + (rownum * self.surface.height / self.units)
                cell.topleft = (cellposy, cellposx)
                evenrow = rownum % 2 == 0
                if evenrow == evencol:
                    cell_color = self.even_color
                else:
                    cell_color = self.odd_color

                pygame.draw.rect(screen, cell_color, cell, 0)

                # pieces
                cell_piece = self.grid[rownum][colnum]
                if isinstance(cell_piece, pieces.Piece):
                    cell_piece.draw(screen, cell.centerx, cell.centery)
