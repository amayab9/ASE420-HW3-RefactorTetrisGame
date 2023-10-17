import pygame
import random


class TetrisPiece:
    COLORS = [
        (0, 0, 0),
        (120, 37, 179),
        (100, 179, 179),
        (80, 34, 22),
        (80, 134, 22),
        (180, 34, 22),
        (180, 34, 122),
    ]

    FIGURES = (
        ([1, 5, 9, 13], [4, 5, 6, 7]),
        ([4, 5, 9, 10], [2, 6, 5, 9]),
        ([6, 7, 9, 10], [1, 5, 6, 10]),
        ([1, 2, 5, 9], [0, 4, 5, 6], [1, 5, 9, 8], [4, 5, 6, 10]),
        ([1, 2, 6, 10], [5, 6, 7, 9], [2, 6, 10, 11], [3, 5, 6, 7]),
        ([1, 4, 5, 6], [1, 4, 5, 9], [4, 5, 6, 9], [1, 5, 6, 9]),
    )

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.color = random.randint(1, len(self.COLORS) - 1)
        self.type = random.randint(0, len(self.FIGURES) - 1)
        self.rotation = 0
        self.x = width // 2
        self.y = 0

    def rotate(self):
        self.rotation = (self.rotation + 1) % len(self.FIGURES[self.type])

    def move_left(self):
        self.x -= 1

    def move_right(self):
        self.x += 1

    def move_down(self):
        self.y += 1

    def get_current_shape(self):
        return self.FIGURES[self.type][self.rotation]

    def get_color(self):
        return self.COLORS[self.color]

    def get_position(self):
        return self.x, self.y


class GameBoard:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.field = [[0] * self.width for _ in range(self.height)]

    def clear(self):
        self.field = [[0] * self.width for _ in range(self.height)]

    def draw(self, screen, block_size, draw_x, draw_y, colors):
        for i in range(self.height):
            for j in range(self.width):
                pygame.draw.rect(
                    screen,
                    (128, 128, 128),
                    [draw_x + block_size * j, draw_y + block_size * i, block_size, block_size],
                    1,
                )
                if self.field[i][j] > 0:
                    pygame.draw.rect(
                        screen,
                        colors[self.field[i][j]],
                        [draw_x + block_size * j + 1, draw_y + block_size * i + 1, block_size - 2, block_size - 1],
                    )

    def intersects(self, piece, piece_x, piece_y):
        for y in range(piece.PIECE_DIMENSION):
            for x in range(piece.PIECE_DIMENSION):
                if piece.get_current_shape()[y * piece.PIECE_DIMENSION + x] > 0:
                    board_x = piece_x + x
                    board_y = piece_y + y
                    if (
                            board_x < 0
                            or board_x >= self.width
                            or board_y >= self.height
                            or (board_y >= 0 and self.field[board_y][board_x] > 0)
                    ):
                        return True
        return False

    def freeze(self, piece, piece_x, piece_y):
        for y in range(piece.PIECE_DIMENSION):
            for x in range(piece.PIECE_DIMENSION):
                if piece.get_current_shape()[y * piece.PIECE_DIMENSION + x] > 0:
                    board_x = piece_x + x
                    board_y = piece_y + y
                    if board_y >= 0:
                        self.field[board_y][board_x] = piece.color


