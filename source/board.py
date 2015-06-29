__author__ = 'Matt'

import pygame
import parameters
import pieces

class Board(object):
    def __init__(self, width, height):
        self.units = parameters.units
        self.odd_color = parameters.blue
        self.even_color = parameters.dark_blue
        self.outline = parameters.black
        self.surface = pygame.Rect((0,0), (width, height))
        self.surface.center = (parameters.xmax/2, parameters.ymax/2)
        self.find_cell_x = lambda pos: self.surface.left + pos * width / self.units
        self.find_cell_y = lambda pos: self.surface.top + pos * height / self.units

        row = [0] * self.units
        grid = [row[:] for j in range(self.units)]
        self.grid = self._setup_grid(grid)

        self.selected_cell = None
        self.held_piece = None
        self.piece_original_pos = None
        self.piece_move_options = None

        self.turn_player_2 = False

    def _setup_grid(self, grid):
        """
        This will initialize the chessboard in memory. Currently only supports the traditional start
        :param grid: 8x8 list of 0's
        :return: grid populated with pieces
        """

        # 2 rows of pawns
        for i in range(self.units):
            grid[1][i] = pieces.Pawn(True, (1, i))
            grid[-2][i] = pieces.Pawn(False, (-2, i))

        for team in range(-1, 1, 1):  # iterates -1 and 0
            # -team as team == -1 -> player 2 -> --1 = +1 -> is_team2 = True
            #          team ==  0 -> player 1 ->  -0 =  0 -> is_team2 = False

            side = grid[team]
            team_2 = not bool(team)

            # rooks
            side[0] = pieces.Rook(team_2, (0, team))
            side[-1] = pieces.Rook(team_2, (-1, team))

            # knights
            side[1] = pieces.Knight(team_2, (1, team))
            side[-2] = pieces.Knight(team_2, (-2, team))

            # bishops
            side[2] = pieces.Bishop(team_2, (2, team))
            side[-3] = pieces.Bishop(team_2, (-3, team))

            # queen
            side[3] = pieces.Queen(team_2, (3, team))

            # king
            side[4] = pieces.King(team_2, (4, team))

        return grid

    def get_square(self, mousex, mousey):
        """
        Returns the (2-D) index of the square/cell/box that the mouse is currently over using
        Xi = xL + a/units * width rearranged for a: a = units * (Xi - xL) / width
        and similar for y
        :param mousex: int - x position of the mouse
        :param mousey: int - y position of the mouse
        :return: tuple - 2 elements corresponding to the cell the mouse is over, for use in self.grid
        """
        surface = self.surface
        left = surface.left
        right = surface.right
        top = surface.top
        bottom = surface.bottom
        in_square_x = left < mousex < right
        in_square_y = top < mousey < bottom

        if not in_square_x or not in_square_y:
            return None
        else:
            column = (self.units * (mousex - left) / surface.width)
            row = (self.units * (mousey - top) / surface.height)
            return row, column

    def grab_piece(self):
        """
        Allows for drag and drop operations. Assumes mouse button is currently held down
        """
        if self.selected_cell is not None:
            held_square = self.grid[self.selected_cell[0]][self.selected_cell[1]]
            if isinstance(held_square, pieces.Piece):
                if held_square.is_team2 == self.turn_player_2:
                    self.held_piece = held_square
                    self.piece_original_pos = (self.selected_cell[0], self.selected_cell[1])
                    self.piece_move_options = self.held_piece.move_options(self.grid, self.piece_original_pos)
                    self.grid[self.selected_cell[0]][self.selected_cell[1]] = 0

                    if isinstance(held_square, pieces.King):
                        castle_opts = held_square.check_castle(self.grid)
                        held_square.castle_opts = castle_opts
                        self.piece_move_options.extend(castle_opts[::3])


    def drop_piece(self, mousex, mousey):
        """
        If there is a piece being held, drops the piece on the square the mouse is hovering over on mouse-up
        :param mousex: int - x position of the mouse
        :param mousey: int - y position of the mouse
        """
        if self.held_piece is not None:
            mouse_row, mouse_col = self.get_square(mousex, mousey)

            if (mouse_row, mouse_col) in self.piece_move_options:
                self.grid[mouse_row][mouse_col] = self.held_piece
                self.held_piece.current_pos = (mouse_row, mouse_col)

                if self.held_piece.current_pos != self.held_piece.starting_pos:
                    self.held_piece.has_moved = True
                    self.turn_player_2 = not self.turn_player_2

                if isinstance(self.held_piece, pieces.King):
                    if (mouse_row, mouse_col) in self.held_piece.castle_opts:
                        # this needs a refactor even if it works!
                        # moves the rook to the empty space next to the now castled king
                        castle_ind = self.held_piece.castle_opts.index((mouse_row, mouse_col))
                        rook_old_pos = self.held_piece.castle_opts[castle_ind + 1]
                        rook_new_pos = self.held_piece.castle_opts[castle_ind + 2]

                        self.grid[rook_old_pos[0]][rook_old_pos[1]], self.grid[rook_new_pos[0]][rook_new_pos[1]] = \
                        self.grid[rook_new_pos[0]][rook_new_pos[1]], self.grid[rook_old_pos[0]][rook_old_pos[1]]

            else:
                self.grid[self.piece_original_pos[0]][self.piece_original_pos[1]] = self.held_piece

            self.held_piece = None
            self.selected_cell = None
            self.piece_original_pos = None

    def draw(self, screen, mousex, mousey):
        """
        Draws the board with the pieces
        :param screen: pygame.Surface - screen to draw the board to
        :param mousex: int - current mouse x position
        :param mousey: int - current mouse y position
        """
        # outline
        pygame.draw.rect(screen, self.outline, self.surface, 5)

        # checkerboard
        surfacetop, surfaceleft = self.surface.topleft
        cellsize = self.surface.width / self.units
        cell = pygame.Rect((0,0), (cellsize, cellsize))
        hover_cell = self.get_square(mousex, mousey)

        for colnum in range(self.units):
            cellposy = self.find_cell_x(colnum)
            evencol = colnum % 2 == 0

            for rownum in range(self.units):
                cellposx = self.find_cell_y(rownum)
                cell.topleft = (cellposy, cellposx)
                evenrow = rownum % 2 == 0

                if evenrow == evencol:
                    cell_color = self.even_color
                else:
                    cell_color = self.odd_color

                pygame.draw.rect(screen, cell_color, cell, 0)

                # cell mouse is hovering over
                if hover_cell is not None:
                    if rownum == hover_cell[0] and colnum == hover_cell[1]:
                        highlight_surf = pygame.Surface((cellsize, cellsize))  # ignore pycharm being dumb
                        highlight_surf.set_alpha(128)
                        highlight_surf.fill(parameters.gold_hl)
                        screen.blit(highlight_surf, cell)

                # pieces
                cell_piece = self.grid[rownum][colnum]
                if isinstance(cell_piece, pieces.Piece):
                    cell_piece.draw(screen, cell.centerx, cell.centery, cellsize)

        # selected cell
        if self.selected_cell is not None:
            sel_x = self.find_cell_x(self.selected_cell[0])
            sel_y = self.find_cell_y(self.selected_cell[1])
            sel_cell = pygame.Rect(sel_y, sel_x, cellsize, cellsize)
            pygame.draw.rect(screen, parameters.black, sel_cell, 2)

        # held piece
        if self.held_piece is not None:
            # cells piece can move to
            mouse_loc = self.get_square(mousex, mousey)
            opt_surf = pygame.Surface((cellsize, cellsize))
            opt_surf.set_alpha(128)
            opt_surf.fill(parameters.silver_hl)
            for move_option in self.piece_move_options:
                option_x = self.find_cell_x(move_option[1])
                option_y = self.find_cell_y(move_option[0])
                screen.blit(opt_surf, (option_x, option_y))

            # the piece being held
            self.held_piece.draw(screen, mousex, mousey, cellsize)
