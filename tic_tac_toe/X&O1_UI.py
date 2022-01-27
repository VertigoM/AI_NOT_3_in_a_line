import copy
import sys

import pygame
import time
from typing import List, Optional

MAX_DEPTH = 6


def identical_elements(l: list):
    if len(set(l)) == 1:
        return l[0] if l[0] != Game.EMPTY else False
    return False


class Game:
    display = None
    x_img = None
    zero_img = None
    cell_grid = []
    cell_size: int
    NO_COLUMNS = 3
    MIN_P = None
    MAX_P = None
    EMPTY = '#'

    def __init__(self, table=None):
        self.matrix = table or [Game.EMPTY] * self.NO_COLUMNS ** 2

    @classmethod
    def init(cls, display, no_columns=3, cell_size=100):
        # initialize the display
        cls.display = display
        # and the cell size (in pixels)
        cls.cell_size = cell_size

        # <load and resize de images for X and O>
        cls.x_img = pygame.image.load('tic_tac_toe/x_img.png')
        cls.x_img = pygame.transform.scale(cls.x_img, (cell_size, cell_size))
        cls.zero_img = pygame.image.load('tic_tac_toe/o_img.png')
        cls.zero_img = pygame.transform.scale(cls.zero_img, (cell_size, cell_size))
        # </load and resize the images for X and O>

        # build the actual grid via a list
        for line in range(no_columns):
            for column in range(no_columns):
                cell = pygame.Rect(column * (cell_size + 1), line * (cell_size + 1), cell_size, cell_size)
                cls.cell_grid.append(cell)

    @classmethod
    def adverse_player(cls, player):
        return cls.MAX_P if player == cls.MIN_P else cls.MIN_P

    def draw_grid(self, mark=None):
        # for each index in the list of elements
        for index in range(len(self.matrix)):
            # get the line of the element
            line = index // 3
            column = index % 3

            if mark == index:
                # if the line is marked i.e. selected by the player
                # it will be marked by coloring it with red
                color = pygame.color.Color(255, 0, 0)  # RED
            else:
                color = pygame.color.Color(255, 255, 255)  # WHITE
            # draw each tile by line/index pair
            pygame.draw.rect(self.__class__.display, color, self.__class__.cell_grid[index])
            # pygame.draw.rect(canvas, color, element)
            (x, y) = (column * (self.__class__.cell_size + 1), line * (self.__class__.cell_size + 1))
            if self.matrix[index] == 'X':
                self.__class__.display.blit(self.__class__.x_img, (x, y))
            elif self.matrix[index] == 'O':
                self.__class__.display.blit(self.__class__.zero_img, (x, y))
            pygame.display.flip()
            # pygame.display.flip()   := This will update the contents of the entire display
            # pygame.display.update() := This functions is like an optimized version of pygame.flip()
            # for software displays. It allows only a portion of the screen to be updated, instead of
            # the entire area. If no argument is passed it updates the entire Surface like pygame.display.flip(_
            # pygame.display.blit()
            # TODO - research more about blit-ing
            #  @ https://www.pygame.org/docs/ref/display.html?highlight=display#module-pygame.display

    def final(self):
        result = self.winning_combination()

        if result:
            return result
        elif Game.EMPTY not in self.matrix:
            return 'DRAW'
        else:
            return False

    '''
        player
            :param the symbol of the player who moves
    '''

    def moves(self, player) -> List:
        l_moves = []
        for i in range(len(self.matrix)):
            if self.matrix[i] == Game.EMPTY:
                copy_matrix = copy.deepcopy(self.matrix)
                copy_matrix[i] = player
                l_moves.append(Game(copy_matrix))
        return l_moves

    '''
        open_line means a line which can still be used to get a win
        line
            :param row/column which is going to be checked
    '''

    def open_line(self, line, player):
        adverse_player = self.adverse_player(player)
        if adverse_player in line:
            return 0
        return line.count(player)

    def n_open_lines(self, player):
        return self.open_line(self.matrix[0:3], player) + \
               self.open_line(self.matrix[3:6], player) + \
               self.open_line(self.matrix[6:9], player) + \
               self.open_line(self.matrix[0:9:3], player) + \
               self.open_line(self.matrix[1:9:3], player) + \
               self.open_line(self.matrix[2:9:3], player) + \
               self.open_line(self.matrix[0:9:4], player) + \
               self.open_line(self.matrix[2:7:2], player)

    def estimate_score(self, depth):
        t_final = self.final()
        if t_final == self.__class__.MAX_P:
            return 99 + depth
        elif t_final == self.__class__.MIN_P:
            return -99 + depth
        elif t_final == 'DRAW':
            return 0
        else:
            return (self.n_open_lines(self.__class__.MAX_P)) - (self.n_open_lines(self.__class__.MIN_P))

    def print_str(self):
        s = f' |{" ".join([str(i) for i in range(self.NO_COLUMNS)])}\n{"-" * (self.NO_COLUMNS + 1) * 2}\n'
        for i in range(self.NO_COLUMNS):
            s += str(i) + ' |'.join(
                [str(x) for x in self.matrix[self.NO_COLUMNS * i: self.NO_COLUMNS * (i + 1)]]) + '\n'
        return s

    # override both built-in methods with custom method print_str
    def __str__(self):
        return self.print_str()

    def __repr__(self):
        return self.print_str()

    # see if there is any winning combination for either player
    # on the game matrix
    def winning_combination(self):
        return identical_elements(self.matrix[0:3]) \
               or identical_elements(self.matrix[3:6]) \
               or identical_elements(self.matrix[6:9]) \
               or identical_elements(self.matrix[0:9:3]) \
               or identical_elements(self.matrix[1:9:3]) \
               or identical_elements(self.matrix[2:9:3]) \
               or identical_elements(self.matrix[0:9:4]) \
               or identical_elements(self.matrix[2:8:2])


