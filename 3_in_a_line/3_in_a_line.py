import copy
import sys
import time
from typing import Optional

import pygame
import numpy as np


class GameBoard:
    # difficulty
    # max level of min_max/alpha_beta search_tree
    MAX_DEPTH = -1

    # display properties
    WIDTH = -1
    HEIGHT = -1
    BOARD_ROWS = -1
    BOARD_COLS = -1

    # cell dimension
    CELL_SIZE = 80

    # canvas
    CANVAS = None

    # colors for the canvas
    GOOGLE_BG_COLOR = pygame.color.Color(28, 170, 156)
    LINE_COLOR = pygame.color.Color(23, 145, 135)

    # line properties
    LINE_WIDTH = 10

    # properties for symbols
    # to be initialised depending of the number
    # of rows and columns
    CIRCLE_RADIUS = 30
    CIRCLE_WIDTH = 10
    CIRCLE_COLOR = pygame.color.Color(239, 231, 200)

    CROSS_WIDTH = 15
    CROSS_SPACE = 15
    CROSS_COLOR = pygame.color.Color(66, 66, 66)

    # player details
    MIN_P = None
    MAX_P = None
    LAST_MOVE = (-1, -1)

    # game turn
    TURN = 0

    def __init__(self, matrix=None):
        """
        :param matrix: existing game_matrix
        """
        if matrix is None:
            self.matrix = np.zeros((self.BOARD_ROWS, self.BOARD_COLS))
        else:
            self.matrix = matrix

    def available_square(self, row, col, player):
        print(GameBoard.TURN)
        if self.__class__.TURN > 1:
            return self.matrix[row, col] == 0 and (row, col) in self.available_moves(player)
        else:
            return True

    def mark_square(self, row, col, player):
        self.matrix[row, col] = player

    @classmethod
    def init(cls):
        cls.MAX_P = 1
        cls.MIN_P = 2

        pygame.init()
        cls.WIDTH = cls.CELL_SIZE * cls.BOARD_COLS
        cls.HEIGHT = cls.CELL_SIZE * cls.BOARD_ROWS

        # set the display resolutions depending on the (x, y) dimensions
        cls.CANVAS = pygame.display.set_mode((cls.WIDTH, cls.HEIGHT))

        # fill the canvas with color and draw the lines
        cls.CANVAS.fill(cls.GOOGLE_BG_COLOR)
        cls.draw_lines()

        pygame.display.set_caption('NOT 3 in a line!')

    @classmethod
    def draw_lines(cls):
        # draw lines for rows i.e. horizontal lines
        for index in range(cls.BOARD_ROWS + 1):
            pygame.draw.line(cls.CANVAS, cls.LINE_COLOR,
                             (0, index * cls.CELL_SIZE), (cls.WIDTH, index * cls.CELL_SIZE), cls.LINE_WIDTH)

        # draw lines for cols i.e. vertical lines
        for index in range(cls.BOARD_COLS + 1):
            pygame.draw.line(cls.CANVAS, cls.LINE_COLOR,
                             (index * cls.CELL_SIZE, 0), (index * cls.CELL_SIZE, cls.HEIGHT), cls.LINE_WIDTH)

    def draw_figure(self):
        for row in range(self.__class__.BOARD_ROWS):
            for col in range(self.__class__.BOARD_COLS):
                (x, y) = (col * self.__class__.CELL_SIZE, row * self.__class__.CELL_SIZE)
                if self.matrix[row, col] == 1:
                    pygame.draw.line(self.__class__.CANVAS, self.__class__.CROSS_COLOR,
                                     (x + self.__class__.CROSS_SPACE, y + self.__class__.CROSS_SPACE),
                                     (x + self.__class__.CELL_SIZE - self.__class__.CROSS_SPACE,
                                      y + self.__class__.CELL_SIZE - self.__class__.CROSS_SPACE),
                                     self.CROSS_WIDTH)
                    pygame.draw.line(self.__class__.CANVAS, self.__class__.CROSS_COLOR,
                                     (x + self.__class__.CELL_SIZE - self.__class__.CROSS_SPACE,
                                      y + self.__class__.CROSS_SPACE), (x + self.__class__.CROSS_SPACE,
                                                                        y + self.__class__.CELL_SIZE - self.__class__.CROSS_SPACE),
                                     self.__class__.CROSS_WIDTH)
                elif self.matrix[row, col] == 2:
                    pygame.draw.circle(self.__class__.CANVAS, self.__class__.CIRCLE_COLOR,
                                       (x + self.__class__.CELL_SIZE // 2, y + self.__class__.CELL_SIZE // 2),
                                       self.__class__.CIRCLE_RADIUS,
                                       self.__class__.CIRCLE_WIDTH)

    @classmethod
    def adverse_player(cls, current_player):
        return cls.MIN_P if current_player == cls.MAX_P else cls.MAX_P

    def is_board_full(self):
        for row in self.matrix:
            if 0 in row:
                return False
        return True

    def available_moves(self, player):
        """
        :param player: player for whom available moves are computed
        :return: set containing all positions which can be marked by the current player
        """
        l_moves = set()
        for row in range(self.BOARD_ROWS):
            for col in range(self.BOARD_COLS):
                if self.matrix[row, col] == player:
                    # check if generated neighbors are inside the grid
                    l_moves.update([(x, y) for (x, y) in neighbors(row, col) if
                                    0 <= x < GameBoard.BOARD_ROWS and 0 <= y < GameBoard.BOARD_COLS and self.matrix[
                                        x, y] == 0])
        # if l_moves is empty it means that the current player has never
        # placed a symbol on a square, thus all squares are available for him
        if not l_moves:
            for row in range(self.BOARD_ROWS):
                for col in range(self.BOARD_COLS):
                    if not self.matrix[row, col]:
                        l_moves.add((row, col))
        print(f'[DEBUG] Current board:\n{self.matrix}')
        print(f'[DEBUG] Possible moves:\n{l_moves} // len: {len(l_moves)} for player: {player}')
        return l_moves

    def boards_from_available_moves(self, player) -> dict:
        """
        :param player: player for whom all possible game boards are computed
        :return: list of all different boards which can be obtained
        """
        boards = {}
        for (x, y) in self.available_moves(player):
            board_copy = copy.deepcopy(self.matrix)
            """
            try:
                board_copy[x, y] = player
            except IndexError as e:
                print(f'[DEBUG] exception message: {str(e)}')
                print(f'[DEBUG] indexes: {(x, y)}')
                print(f'[DEBUG] matrix:\n{board_copy}')
                sys.exit(-1)
            """
            board_copy[x, y] = player
            boards[(x, y)] = GameBoard(board_copy)
        return boards

    def check_loss_condition(self, row: int, col: int) -> bool:
        """
        :param row:
        :param col:
        (x, y) pair - coordinates of the current placed element
        :return: if the current move caused a loss or not
        """

        # placed element
        el = self.matrix[row, col]

        vertical = 1
        horizontal = 1
        first_diag = 1
        second_diag = 1

        # check vertical
        # check upward
        try:
            x = row - 1
            while self.matrix[x, col] == el:
                vertical += 1
                if vertical >= 3:
                    return True
                x -= 1
        except IndexError:
            pass

        # check downward
        try:
            x = row + 1
            while self.matrix[x, col] == el:
                vertical += 1
                if vertical >= 3:
                    return True
                x += 1
        except IndexError:
            pass

        if vertical >= 3:
            return True

        # check horizontal
        # check left
        try:
            y = col - 1
            while self.matrix[row, y] == el:
                horizontal += 1
                if horizontal >= 3:
                    return True
                y -= 1
        except IndexError:
            pass

        # check right
        try:
            y = col + 1
            while self.matrix[row, y] == el:
                horizontal += 1
                if horizontal >= 3:
                    return True
                y += 1
        except IndexError:
            pass

        if horizontal >= 3:
            return True

        # check first diagonal
        # check descending
        try:
            x = row + 1
            y = col + 1
            while self.matrix[x, y] == el:
                first_diag += 1
                if first_diag >= 3:
                    return True
                x += 1
                y += 1
        except IndexError:
            pass

        # check ascending
        try:
            x = row - 1
            y = col - 1
            while self.matrix[x, y] == el:
                first_diag += 1
                if first_diag >= 3:
                    return True
                x -= 1
                y -= 1
        except IndexError:
            pass

        if first_diag >= 3:
            return True

        # check second diagonal
        # check descending
        try:
            x = row + 1
            y = col - 1
            while self.matrix[x, y] == el:
                second_diag += 1
                if second_diag >= 3:
                    return True
                x += 1
                y -= 1
        except IndexError:
            pass

        try:
            x = row - 1
            y = col + 1
            while self.matrix[x, y] == el:
                second_diag += 1
                if second_diag >= 3:
                    return True
                x -= 1
                y += 1
        except IndexError:
            pass

        if second_diag >= 3:
            return True

        return False

    def estimate_score(self, depth):
        t_final = self.final()
        if t_final == self.__class__.MAX_P:
            return 99 + depth
        elif t_final == self.__class__.MIN_P:
            return -99 + depth
        elif t_final == 'DRAW':
            return 0
        else:
            return 1

    def final(self):
        empty_board = True
        for row in range(GameBoard.BOARD_ROWS):
            for col in range(GameBoard.BOARD_COLS):
                # if square has been claimed by one of the players
                # check if it is part of a losing combination
                if not self.matrix[row, col]:
                    empty_board = True
                    continue
                return self.check_loss_condition(row, col)
        return 'DRAW' if empty_board else False


def neighbors(x, y):
    return [(x, y + 1),  # (0, +1)
            (x - 1, y + 1),  # (-1, +1)
            (x - 1, y),  # (-1, 0)
            (x - 1, y - 1),  # (-1, -1)
            (x, y - 1),  # (0, -1)
            (x + 1, y - 1),  # (+1, -1)
            (x + 1, y),  # (+1, 0)
            (x + 1, y + 1)]  # (+1, +1)


class GameState:
    """
        Class used by minimax and alpha-beta algorithms;
        one instance of this class represents a node from the minmax/alpha-beta tree;
        It stores the state of the game matrix
        Its condition to be run is for the Game Class to have MIN_P & MAX_P initialized
        it also requires Game Class to implement a function which returns a list
        # of all the possible configurations after ones turn

        Note to self - available_squares returns a list of tuples which contains
        all the possible moves of the current player
    """

    def __init__(self, game_board: GameBoard, current_player: int, depth: int, parent=None, estimation=None):
        self.game_board = game_board
        self.current_player = current_player

        # the height of the current subtree
        self.depth = depth

        # parent node: GameState
        self.parent = parent

        # the score estimation of the 'favorability' of the current state
        # if it's a final state i.e. one of the players lost or the best child move for the current player
        self.estimation = estimation

        # list of possible moves from the current state
        self.possible_moves: dict

        self.chosen_state: Optional[GameState] = None

    def moves(self):
        # dict of possible moves and corresponding game board
        d_moves = self.game_board.boards_from_available_moves(self.current_player)
        adverse_player = GameBoard.adverse_player(self.current_player)

        # create a new possible game state object from each possible move
        # d_state_moves = [GameState(move, adverse_player, self.depth - 1, self) for move in d_moves]
        d_state_moves = {key: GameState(value, adverse_player, self.depth - 1, self) for key, value in d_moves.items()}
        return d_state_moves


def min_max(game_state: GameState) -> GameState:
    """
    :param game_state: parent GameState from which child nodes are derived
    :return: GameState with the most favorable game_board i.e. with the best move
    for the current player
    """
    # if leaf level has been reached or a final state has been met

    if game_state.depth == 0 or game_state.game_board.final():
        # TODO - complete function
        # TODO - create GameState::GameMatrix::estimate_score function
        game_state.estimation = game_state.game_board.estimate_score(game_state.depth)
        return game_state

    # compute all possible moves from the current state
    # dictionary: key: (x, y): coordinates of the last move
    #             value: GameState: build from modified game_board
    game_state.possible_moves = game_state.moves()

    # apply min_max algorithm on each of the possible
    # moves in order to create every possible subtree
    estimated_moves = [min_max(move) for move in game_state.possible_moves.values()]

    if game_state.current_player == GameBoard.MAX_P:
        # pick the state with the max estimation
        # if the current player is MIN_P i.e. the player most of the times
        # -- tries to maximize the outcome
        game_state.chosen_state = max(estimated_moves, key=lambda x: x.estimation)
    else:
        # pick the state with the min estimation
        # if the current player is MIN_P i.e. the player
        # -- tries to minimize
        game_state.chosen_state = min(estimated_moves, key=lambda x: x.estimation)

    game_state.estimation = game_state.chosen_state.estimation
    return game_state


def main():
    # x = int(input('NO ROWS: '))
    # y = int(input('NO COLS: '))

    # TODO #1
    # take the number of rows / cols as user input instead of hardcode-ing them

    # TODO #2
    # take the player symbols as user input instead of hardcode-ing them

    # TODO #3
    # persist possible moves in memory in order not to generate them each time
    # and only remove used positions / add newly generated positions

    # TODO #4
    # refactor functions from check_loss_condition in order to not repeat code

    # TODO #5
    # take GameBoard.MAX_DEPTH as difficulty setting

    # TODO #6
    # generated neighbors from GameBoard::neighbors need to be checked to be inside
    # GameBoard.NO_COLS & GameBoard.NO_ROWS

    # TODO #7
    # create a menu for inputting all data & select game difficulty

    GameBoard.BOARD_ROWS = 6
    GameBoard.BOARD_COLS = 4

    # initialize the game board
    game_board = GameBoard()

    GameBoard.init()
    game_board.draw_figure()
    pygame.display.flip()

    GameBoard.MIN_P = 1
    GameBoard.MAX_P = 2

    GameBoard.MAX_DEPTH = 6

    current_state = GameState(game_board=game_board, current_player=game_board.MIN_P, depth=GameBoard.MAX_DEPTH)

    while True:
        if pygame.display.get_init():
            if current_state.current_player == GameBoard.MIN_P:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit(0)
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        (x, y) = map(lambda pos: pos // GameBoard.CELL_SIZE, event.pos)
                        # don't end turn until a valid move is not made
                        if current_state.game_board.available_square(*(y, x), current_state.current_player):
                            current_state.game_board.mark_square(*(y, x), current_state.current_player)
                        else:
                            # game_board square not available
                            print('=== :-) ===')
                            # don't continue running the code and listen
                            # to the next event
                            continue

                        # the move was valid
                        GameBoard.LAST_MOVE = (y, x)

                        current_state.game_board.draw_figure()
                        pygame.display.update(
                            pygame.Rect(x * GameBoard.CELL_SIZE, y * GameBoard.CELL_SIZE, GameBoard.CELL_SIZE,
                                        GameBoard.CELL_SIZE))

                        current_state.current_player = GameBoard.adverse_player(current_state.current_player)

                        GameBoard.TURN += 1
            # other players turn i.e. computer's turn
            elif current_state.current_player == GameBoard.MAX_P:
                t_before = time.time()
                actualised_state = min_max(current_state)

                '''
                    current_state.game_board = actualised_state.chosen_state.game_board
                    AttributeError: 'NoneType' has no attribute 'game_board'
                '''
                current_state.game_board = actualised_state.chosen_state.game_board
                current_state.game_board.draw_figure()
                pygame.display.flip()
                # pygame.display.update()
                print(current_state.game_board.matrix)
                t_after = time.time()
                print(f'=== Computing took: {t_after - t_before} ===')

                if current_state.game_board.final():
                    print(f'PLAYER LOST: {current_state.current_player}')

                # TODO - check if win
                current_state.current_player = GameBoard.adverse_player(current_state.current_player)

                GameBoard.TURN += 1

            # check if board is full and stop game
            if current_state.game_board.is_board_full():
                print('=== BOARD FULL ===')
                GameBoard.CANVAS.fill(GameBoard.GOOGLE_BG_COLOR)
                pygame.display.flip()
                time.sleep(3)
                pygame.quit()
                sys.exit(0)


if __name__ == '__main__':
    main()
