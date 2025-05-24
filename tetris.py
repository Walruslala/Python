import pygame
import random
import sys

# เริ่มต้นโมดูลของ pygame
pygame.init()

# ขนาดหน้าจอ
CELL_SIZE = 30
COLS = 10
ROWS = 20
PANEL_WIDTH = 6  
WIDTH = CELL_SIZE * (COLS + PANEL_WIDTH)
HEIGHT = CELL_SIZE * ROWS

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Tetra')

# สี
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREY = (100, 100, 100)
TETROMINO_TYPES = {
    'I': ([[1,1,1,1]],        (0, 255, 255)),  # Cyan
    'O': ([[1,1],
           [1,1]],           (255, 255, 0)),   # Yellow
    'T': ([[1,1,1],
           [0,1,0]],         (128, 0, 128)),   # Purple
    'S': ([[0,1,1],
           [1,1,0]],         (0, 255, 0)),     # Green
    'Z': ([[1,1,0],
           [0,1,1]],         (255, 0, 0)),     # Red
    'J': ([[0,0,1],
           [1,1,1]],         (0, 0, 255)),     # Blue
    'L': ([[1,0,0],
           [1,1,1]],         (255, 165, 0))    # Orange
}

clock = pygame.time.Clock()
FPS = 60

font = pygame.font.SysFont('Arial', 24)
big_font = pygame.font.SysFont('Arial', 48)

# ตัวแปรเกม
grid = [[BLACK for _ in range(COLS)] for _ in range(ROWS)]

class Tetromino:
    def __init__(self, type_name=None):
        if type_name is None:
            self.type = random.choice(list(TETROMINO_TYPES.keys()))
        else:
            self.type = type_name

        self.shape, self.color = TETROMINO_TYPES[self.type]
        self.x = COLS // 2 - len(self.shape[0]) // 2
        self.y = 0

    def rotate(self):
        rotated = [list(row) for row in zip(*self.shape[::-1])]
        if not self.collide(0, 0, rotated):
            self.shape = rotated

    def collide(self, dx, dy, shape=None):
        if shape is None:
            shape = self.shape
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    new_x = self.x + x + dx
                    new_y = self.y + y + dy
                    if new_x < 0 or new_x >= COLS or new_y >= ROWS:
                        return True
                    if new_y >= 0 and grid[new_y][new_x] != BLACK:
                        return True
        return False

    def freeze(self):
        for y, row in enumerate(self.shape):
            for x, cell in enumerate(row):
                if cell:
                    grid[self.y + y][self.x + x] = self.color

    def move(self, dx, dy):
        if not self.collide(dx, dy):
            self.x += dx
            self.y += dy
            return True
        return False


def clear_lines():
    global grid
    lines_cleared = 0
    new_grid = []
    for row in grid:
        if all(cell != BLACK for cell in row):
            lines_cleared += 1
        else:
            new_grid.append(row)
    for _ in range(lines_cleared):
        new_grid.insert(0, [BLACK for _ in range(COLS)])
    grid = new_grid
    return lines_cleared

def draw_grid():
    for x in range(COLS):
        for y in range(ROWS):
            pygame.draw.rect(screen, GREY, (x*CELL_SIZE, y*CELL_SIZE, CELL_SIZE, CELL_SIZE), 1)

def draw_piece(piece, offset_x, offset_y):
    for y, row in enumerate(piece.shape):
        for x, cell in enumerate(row):
            if cell:
                pygame.draw.rect(screen, piece.color, 
                                 (offset_x + x*CELL_SIZE, offset_y + y*CELL_SIZE, CELL_SIZE, CELL_SIZE))

def draw_text(text, font, color, center):
    text_surface = font.render(text, True, color)
    rect = text_surface.get_rect(center=center)
    screen.blit(text_surface, rect)