class GameState:
    """
        Class used by minmax and alpha-beta algorithms;
        one instance of this class represents a node from the minmax tree;
        It stores the state of the game matrix
        Its condition to be run is for the Game Class to have MIN_P & MAX_P initialized
        it also requires Game Class to implement a function called moves which
        returns a list with the possible configurations after ones turn
    """

    def __init__(self, game_matrix: Game, current_player, depth: int, parent=None, estimation=None):
        self.game_matrix = game_matrix
        self.current_player = current_player

        # the depth from the states tree
        self.depth = depth
        self.parent = parent

        # the score estimation of the 'favorability' of the current state (if it's final
        # or of the best child move for the current player
        self.estimation = estimation

        # list of possible moves
        self.possible_moves = []

        # best move for the current player chosen from the list of possible moves
        # of type GameState
        self.chosen_state: Optional[GameState] = None

    def moves(self):
        # list of possible moves generated from moves method
        # from class Game
        l_moves = self.game_matrix.moves(self.current_player)
        adverse_player = Game.adverse_player(self.current_player)

        # create a new possible game state object from each possible move
        l_state_moves = [GameState(move, adverse_player, self.depth - 1, parent=self) for move in l_moves]
        return l_state_moves

    def __str__(self):
        s = f'{str(self.game_matrix)} (Current player {self.current_player})\n'
        return s


def min_max(state: GameState) -> GameState:
    # if leaf level has been reached or a final state has been met
    if state.depth == 0 or state.game_matrix.final():
        state.estimation = state.game_matrix.estimate_score(state.depth)
        return state

    # compute all possible moves from the current state
    state.possible_moves = state.moves()

    # apply min_max algorithm on each of the possible
    # moves in order to create every possible subtree
    estimated_moves = [min_max(move) for move in state.possible_moves]

    if state.current_player == Game.MAX_P:
        # pick the state with the max estimation
        # if the current player is MAX_P i.e. the player
        # tries to maximize
        state.chosen_state = max(estimated_moves, key=lambda x: x.estimation)
    else:
        # pick the state with the min estimation
        # if the current player is MIN_P i.e. the player
        # tries to minimize
        state.chosen_state = min(estimated_moves, key=lambda x: x.estimation)

    # set the estimation for the state accordingly
    state.estimation = state.chosen_state.estimation
    return state


