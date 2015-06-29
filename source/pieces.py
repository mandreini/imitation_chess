__author__ = 'Matt'

from abc import ABCMeta, abstractmethod
import pygame
import parameters


class Piece(object):

    __metaclass__ = ABCMeta

    piece_num = 0
    name = 'default'

    def __init__(self, is_team2, starting_pos):
        corr_ind = lambda ind: parameters.units + ind if ind < 0 else ind
        corr_x = corr_ind(starting_pos[0])
        corr_y = corr_ind(starting_pos[1])
        self.starting_pos = (corr_x, corr_y)
        self.current_pos = (corr_x, corr_y)
        self.has_moved = False
        self.is_team2 = is_team2

        if is_team2:
            self.piece_color = parameters.black
        else:
            self.piece_color = parameters.white

        self.piece_img = self._load_image()
        self.castle_opts = []  # for the king to castle, but also as safety

    def _load_image(self):
        """
        load the image associated with the piece given
        :return:
          piece_img: pygame.Surface - image to draw
        """

        teamcolor = 'black' if self.is_team2 else 'white'
        piece_name = self.name
        if piece_name == 'default': teamcolor = 'none'

        # load and return the image
        loc = "../images/%s-%s.png" % (piece_name, teamcolor)
        piece_img = pygame.image.load(loc)
        return piece_img

    def draw(self, screen, xloc, yloc, cell_size):
        """
        Draws the piece to the given screen at the given x and y coordinates
        Currently draws the piece_num
        :param screen: pygame.Surface - screen to draw the piece to
        :param xloc: int - x location for the center
        :param yloc: int - y location for the center
        :param cell_size: int - size of the cell
        """
        piece_img = self.piece_img
        piece_img = pygame.transform.scale(piece_img, (cell_size*8/10, cell_size*8/10))
        piece_rect = piece_img.get_rect()
        piece_rect.center = (xloc, yloc)

        screen.blit(piece_img, piece_rect)

    def move_options(self, grid, position):
        """
        The function to determine where the piece is allowed to move given the piece type and current board layout
        :param grid: list - 2-D table of the current board layout from board.Board.grid
        :param position: tuple - current position of the piece in (y, x)
        :return:
        """
        moves, takeoffs, continuous = self.movement()
        options = [position]  # current position of the piece (being held)
        determining_continuous = True

        if moves is not None:
            multiplier = 1  # used to extend continuous=True pieces to more than 1 cell movement
            finished_directions = []  # used to mark which directions have reached an end

            while determining_continuous:
                opts_to_add = []

                for movenum, move in enumerate(moves):
                    if movenum not in finished_directions:
                        new_opt = (position[0] + multiplier*move[0], position[1] + multiplier*move[1],)

                        in_y = 0 <= new_opt[0] < parameters.units
                        in_x = 0 <= new_opt[1] < parameters.units
                        if in_y and in_x:
                            populant = grid[new_opt[0]][new_opt[1]]

                            if populant == 0:
                                opts_to_add.append(new_opt)

                            else:
                                if populant.is_team2 != self.is_team2:
                                    opts_to_add.append(new_opt)

                                finished_directions.append(movenum)

                determining_continuous = continuous
                if determining_continuous:
                    multiplier += 1

                if len(finished_directions) < len(moves):
                    options.extend(opts_to_add)
                else:
                    determining_continuous = False

                # fallback to avoid infinite loop JIC
                if multiplier > 8: break

        # Determine if a takeoff move is possible
        if takeoffs is not None:
            for takeoff in takeoffs:
                new_opt = (position[0] + takeoff[0], position[1] + takeoff[1],)

                in_y = 0 <= new_opt[0] < parameters.units
                in_x = 0 <= new_opt[1] < parameters.units
                if in_y and in_x:
                    populant = grid[new_opt[0]][new_opt[1]]

                    if isinstance(populant, Piece):
                        if populant.is_team2 != self.is_team2:
                            options.append(new_opt)

        return options

    @abstractmethod
    def movement(self):
        """
        Method to control the movement of the pieces
        :return:
          continuous: bool - move continuously along specified direction or only 1 step
          moves: tuple - direction(s) the piece can move along
          takeoffs: tuple - direction(s) the piece can move only if to take off another piece
        """
        return None, None, None

class Pawn(Piece):
    """The pawn piece"""
    piece_num = 1
    name = 'pawn'

    def movement(self):
        if self.is_team2:
            moves = [[1, 0], [2, 0]]
            takeoffs = ([1, -1], [1, 1])
        else:
            moves = [[-1, 0], [-2, 0]]
            takeoffs = ([-1, -1], [-1, 1])
        # moves[1] corresponds to the 'pawn can move 2 steps if from starting position'

        if self.has_moved:
            # removes the 'pawn can move 2 steps if from starting position'
            moves.pop(1)

        moves = tuple(moves)
        continuous = False

        return moves, takeoffs, continuous

class Rook(Piece):
    """The rook piece"""
    piece_num = 2
    name = 'rook'

    def movement(self):
        moves = ([1, 0], [0, 1], [-1, 0], [0, -1])
        takeoffs = None
        continuous = True

        return moves, takeoffs, continuous

class Knight(Piece):
    """The knight piece"""
    piece_num = 3
    name = 'knight'

    def movement(self):
        moveset1 = ([1, 2], [-1, 2], [-1, -2], [1, -2])
        moveset2 = tuple([ms[::-1] for ms in moveset1])
        moves = moveset1 + moveset2
        takeoffs = None
        continuous = False

        return moves, takeoffs, continuous

class Bishop(Piece):
    """The bishop piece"""
    piece_num = 4
    name = 'bishop'

    def movement(self):
        moves = ([1, 1], [1, -1], [-1, -1], [-1, 1])
        takeoffs = None
        continuous = True

        return moves, takeoffs, continuous

class Queen(Piece):
    """The queen piece"""
    piece_num = 5
    name = 'queen'

    def movement(self):
        moveset1 = ([1, 0], [-1, 0], [1, -1])
        moveset2 = tuple([ms[::-1] for ms in moveset1])
        moves = moveset1 + moveset2 + ([1, 1], [-1, -1])
        takeoffs = None
        continuous = True

        return moves, takeoffs, continuous

class King(Piece):
    """The king piece"""
    piece_num = 6
    name = 'king'

    def movement(self):
        moveset1 = ([1, 0], [-1, 0], [1, -1])
        moveset2 = tuple([ms[::-1] for ms in moveset1])
        moves = moveset1 + moveset2 + ([1, 1], [-1, -1])
        takeoffs = None
        continuous = False

        return moves, takeoffs, continuous

    def check_castle(self, grid):
        """
        This is used to check if a castle move is possible
        Requirements: both king and rook to castle with must not have moved (has_moved = False)
        Empty spaced in between king and rook in question
        :param grid: list - 2-D table of the gameboard
        :return:
        """
        if self.has_moved: return []

        row = self.starting_pos[1]
        y_pos = grid[row]
        left = right = False

        # left rook (index 0)
        rook = y_pos[0] if y_pos[0].name == 'rook' else None
        if rook is not None:
            if grid[row][1] == grid[row][2] == 0:
                left = True

        # right rook (index -1)
        rook = grid[row][-1] if grid[row][-1].name == 'rook' else None
        if rook is not None:
            if y_pos[4] == y_pos[5] == y_pos[6] == 0:
                right = True

        castle_opts = []
        # (king_pos, rook_old, rook_new)
        if left:
            castle_opts.extend(((row, 1), (row, 0), (row, 2)))
        if right:
            castle_opts.extend(((row, 6), (row, 7), (row, 5)))

        return castle_opts
