import copy
import time
from typing import List, Optional

MAX_DEPTH = 6


def identical_elements(l: list):
    if len(set(l)) == 1:
        return l[0] if l[0] != Game.EMPTY else False
    return False


class Game:
    NO_COLUMNS = 3
    MIN_P = None
    MAX_P = None
    EMPTY = '#'

    def __init__(self, table=None):
        self.matrix = table or [Game.EMPTY] * self.NO_COLUMNS ** 2

    @classmethod
    def adverse_player(cls, player):
        return cls.MAX_P if player == cls.MIN_P else cls.MIN_P

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

    # <?> TODO find out what's going on with these
    def __str__(self):
        return self.print_str()

    def __repr__(self):
        return self.print_str()
    # </?>

    # see if there is any winning combination for either player
    # on the game matrix
    def winning_combination(self):
        return identical_elements(self.matrix[0:3])   \
            or identical_elements(self.matrix[3:6])   \
            or identical_elements(self.matrix[6:9])   \
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

    while True:
        # Human player := the minimizing player
        if current_state.current_player == Game.MIN_P:
            print(f'Now it\'s {current_state.current_player}\' turn.\n')
            valid_response = False
            while not valid_response:
                try:
                    line = int(input('Line: '))
                    column = int(input('Column: '))

                    if line in range(Game.NO_COLUMNS) and column in range(Game.NO_COLUMNS):
                        if current_state.game_matrix.matrix[line * Game.NO_COLUMNS + column] == Game.EMPTY:
                            valid_response = True
                        else:
                            print('=== :) ===')
                    else:
                        print('Line and column are integer values between 0 and 2.')
                except ValueError:
                    print('===INVALID INPUT===\n===TRY AGAIN===\n')

            current_state.game_matrix.matrix[line * Game.NO_COLUMNS + column] = Game.MIN_P
            print(f'Current state: {str(current_state)}')

            if print_if_final(current_state):
                break

            # after a valid move the current player is changed
            # with the adverse player
            current_state.current_player = Game.adverse_player(current_state.current_player)
        else:
            # current player is the computer i.e. the maximizing player
            print(f'Now it\'s {current_state.current_player}\' turn.\n')
            start_time = time.time()

            if algorithm_type == '1':
                actualised_state: GameState = min_max(current_state)
            else:
                actualised_state: GameState = alpha_beta(-500, 500, current_state)
            # The current state is replaced/actualised with the one
            # which benefits the current player the most
            # in this case, the move with the biggest estimation score
            current_state.game_matrix = actualised_state.chosen_state.game_matrix
            print(f'Current board:\n{str(current_state)}')

            end_time = time.time()
            print(f'===MOVE REALISED IN {end_time - start_time} seconds===')
            if print_if_final(current_state):
                break

            # switch the player to the adverse player
            current_state.current_player = Game.adverse_player(current_state.current_player)


if __name__ == '__main__':
    main()