def menu_screen():
    screen.fill(BLACK)
    draw_text('TETRA', big_font, WHITE, (WIDTH//2, HEIGHT//3))
    draw_text('Press ENTER to Start', font, WHITE, (WIDTH//2, HEIGHT//2))
    pygame.display.update()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    waiting = False

def game_over_screen(score):
    screen.fill(BLACK)
    draw_text('GAME OVER', big_font, WHITE, (WIDTH//2, HEIGHT//3))
    draw_text(f'Score: {score}', font, WHITE, (WIDTH//2, HEIGHT//2))
    draw_text('Press R to Restart', font, WHITE, (WIDTH//2, HEIGHT//1.5))
    pygame.display.update()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    waiting = False


def main():
    global grid
    menu_screen()

    running = True
    current_piece = Tetromino()
    next_piece = Tetromino()
    hold_piece = None
    can_hold = True
    fall_time = 0
    fall_speed = 500
    score = 0

    while running:
        dt = clock.tick(FPS)
        fall_time += dt

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_piece.move(-1, 0)
                if event.key == pygame.K_RIGHT:
                    current_piece.move(1, 0)
                if event.key == pygame.K_DOWN:
                    current_piece.move(0, 1)
                if event.key == pygame.K_UP:
                    current_piece.rotate()
                if event.key == pygame.K_LSHIFT:
                    if can_hold:
                        if hold_piece is None:
                            hold_piece = Tetromino(current_piece.type)
                            current_piece = next_piece
                            next_piece = Tetromino()
                        else:
                            hold_piece.type, current_piece.type = current_piece.type, hold_piece.type
                            hold_piece.shape, hold_piece.color = TETROMINO_TYPES[hold_piece.type]
                            current_piece.shape, current_piece.color = TETROMINO_TYPES[current_piece.type]
                        can_hold = False
                if event.key == pygame.K_SPACE:
                    while current_piece.move(0, 1):
                        pass
                    current_piece.freeze()
                    lines = clear_lines()
                    score += lines * 100
                    fall_speed = max(100, fall_speed - 20 * lines)
                    current_piece = next_piece
                    next_piece = Tetromino()
                    can_hold = True
                    if current_piece.collide(0, 0):
                        game_over_screen(score)
                        grid = [[BLACK for _ in range(COLS)] for _ in range(ROWS)]
                        main()


        if fall_time > fall_speed:
            if not current_piece.move(0, 1):
                current_piece.freeze()
                lines = clear_lines()
                score += lines * 100
                if lines > 0:
                    fall_speed = max(100, fall_speed - 20)
                current_piece = next_piece
                next_piece = Tetromino()
                can_hold = True
                if current_piece.collide(0, 0):
                    game_over_screen(score)
                    grid = [[BLACK for _ in range(COLS)] for _ in range(ROWS)]
                    main()
            fall_time = 0

        screen.fill(BLACK)

        # วาดบล็อกที่ล็อคแล้ว
        for y in range(ROWS):
            for x in range(COLS):
                color = grid[y][x]
                if color != BLACK:
                    pygame.draw.rect(screen, color, (x*CELL_SIZE, y*CELL_SIZE, CELL_SIZE, CELL_SIZE))

        # วาดบล็อกที่กำลังตก
        draw_piece(current_piece, current_piece.x*CELL_SIZE, current_piece.y*CELL_SIZE)

        # วาดตาราง
        draw_grid()

        # วาด Panel ขวา
        pygame.draw.rect(screen, GREY, (COLS*CELL_SIZE, 0, PANEL_WIDTH*CELL_SIZE, HEIGHT))

        # แสดง Score
        draw_text(f'Score: {score}', font, WHITE, (COLS*CELL_SIZE + PANEL_WIDTH*CELL_SIZE//2, 50))

        # แสดง Next Piece
        draw_text('Next:', font, WHITE, (COLS*CELL_SIZE + PANEL_WIDTH*CELL_SIZE//2, 120))
        draw_piece(next_piece, COLS*CELL_SIZE + CELL_SIZE, 150)

        # แสดง Hold Piece
        draw_text('Hold:', font, WHITE, (COLS*CELL_SIZE + PANEL_WIDTH*CELL_SIZE//2, 300))
        if hold_piece:
            draw_piece(hold_piece, COLS*CELL_SIZE + CELL_SIZE, 330)

        pygame.display.update()

main()