def alpha_beta(alpha: int, beta: int, state: GameState) -> GameState:
    # if leaf level has been reached or a final state has been met
    if state.depth == 0 or state.game_matrix.final():
        state.estimation = state.game_matrix.estimate_score(state.depth)
        return state

    # if it is in a valid interval than processing is no longer needed
    if alpha > beta:
        return state

    state.possible_moves = state.moves()

    if state.current_player == Game.MAX_P:
        current_estimation = float('-inf')

        for move in state.possible_moves:
            # compute the estimation for the new state by building the subtree
            # subtree for the new state
            new_state = alpha_beta(alpha, beta, move)

            if current_estimation < new_state.estimation:
                state.chosen_state = new_state
                current_estimation = new_state.estimation
            if alpha < new_state.estimation:
                alpha = new_state.estimation
                # invalid interval since alpha should always be less than beta
                if alpha >= beta:
                    break

    elif state.current_player == Game.MIN_P:
        current_estimation = float('inf')

        for move in state.possible_moves:
            new_state = alpha_beta(alpha, beta, move)

            if current_estimation > new_state.estimation:
                state.chosen_state = new_state
                current_estimation = new_state.estimation
            if beta > new_state.estimation:
                beta = new_state.estimation
                if alpha >= beta:
                    break

    state.estimation = state.chosen_state.estimation
    return state


def print_if_final(current_state: GameState):
    final = current_state.game_matrix.final()
    if final:
        if final == 'DRAW':
            print('DRAW')
        else:
            print(f'{final} WON!')

        return True
    return False


def main():
    valid_response = False
    line = -1
    column = -1
    algorithm_type = -1
    while not valid_response:
        algorithm_type = input('Used algorithm?\n1.Minmax\n2.Alpha-beta\n>>Input: ')
        if algorithm_type in ['1', '2']:
            valid_response = True
        else:
            print('Pick one of the given values: 1, 2')

    valid_response = False
    while not valid_response:
        choice = input('Play as:\n1.X\n2.O\n>>Input: ')
        if choice in ['1', '2']:
            valid_response = True
            Game.MIN_P = 'X' if choice == '1' else 'O'
            Game.MAX_P = 'O' if choice == '1' else 'X'
        else:
            print('Pick one of the given values: 1, 2')

    current_board = Game()
    print(f'Current board:\n{str(current_board)}')

    # create initial state
    current_state = GameState(game_matrix=current_board, current_player='X', depth=MAX_DEPTH)

    # pygame functionality initialized
    pygame.init()
    pygame.display.set_caption("tic-tac-toe")
    # two more pixels for each line
    canvas = pygame.display.set_mode(size=(302, 302))
    Game.init(canvas)

    to_move = [-1, -1]
    while True:
        if current_state.current_player == Game.MIN_P:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # get the position of the click
                    cursor_pos = pygame.mouse.get_pos()

                    for np in range(len(Game.cell_grid)):
                        if Game.cell_grid[np].collidepoint(cursor_pos):
                            # check if the click position is inside
                            # one of the cells from the cell grid
                            line = np // 3
                            column = np % 3
                        if current_state.game_matrix.matrix[np] == Game.MIN_P:
                            if to_move != [-1, -1] and line == to_move[0] and column == to_move[1]:
                                to_move = [-1, -1]
                                # draw the grid w/o the selected cell
                                current_state.game_matrix.draw_grid()
                            else:
                                to_move = [line, column]
                                # draw the grid w/ the selected cell
                                current_state.game_matrix.draw_grid(np)
                        elif current_state.game_matrix.matrix[np] == Game.EMPTY:
                            if to_move != [-1, -1]:
                                # set the cell with indices to_move to empty
                                current_state.game_matrix.matrix[to_move[0] * 3 + to_move[1]] = Game.EMPTY

                                to_move = [-1, -1]

                            # place the symbol on the game board
                            current_state.game_matrix.matrix[line * 3 + column] = Game.MIN_P
                            print(str(current_state))

                            current_state.game_matrix.draw_grid()
                            # test if the move has ended the game
                            if print_if_final(current_state):
                                break

                            # switch the player with the other
                            current_state.current_player = Game.adverse_player(current_state.current_player)
        # MAX_P player, i.e. the computer
        else:
            t_before = time.time()
            if algorithm_type == '1':
                actualised_state = min_max(current_state)
            else:
                actualised_state = alpha_beta(-500, 500, current_state)
            current_state.game_matrix = actualised_state.chosen_state.game_matrix

            current_state.game_matrix.draw_grid()
            t_after = time.time()
            print(f'=== Computing took: {t_after - t_before} ===')
            if print_if_final(current_state):
                break

            current_state.current_player = Game.adverse_player(current_state.current_player)


if __name__ == '__main__':
    main()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

