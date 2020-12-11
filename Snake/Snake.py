"""Assignment: Snake
   Created on 11 dec. 2020
   Author: Anh Duy Nguyen"""

from ipy_lib import SnakeUserInterface

ID_EMPTY = 0
ID_FOOD = 1
ID_SNAKE = 2
ID_WALL = 3
WIDTH = 32
HEIGHT = 24
MAX_X = WIDTH - 1
MIN_X = 0
MAX_Y = HEIGHT - 1
MIN_Y = 0
ANIMATION_SPEED = 10
INIT_DIRECTION = 'r'
INIT_SNAKE_COORDINATES = [(1, 0), (0, 0)]


class Coordinate:
    def __init__(self, x, y):
        self.x = int(x)
        self.y = int(y)

    def change_values(self, change_x, change_y):
        self.x += change_x
        self.y += change_y

        return self.x, self.y

    def swap_values(self, x, y):
        self.x = x
        self.y = y

        return self.x, self.y

    def move(self, direction):
        if direction == 'l':
            self.change_values(-1, 0) if self.x != MIN_X else self.swap_values(MAX_X, self.y)
        if direction == 'r':
            self.change_values(1, 0) if self.x != MAX_X else self.swap_values(MIN_X, self.y)
        if direction == 'u':
            self.change_values(0, -1) if self.y != MIN_Y else self.swap_values(self.x, MAX_Y)
        if direction == 'd':
            self.change_values(0, 1) if self.y != MAX_Y else self.swap_values(self.x, MIN_Y)


class Snake:
    def __init__(self, coordinates):
        # A snake consists of a list of coordinates where all the pieces of the snake are located on the grid
        self.coordinates = coordinates

    def get_coordinates(self):
        return self.coordinates

    def get_head(self):
        return self.coordinates[0]

    def get_tail(self):
        return self.coordinates[-1]

    def get_body(self):
        return self.coordinates[1:]

    def position(self, direction):
        # Determines the next position of the snake
        # The movement of the snake is basically removal of the tail and extension of the head
        new_head = Coordinate(*self.get_head())
        new_head.move(direction)
        self.coordinates.insert(0, (new_head.x, new_head.y))
        self.coordinates.remove(self.coordinates[-1])

    def place(self, ui):
        # Places the snake on the interface by placing the pieces respective to their coordinates
        for coordinate in self.coordinates:
            coordinate = Coordinate(*coordinate)
            ui.place(coordinate.x, coordinate.y, ID_SNAKE)

    def extend_tail(self):
        # Extends the tail of the snake by adding the tail to the snake, so it cancels out the tail being removed
        # in self.place
        self.coordinates.append(self.get_tail())

    def game_over(self, walls):
        # Checks whether the player has lost
        # You have lost when the head of the snake hits its own body, or when the head hits a wall
        return (self.get_head() in self.get_body()) or (self.get_head() in walls)


class Food:
    def __init__(self, food):
        self.food = food

    def get_coordinates(self):
        return Coordinate(*self.food)

    def generate(self, ui, snake, walls):
        # Generates new coordinates for the food, the new coordinates cannot be the same as before, within the snake,
        # nor within the walls
        new_food = (ui.random(MAX_X), ui.random(MAX_Y))
        while (new_food == self.food) or (new_food in snake) or (new_food in walls):
            new_food = (ui.random(MAX_X), ui.random(MAX_Y))
        self.food = new_food

    def place(self, ui):
        food_coordinates = self.get_coordinates()
        ui.place(food_coordinates.x, food_coordinates.y, ID_FOOD)

    def eaten(self, snake_head):
        # Checks if the food is eaten, by looking if the snake's head is in the same position as the food
        snake_head = Coordinate(*snake_head)
        food_coordinates = self.get_coordinates()
        return (food_coordinates.x, food_coordinates.y) == (snake_head.x, snake_head.y)

    def remove(self, ui):
        # 'Removes' the food from the grid by replacing it with a snake piece
        food_coordinates = self.get_coordinates()
        ui.place(food_coordinates.x, food_coordinates.y, ID_SNAKE)


class Walls:
    def __init__(self, coordinates):
        self.coordinates = coordinates

    def get_coordinates(self):
        return self.coordinates

    def place(self, ui):
        for wall in self.coordinates:
            wall = Coordinate(*wall)
            ui.place(wall.x, wall.y, ID_WALL)


def read_file(file_name):
    file = open(file_name)
    open_file = file.readlines()
    file.close()

    return open_file


def change_direction(new_direction):
    global direction
    direction = new_direction
    return direction


def legal_move(event_data, direction):
    # The snake can only move forwards, so it can only move vertically when going horizontally and vice versa
    if event_data in {'l', 'r'} and direction in {'u', 'd'}:
        return True
    elif event_data in {'u', 'd'} and direction in {'l', 'r'}:
        return True


def prepare_data_level(level):
    # Prepares the data of the level by separating the initial direction and the coordinates of the walls and the
    # initial snake, returning the lists of the coordinates for the latter.
    # The parsing is done as the description given in the practical manual, hence the separation of the first two lines
    # And the rest of the code
    walls = []
    init_snake_coordinates = []
    init_direction = ''

    for line in level[:2]:
        if '=' in line:
            line = line.split('=')
            coordinate_snake = Coordinate(*line[0].split())
            init_direction = line[1].lower()
            coordinate_wall = Coordinate(*line[2].split())

            init_snake_coordinates.append((coordinate_snake.x, coordinate_snake.y))
            walls.append((coordinate_wall.x, coordinate_wall.y))
            break

        line = line.split()
        coordinate_snake = Coordinate(*line)
        init_snake_coordinates.append((coordinate_snake.x, coordinate_snake.y))

    for coordinate in level[2:]:
        coordinate = Coordinate(*coordinate.split())
        walls.append((coordinate.x, coordinate.y))

    return walls, init_snake_coordinates, init_direction


def process_event(event):
    global direction
    global ui
    global snake
    global food
    global walls

    if event.name == 'arrow':
        if legal_move(event.data, direction):
            direction = event.data

    if event.name == 'alarm':


        ui.clear()
        snake.position(direction)
        if snake.game_over(walls.get_coordinates()):
            print('GAME OVER')
            ui.wait(1000)
            ui.close()
        if food.eaten(snake.get_head()):
            food.remove(ui)
            food.generate(ui, snake.get_coordinates(), walls.get_coordinates())
            snake.extend_tail()
        snake.place(ui)
        food.place(ui)
        walls.place(ui)
        ui.show()


'''Start program'''

ui = SnakeUserInterface(WIDTH, HEIGHT)
ui.set_animation_speed(ANIMATION_SPEED)
init_snake_coordinates = INIT_SNAKE_COORDINATES
direction = INIT_DIRECTION
walls = []
level = None
# level = read_file('SnakeInput4.txt')                       # Uncomment if you want to play levels

if level is not None:
    walls, init_snake_coordinates, direction = prepare_data_level(level)

snake = Snake(init_snake_coordinates)
walls = Walls(walls)
food = Food((ui.random(MAX_X), ui.random(MAX_Y)))
food.generate(ui, snake.get_coordinates(), walls.get_coordinates())

while True:

    event = ui.get_event()
    process_event(event)
