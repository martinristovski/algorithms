import math
import pygame
from queue import PriorityQueue

# COLORS
EMPTY_COLOR = (255, 255, 255) # white
CLOSED_COLOR = (255, 0, 0)    # red
OPEN_COLOR = (0, 255, 0)      # green
BARRIER_COLOR = (0, 0, 0)     # black
START_COLOR = (255, 165, 0)   # orange
END_COLOR = (140, 0, 140)     # purple
PATH_COLOR = (240, 230, 140)  # yellow


WINDOW_SIZE = 800
WINDOW = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
pygame.display.set_caption("A* Visualization")


class Square:
    def __init__(self, row, col, size, total_rows):
        self.row = row
        self.col = col
        self.x = row * size
        self.y = col * size
        self.size = size
        self.total_rows = total_rows
        self.color = EMPTY_COLOR

        self.neighbors = []

    def get_position(self):
        return self.row, self.col
    
    def is_closed(self):
        return self.color == CLOSED_COLOR

    def is_open(self):
        return self.color == OPEN_COLOR    

    def is_barrier(self):
        return self.color == BARRIER_COLOR

    def is_start(self):
        return self.color == START_COLOR

    def is_end(self):
        return self.color == END_COLOR

    def reset(self):
        self.color = EMPTY_COLOR

    def make_closed(self):
        self.color = CLOSED_COLOR

    def make_open(self):
        self.color = OPEN_COLOR

    def make_barrier(self):
        self.color = BARRIER_COLOR

    def make_start(self):
        self.color = START_COLOR

    def make_end(self):
        self.color = END_COLOR

    def make_path(self):
        self.color = PATH_COLOR

    def draw(self, window):
        pygame.draw.rect(WINDOW, self.color,
            (self.x, self.y, self.size, self.size))

    def update_neighbors(self, grid):
        self.neighbors = []

        if (self.row < self.total_rows - 1 and 
            not grid[self.row + 1][self.col].is_barrier()): # down
            self.neighbors.append(grid[self.row + 1][self.col])

        if (self.row > 0 and 
            not grid[self.row - 1][self.col].is_barrier()): # up
            self.neighbors.append(grid[self.row - 1][self.col])

        if (self.col < self.total_rows - 1 and 
            not grid[self.row][self.col + 1].is_barrier()): # right
            self.neighbors.append(grid[self.row][self.col + 1])

        if (self.col > 0 and 
            not grid[self.row][self.col - 1].is_barrier()): # left
            self.neighbors.append(grid[self.row][self.col - 1])

    def __lt__(self, other):
        return False

def heuristic(point1, point2):
    x1, y1 = point1
    x2, y2 = point2
    return abs(x2 - x1) + abs (y2 - y1)

def reconstruct_path(origin, current, draw):
    while current in origin:
        current = origin[current]
        current.make_path()
        draw()


def algorithm(draw, grid, start, end):
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))

    origin = {}

    g_score = {square: float("inf") for row in grid for square in row}
    g_score[start] = 0

    f_score = {square: float("inf") for row in grid for square in row}
    f_score[start] = heuristic(start.get_position(), end.get_position())

    open_set_hash = {start}

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        
        current = open_set.get()[2]
        open_set_hash.remove(current)

        if current == end:
            reconstruct_path(origin, end, draw)
            start.make_start()
            end.make_end()
            return True

        for neighbor in current.neighbors:
            temp_g_score = g_score[current] + 1

            if temp_g_score < g_score[neighbor]:
                origin[neighbor] = current
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = (temp_g_score + 
                    heuristic(neighbor.get_position(), end.get_position()))

                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
                    neighbor.make_open()

        draw()

        if current != start:
            current.make_closed()
    
    return False


def make_grid(rows, size):
    grid = []
    gap = size // rows
    
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            square = Square(i, j, gap, rows)
            grid[i].append(square)

    return grid

def draw_grid(window, rows, size):
    gap = size // rows

    for i in range(rows):
        pygame.draw.line(window, BARRIER_COLOR, (0, i*gap), (size, i*gap))
        for j in range(rows):
            pygame.draw.line(window, BARRIER_COLOR, (j*gap, 0), (j*gap, size))

def draw(window, grid, rows, size):
    window.fill(EMPTY_COLOR)

    for row in grid:
        for square in row:
            square.draw(window)

    draw_grid(window, rows, size)

    pygame.display.update()

def get_clicked_position(position, rows, size):
    gap = size // rows
    y, x = position

    row = y // gap
    col = x // gap

    return row, col

def main(window, size):
    ROWS = 50
    grid = make_grid(ROWS, size)

    start = None
    end = None

    run = True

    while run:
        draw(WINDOW, grid, ROWS, size)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if pygame.mouse.get_pressed()[0]: # left click
                position = pygame.mouse.get_pos()
                row, col = get_clicked_position(position, ROWS, size)
                square = grid[row][col]

                if not start and square != end:
                    start = square
                    start.make_start()
                
                elif not end and square != start:
                    end = square
                    end.make_end()
                
                elif square != start and square != end:
                    square.make_barrier()

            elif pygame.mouse.get_pressed()[2]: # right click
                position = pygame.mouse.get_pos()
                row, col = get_clicked_position(position, ROWS, size)
                square = grid[row][col]
                square.reset()
                if square == start:
                    start = None
                if square == end:
                    stop = None
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and start and end:
                    for row in grid:
                        for square in row:
                            square.update_neighbors(grid)
                    
                    algorithm(lambda: draw(WINDOW, grid, ROWS, size), 
                        grid, start, end)

                if event.key == pygame.K_c:
                    start = None
                    end = None
                    grid = make_grid(ROWS, size)

    pygame.quit()

main(WINDOW, WINDOW_SIZE)