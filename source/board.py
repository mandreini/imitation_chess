__author__ = 'Matt'

import copy

import pygame

import parameters
import pieces

class Board(object):
    def __init__(self, width, height, theme='default'):
        self.theme = theme
        self.units = parameters.units
        self.surface = pygame.Rect((0,0), (width, height))
        self.surface.center = (parameters.xmax/2, parameters.ymax/2)
        self.find_cell_x = lambda pos: self.surface.left + pos * width / self.units
        self.find_cell_y = lambda pos: self.surface.top + pos * height / self.units
        self.background_color, self.outline, self.odd_color, self.even_color = self._determine_theme_colors()

        self.can_undo_txt = parameters.undo_font.render('Undo', 1, parameters.red)
        self.disabled_undo_txt = parameters.undo_font.render('Undo', 1, parameters.black)
        self.undo_rect = self.can_undo_txt.get_rect()
        self.undo_rect.bottomright = (parameters.xmax, parameters.ymax)

        row = [0] * self.units
        grid = [row[:] for j in range(self.units)]
        self.grid = self._setup_grid(grid)

        self.past_moves = []

        self.turn_player_2 = False
        self.can_undo = False
        self.pawn_at_end = False

        self.selected_cell = None
        self.held_piece = None
        self.piece_original_pos = None
        self.piece_move_options = None
        self.winner = None
        self.pawn_to_upgrade = None
        self.upgrade_pawn_team_2 = None
        self.dead_piece = None

    def _determine_theme_colors(self):
        """
        Determines the colors corresponding to the theme chosen (currently only supports color changes)
        :return:
        """
        # { key: [background, outline, odd_color, even_color], ... }
        theme_parameters = {
            'default': [parameters.white, parameters.black, parameters.blue, parameters.dark_blue],
            'simplistic': [parameters.white, parameters.black, parameters.silver_hl, parameters.grey],
            'flipped': [parameters.white, parameters.black, parameters.blue, parameters.dark_blue],
            'vibrant': [parameters.silver_hl, parameters.gold_hl, parameters.brown, parameters.dark_green],
            'movement': [parameters.white, parameters.black, parameters.black, parameters.grey],
        }

        if theme_parameters.has_key(self.theme):
            curr_theme = theme_parameters[self.theme]
        else:
            curr_theme = theme_parameters['default']

        return curr_theme

    def _setup_grid(self, grid):
        """
        This will initialize the chessboard in memory. Currently only supports the traditional start
        :param grid: 8x8 list of 0's
        :return: 8x8 grid populated with pieces (and 0's)
        """

        # 2 rows of pawns
        for i in range(self.units):
            grid[1][i] = pieces.Pawn(True, (1, i), self.theme)
            grid[-2][i] = pieces.Pawn(False, (-2, i), self.theme)

        for team in range(-1, 1, 1):  # iterates -1 and 0

            side = grid[team]
            team_2 = not bool(team)

            # rooks
            side[0] = pieces.Rook(team_2, (team, 0), self.theme)
            side[-1] = pieces.Rook(team_2, (team, -1), self.theme)

            # knights
            side[1] = pieces.Knight(team_2, (team, 1), self.theme)
            side[-2] = pieces.Knight(team_2, (team, -2), self.theme)

            # bishops
            side[2] = pieces.Bishop(team_2, (team, 2), self.theme)
            side[-3] = pieces.Bishop(team_2, (team, -3), self.theme)

            # queen
            side[3] = pieces.Queen(team_2, (team, 3), self.theme)

            # king
            side[4] = pieces.King(team_2, (team, 4), self.theme)

        return grid

    def refresh_theme(self, new_theme):
        """
        This will change the layout of the board without needing to call __init__
        :param new_theme: str - new theme
        :return:
        """
        self.theme = new_theme
        self.background_color, self.outline, self.odd_color, self.even_color = self._determine_theme_colors()

        for row in range(len(self.grid)):
            for col in range(row):
                if isinstance(self.grid[row][col], pieces.Piece):
                    self.grid[row][col].refresh_theme(new_theme)

    def do_event(self, event, mousex, mousey, heaven):
        """
        This will process the event when the gameboard is active
        :param event: pygame.Event object to process
        :return:
        """
        if self.winner is None:
            if event.type == pygame.MOUSEBUTTONDOWN:
                new_sel_cell = self.get_square(mousex, mousey)
                self.selected_cell = new_sel_cell if self.selected_cell != new_sel_cell else None
                self.grab_piece()

                if self.undo_rect.collidepoint((mousex, mousey)) and self.can_undo:
                    self.undo()

            if event.type == pygame.MOUSEBUTTONUP:
                self.drop_piece(mousex, mousey, heaven)

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

    def drop_piece(self, mousex, mousey, graveyard):
        """
        If there is a piece being held, drops the piece on the square the mouse is hovering over on mouse-up
        :param mousex: int - x position of the mouse
        :param mousey: int - y position of the mouse
        """
        if self.held_piece is not None:
            mouse_pos = self.get_square(mousex, mousey)

            # occasionally does not let players place certain pieces in certain areas..?
            if (mouse_pos is not None and mouse_pos in self.piece_move_options
                and mouse_pos != self.held_piece.current_pos):
                self.turn_player_2 = not self.turn_player_2

                mouse_row, mouse_col = mouse_pos
                new_grid_pos = self.grid[mouse_row][mouse_col]

                if isinstance(new_grid_pos, pieces.Piece):
                    # graveyard.add_piece(self.grid[mouse_row][mouse_col].piece_num)
                    graveyard.set_dead_piece(new_grid_pos.name, (mousex, mousey))

                # store move for undo
                old_pos = self.piece_original_pos
                old_piece = self.held_piece
                new_pos = mouse_pos
                new_piece = copy.deepcopy(new_grid_pos)
                has_moved = self.held_piece.has_moved
                self.past_moves.append((old_pos, old_piece, new_pos, new_piece, has_moved))

                if isinstance(new_grid_pos, pieces.King):
                    self.winner = self.held_piece.is_team2

                self.grid[mouse_row][mouse_col] = self.held_piece
                self.held_piece.current_pos = (mouse_row, mouse_col)

                if self.held_piece.current_pos != self.held_piece.starting_pos:
                    self.held_piece.has_moved = True

                if isinstance(self.held_piece, pieces.King):
                    if (mouse_row, mouse_col) in self.held_piece.castle_opts:
                        # this needs a refactor even if it works!
                        # moves the rook to the empty space next to the now castled king
                        castle_ind = self.held_piece.castle_opts.index((mouse_row, mouse_col))
                        rook_old_pos = self.held_piece.castle_opts[castle_ind + 1]
                        rook_new_pos = self.held_piece.castle_opts[castle_ind + 2]

                        self.grid[rook_old_pos[0]][rook_old_pos[1]], self.grid[rook_new_pos[0]][rook_new_pos[1]] = \
                        self.grid[rook_new_pos[0]][rook_new_pos[1]], self.grid[rook_old_pos[0]][rook_old_pos[1]]

                if isinstance(self.held_piece, pieces.Pawn):
                    if self.held_piece.current_pos[0] == 0 or self.held_piece.current_pos[0] == 7:
                        self.pawn_at_end = True
                        self.pawn_to_upgrade = self.held_piece.current_pos

                self.can_undo = True

            else:
                self.grid[self.piece_original_pos[0]][self.piece_original_pos[1]] = self.held_piece

            self.held_piece = None
            self.selected_cell = None
            self.piece_original_pos = None

    def pawn_upgrade(self, position, is_team2, choice=3):
        """
        This will change a pawn into the choice piece when said pawn has reached the end of the board
        :param choice: pieces.Piece object to change the pawn into
        """

        piece_opts = [pieces.Rook, pieces.Knight, pieces.Bishop, pieces.Queen]
        choice_piece = piece_opts[choice]

        self.grid[position[0]][position[1]] = choice_piece(is_team2, self.pawn_to_upgrade, self.theme)
        self.grid[position[0]][position[1]].has_moved = True
        self.past_moves.append(['pawn_upgrade', self.pawn_to_upgrade])

        self.pawn_to_upgrade = None
        self.pawn_at_end = False

    def undo(self):
        """ Undoes the last move """
        last_move = self.past_moves[-1]
        self.past_moves.pop(-1)

        if last_move[0] == 'pawn_upgrade':
            self.downgrade_pawn(last_move[1])
            last_move = self.past_moves[-1]
            self.past_moves.pop(-1)

        old_pos, old_piece, new_pos, new_piece, has_moved = last_move
        self.grid[old_pos[0]][old_pos[1]] = old_piece
        self.grid[new_pos[0]][new_pos[1]] = new_piece

        old_piece.has_moved = has_moved

        self.turn_player_2 = not self.turn_player_2

        self.can_undo = len(self.past_moves) > 0

    def downgrade_pawn(self, position):
        """
        This will revert the upgraded pawn back into a pawn
        :param position: tuple - grid location of the piece to revert to a pawn
        """
        grid_pos = self.grid[position[0]][position[1]]
        grid_pos = pieces.Pawn(is_team2=self.turn_player_2, starting_pos=position, theme=self.theme)
        grid_pos.has_moved = True

    def draw(self, screen, mousex, mousey):
        """
        Draws the board with the pieces
        :param screen: pygame.Surface - screen to draw the board to
        :param mousex: int - current mouse x position
        :param mousey: int - current mouse y position
        """
        # outline
        screen.fill(self.background_color)
        pygame.draw.rect(screen, self.outline, self.surface, 5)

        # checkerboard
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

        # undo button
        undo_txt = self.can_undo_txt if self.can_undo else self.disabled_undo_txt
        screen.blit(undo_txt, self.undo_rect)

        # win condition
        if self.winner is not None:
            win_player = "2" if self.winner else "1"
            win_txt = parameters.win_font.render("player %s has won!" % win_player, 1, parameters.green)
            win_rect = win_txt.get_rect()
            win_rect.center = (parameters.xmax/2, parameters.ymax/2)
            screen.blit(win_txt, win_rect)
