from random import choice, randrange
import pygame as pg

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)
POISON_APPLE_COLOR = (0, 0, 255)

# Скорость движения змейки:
SPEED = 20

# Настройка игрового окна:
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pg.display.set_caption('Змейка')

# Настройка времени:
clock = pg.time.Clock()

# Тут опишите все классы игры.
class GameObject:
    """
    Базовый класс для всех игровых объектов (яблоко, змейка).

    Attributes:
        position (tuple[int, int]): Координаты (x, y) объекта в пикселях.
        body_color (tuple[int, int, int]): RGB-цвет объекта.
    """

    def __init__(self, body_color = None):
        """
        Инициализирует игровой объект.
        """
        self.position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.body_color = body_color

    def _draw_rect(self, position, color):
        rect = pg.Rect(position, (GRID_SIZE, GRID_SIZE))        
        pg.draw.rect(screen, color, rect)
        pg.draw.rect(screen, BORDER_COLOR, rect, 1)

    def draw(self):
        """
        Базовый метод для отрисовки объектов, будет переопределён
        для дочерних классов, заглушка.
        """
        raise NotImplementedError

class Apple(GameObject):
    """
    Класс яблока — еды для змейки.

    Появляется в случайной свободной позиции на игровом поле.
    """

    def __init__(self, body_color = APPLE_COLOR, free_rect = None):
        super().__init__(body_color)
        self.free_rect = free_rect
        self.randomize_position()

    def randomize_position(self):
        """Случайным образом ставит яблоко на игровом поле."""
        if self.free_rect:
            self.position = choice(self.free_rect)
        else:
            apple_x = randrange(0, GRID_WIDTH)
            apple_y = randrange(0, GRID_HEIGHT)
            self.position = (apple_x, apple_y)
    def draw(self):
        """Рисует яблоко на игровом поле."""
        self._draw_rect(self.position, self.body_color)


class PoisonApple(Apple):
    """
    Класс отравленного яблока для змейки, уменьшает её длину на одно
    деление. Наследует все методы от Apple.
    """

    def __init__(self, body_color = POISON_APPLE_COLOR):
        super().__init__(body_color)
        self.randomize_position()

class Snake(GameObject):
    """
    Класс змейки.

    Управляется клавишами со стрелками. Может расти после поедания яблока.
    При столкновении с собой сбрасывается до начального состояния.
    """

    def __init__(self, body_color = SNAKE_COLOR):
        super().__init__()
        self.start_position = self.position
        self.start_direction = RIGHT
        self.positions = [self.position]
        self.length = 1
        self.direction = RIGHT
        self.next_direction = None
        self.last = None

    def reset(self):
        """Перезапускает игру при столкновении змейки с собой."""
        self.positions = [self.start_position]
        self.direction = self.start_direction
        self.next_direction = None
        self.last = None
        self.length = 1

    def get_head_position(self):
        """Определяет положение головы змейки."""
        return self.positions[0]

    def move(self):
        """
        Перемещает змейку на один шаг в текущем направлении.

        Новая голова добавляется в начало списка. Если длина превышает
        self.length, хвост удаляется и сохраняется в self.last для
        последующего затирания. При выходе за границы экрана координаты
        зацикливаются (телепортация).
        """
        head_snake_x, head_snake_y = self.get_head_position()
        dx, dy = self.direction
        new_head_x = head_snake_x + dx * GRID_SIZE
        new_head_y = head_snake_y + dy * GRID_SIZE
        new_head_x = new_head_x % SCREEN_WIDTH
        new_head_y = new_head_y % SCREEN_HEIGHT
        self.positions.insert(0, (new_head_x, new_head_y))
        if len(self.positions) > self.length:
            self.last = self.positions.pop()
        else:
            self.last = None

    def draw(self):
        """
        Отрисовывает змейку: каждый сегмент — прямоугольник с границей;
        предыдущий хвост закрашивается фоном.
        """
        for position in self.positions[:-1]:
            self._draw_rect(position, self.body_color)
            
        self._draw_rect(self.get_head_position(), self.body_color)
        if self.last:
            self._draw_rect(self.last, BOARD_BACKGROUND_COLOR)
            
    def update_direction(self):
        """
        Применяет запрошенное направление (self.next_direction), если оно
        задано.
        """
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

def handle_keys(game_object):
    """
    Обрабатывает события клавиатуры и закрытие окна.

    Изменяет next_direction змейки, предотвращая разворот на 180°.
    При закрытии окна завершает игру.

    Args:
        game_object: Экземпляр змейки, для которой меняется направление.
    """
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            raise SystemExit
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pg.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pg.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pg.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT

def game_reset(snake, apple, poison_apple ):
    """Сбрасывает игру в начало."""
    snake.reset()
    free_apple = get_free_rect(snake)
    apple.randomize_position(free_apple)
    free = get_free_rect(snake, apple=)
    poison_apple.randomize_position(free)
    return SPEED

def get_free_rect(snake, apple= None):
    occupied_rect = set(snake.positions)
    if apple and apple.position:
        occupied_rect.add(apple.position)
    all_rect = set()
    for x in range(0, SCREEN_WIDTH, GRID_SIZE):
        for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
            all_rect.add((x, y))
    free_rect = all_rect - occupied_rect
    return free_rect            

def main():
    """
    Главная функция игры Змейка.

    Инициализирует Pygame, создаёт объекты Apple и Snake, запускает игровой
    цикл. Обрабатывает поедание яблока (увеличение длины) и столкновение с
    собой (сброс). Управляет отрисовкой и скоростью игры.
    """
    pg.init()

    # Инициализация PyGame:
    # Тут нужно создать экземпляры классов.
    snake = Snake()
    free = get_free_rect(snake)
    apple = Apple(free)
    free_poison = get_free_rect(snake, apple)
    poison_apple = PoisonApple(free_poison)
    current_speed = SPEED
    while True:
        clock.tick(current_speed)
        screen.fill(BOARD_BACKGROUND_COLOR)
        handle_keys(snake)
        snake.update_direction()
        snake.move()
        # Проверка съедения обычного яблока
        if snake.get_head_position() == apple.position:
            snake.length += 1
            free = get_free_rect(snake, poison_apple)
            apple.randomize_position(free)
            current_speed += 1

        # Проверка съедения отравленного яблока
        if snake.get_head_position() == poison_apple.position:
            if snake.length > 1:
                snake.length -= 1
                free = get_free_rect(snake, apple)
                poison_apple.randomize_position(free)
                # Удаляем последний сегмент змейки
                if len(snake.positions) > snake.length:
                    snake.last = snake.positions.pop()
            else:
                current_speed = game_reset(snake, apple, poison_apple)
        if snake.get_head_position() in snake.positions[1::]:
            current_speed = game_reset(snake, apple, poison_apple)
        apple.draw()
        poison_apple.draw()
        snake.draw()
        pg.display.update()

if __name__ == '__main__':
    main()