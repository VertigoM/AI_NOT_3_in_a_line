import time

import pygame
import sys
import numpy as np

WIDTH = 600
HEIGHT = 600
BOARD_ROWS = 3
BOARD_COLS = 3

LINE_WIDTH = 15

WHITE = pygame.color.Color(255, 255, 255)
RED = pygame.color.Color(255, 0, 0)
GOOGLE_BG_COLOR = pygame.color.Color(28, 170, 156)
LINE_COLOR = pygame.color.Color(23, 145, 135)

CIRCLE_RADIUS = 60
CIRCLE_WIDTH = 15
CIRCLE_COLOR = pygame.color.Color(239, 231, 200)

CROSS_WIDTH = 20
CROSS_COLOR = (66, 66, 66)
CROSS_SPACE = 40

canvas = pygame.display.set_mode((600, 600))
pygame.display.set_caption('TIC TAC TOE')


# board
game_board = np.zeros((BOARD_ROWS, BOARD_COLS))


def draw_lines(canvas, no_rows, no_columns):
    width, height = canvas.get_size()
    cell_size = width // max(no_rows, no_columns)

    # draw lines for rows
    for index in range(no_rows + 1):
        pygame.draw.line(canvas, LINE_COLOR, (0, index * cell_size), (width, cell_size * index), LINE_WIDTH)

    # draw lines for columns
    for index in range(no_columns + 1):
        pygame.draw.line(canvas, LINE_COLOR, (index * cell_size, 0), (cell_size * index, height), LINE_WIDTH)


def mark_square(row, col, player):
    print(f'[DEBUG]mark_square: {(row, col)}')
    game_board[row][col] = player


def draw_figures(screen):
    for row in range(BOARD_ROWS):
        for col in range(BOARD_COLS):
            if game_board[row][col] == 2:
                pygame.draw.circle(screen, CIRCLE_COLOR, (int(col * 200 + 200 // 2), int(row * 200 + 200 // 2)),
                                   CIRCLE_RADIUS, CIRCLE_WIDTH)
            elif game_board[row][col] == 1:
                pygame.draw.line(screen, CROSS_COLOR, (col * 200 + CROSS_SPACE, row * 200 + 200 - CROSS_SPACE),
                                 (col * 200 + 200 - CROSS_SPACE, row * 200 + CROSS_SPACE), CROSS_WIDTH)
                pygame.draw.line(screen, CROSS_COLOR, (col * 200 + CROSS_SPACE, row * 200 + CROSS_SPACE),
                                 (col * 200 + 200 - CROSS_SPACE, row * 200 + 200 - CROSS_SPACE), CROSS_WIDTH)


def available_square(row, col):
    return game_board[row][col] == 0


def check_win(player):
    # vertical win check
    for col in range(BOARD_COLS):
        if np.all(player == game_board[:, col]):
            draw_vertical_winning_line(col, player)
            return True

    # horizontal win check
    for row in range(BOARD_ROWS):
        if np.all(player == game_board[row, :]):
            draw_horizontal_winning_line(row, player)
            return True

    # ascending diagonal win check
    if game_board[0][0] == game_board[1][1] == game_board[2][2] == player:
        draw_asc_diagonal(player)
        return True

    # descending diagonal check
    if game_board[0][2] == game_board[1][1] == game_board[2][0] == player:
        return True

    return False


def draw_vertical_winning_line(col, player):
    if player == 1:
        color = CROSS_COLOR
    else:
        color = CIRCLE_COLOR
    pygame.draw.line(canvas, color, (col * 200 + 100, 50), (col * 200 + 100, 550), LINE_WIDTH)


def draw_horizontal_winning_line(row, player):
    if player == 1:
        color = CROSS_COLOR
    else:
        color = CIRCLE_COLOR
    pygame.draw.line(canvas, color, (50, row * 200 + 100), (550, row * 200 + 100), LINE_WIDTH)


def draw_asc_diagonal(player):
    pass


def draw_desc_diagonal(player):
    pass


def is_board_full():
    for row in game_board:
        for element in row:
            if element == 0:
                return False
    return True


def adverse_player(current_player):
    if current_player == 1:
        return 2
    elif current_player == 2:
        return 1


def main():
    pygame.init()

    canvas.fill(GOOGLE_BG_COLOR)
    draw_lines(canvas, BOARD_ROWS, BOARD_COLS)
    print(game_board)
    pygame.display.update()

    player = 1
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                (x, y) = map(lambda x: x // 200, event.pos)
                print(f'[DEBUG] CLICKED COORDINATES: {event.pos}')
                if available_square(*(y, x)):
                    if player == 1:
                        '''

                        '''
                        mark_square(*(y, x), 1)
                    elif player == 2:
                        mark_square(*(y, x), 2)
                else:
                    print('=== :-) ===')

                draw_figures(screen=canvas)
                # update only a Rectangle portion of the screen instead
                # of the whole screen
                pygame.display.update(pygame.Rect(x * 200, y * 200, 200, 200))
                if check_win(player):
                    pygame.display.flip()
                    time.sleep(5)
                    return
                else:
                    player = adverse_player(player)
                    print(game_board)


if __name__ == '__main__':
    main()