class TetrisGame:
    PIECE_DIMENSION = 4
    BLOCK_SIZE = 20
    BLOCK_BORDER = 1

    DRAW_X_OFFSET = 100
    DRAW_Y_OFFSET = 60

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((400, 500))
        pygame.display.set_caption("Tetris")
        self.clock = pygame.time.Clock()

        self.FPS = 60
        self.counter = 0
        self.pressing_down = False

        self.initialize_board(20, 10)
        self.current_piece = TetrisPiece(self.Width, self.Height)
        self.board = GameBoard(self.Width, self.Height)
        self.done = False
        self.level = 1

    def initialize_board(self, height, width):
        self.Height = height
        self.Width = width
        self.Field = [[0] * self.Width for _ in range(self.Height)]
        self.State = "start"

    def intersects(self, piece):
        PIECE_DIMENSION = 4
        for y in range(PIECE_DIMENSION):
            for x in range(PIECE_DIMENSION):
                if y * PIECE_DIMENSION + x in piece:
                    if (
                            y + self.current_piece.y >= self.Height
                            or x + self.current_piece.x >= self.Width
                            or x + self.current_piece.x < 0
                            or self.Field[y + self.current_piece.y][x + self.current_piece.x] > 0
                    ):
                        return True
        return False

    def break_lines(self):
        full_rows = []  # List to store indices of full rows
        for i in range(1, self.Height):
            if all(cell > 0 for cell in self.Field[i]):
                full_rows.append(i)

        for row in full_rows:
            del self.Field[row]
            self.Field.insert(0, [0] * self.Width)

    def freeze(self, piece):
        PIECE_DIMENSION = 4
        for y in range(PIECE_DIMENSION):
            for x in range(PIECE_DIMENSION):
                if y * PIECE_DIMENSION + x in piece:
                    self.Field[y + self.current_piece.y][x + self.current_piece.x] = self.current_piece.color
        self.break_lines()
        self.current_piece = TetrisPiece(self.Width, self.Height)
        if self.intersects(self.current_piece.get_current_shape()):
            self.State = "gameover"

    def go_space(self):
        while not self.intersects(self.current_piece.get_current_shape()):
            self.current_piece.move_down()
        self.current_piece.y -= 1
        self.freeze(self.current_piece.get_current_shape())

    def go_down(self):
        self.current_piece.move_down()
        if self.intersects(self.current_piece.get_current_shape()):
            self.current_piece.y -= 1
            self.freeze(self.current_piece.get_current_shape())

    def go_side(self, dx):
        old_x = self.current_piece.x
        self.current_piece.x += dx
        if self.intersects(self.current_piece.get_current_shape()):
            self.current_piece.x = old_x

    def rotate(self):
        old_rotation = self.current_piece.rotation
        self.current_piece.rotate()
        if self.intersects(self.current_piece.get_current_shape()):
            self.current_piece.rotation = old_rotation

    def draw_board(self):
        self.screen.fill((255, 255, 255))

        for i in range(self.Height):
            for j in range(self.Width):
                pygame.draw.rect(
                    self.screen,
                    (128, 128, 128),
                    [100 + 20 * j, 60 + 20 * i, 20, 20],
                    1,
                )
                if self.Field[i][j] > 0:
                    pygame.draw.rect(
                        self.screen,
                        TetrisPiece.COLORS[self.Field[i][j]],
                        [
                            100 + 20 * j + 1,
                            60 + 20 * i + 1,
                            20 - 2,
                            20 - 1,
                        ],
                    )

    def draw_piece(self):
        for y in range(self.PIECE_DIMENSION):
            for x in range(self.PIECE_DIMENSION):
                p = y * self.PIECE_DIMENSION + x
                if p in self.current_piece.get_current_shape():
                    x_pos = self.DRAW_X_OFFSET + self.BLOCK_SIZE * (x + self.current_piece.x) + self.BLOCK_BORDER
                    y_pos = self.DRAW_Y_OFFSET + self.BLOCK_SIZE * (y + self.current_piece.y) + self.BLOCK_BORDER

                    pygame.draw.rect(
                        self.screen,
                        self.current_piece.get_color(),
                        [
                            x_pos,
                            y_pos,
                            self.BLOCK_SIZE - 2 * self.BLOCK_BORDER,
                            self.BLOCK_SIZE - 2 * self.BLOCK_BORDER,
                        ],
                    )

    def main(self):
        while not self.done:
            self.counter += 1
            if self.counter > 100000:
                self.counter = 0

            if (
                    self.counter % (self.FPS // 2 // self.level) == 0
                    or self.pressing_down
            ) and self.State == "start":
                self.go_down()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.done = True
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.rotate()
                    if event.key == pygame.K_LEFT:
                        self.go_side(-1)
                    if event.key == pygame.K_RIGHT:
                        self.go_side(1)
                    if event.key == pygame.K_SPACE:
                        self.go_space()
                    if event.key == pygame.K_DOWN:
                        self.pressing_down = True

                if event.type == pygame.KEYUP and event.key == pygame.K_DOWN:
                    self.pressing_down = False

            self.draw_board()
            self.draw_piece()

            if self.State == "gameover":
                self.done = True

            pygame.display.flip()
            self.clock.tick(self.FPS)

        pygame.quit()


if __name__ == "__main__":
    game = TetrisGame()
    game.main()
