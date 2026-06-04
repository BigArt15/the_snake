from random import randrange

import pygame

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

# Скорость движения змейки:
SPEED = 20

# Настройка игрового окна:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pygame.display.set_caption('Змейка')

# Настройка времени:
clock = pygame.time.Clock()


# Тут опишите все классы игры.
class GameObject:
    """
    Базовый класс для всех игровых объектов (яблоко, змейка).

    Attributes:
        position (tuple[int, int]): Координаты (x, y) объекта в пикселях.
        body_color (tuple[int, int, int]): RGB-цвет объекта.
    """

    def __init__(self, body_color):
        """
        Инициализирует игровой объект.

        Args:
        body_color: Цвет тела объекта в формате (R, G, B).
        """
        self.position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.body_color = body_color

    def draw(self):
        """
        Базовый метод для отрисовки объектов, будет переопредеён
        для дочерних классов, заглушка.
        """
        pass


class Apple(GameObject):
    """
    Класс яблока — еды для змейки.

    Появляется в случайной свободной позиции на игровом поле.
    """

    def __init__(self, body_color):
        super().__init__(body_color)
        self.body_color = body_color

    def randomize_position(self):
        """Случайным образом ставит яблоко на игровом поле."""
        apple_x = randrange(0, SCREEN_WIDTH, GRID_SIZE)
        apple_y = randrange(0, SCREEN_HEIGHT, GRID_SIZE)
        self.position = (apple_x, apple_y)

    def draw(self):
        """Рисует яблоко на игровом поле."""
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


class Snake(GameObject):
    """
    Класс змейки.

    Управляется клавишами со стрелками. Может расти после поедания яблока.
    При столкновении с собой сбрасывается до начального состояния.
    """

    def __init__(self, body_color, direction):
        super().__init__(body_color)
        self.start_position = self.position
        self.start_direction = direction
        self.positions = [self.position]
        self.length = 1
        self.direction = direction
        self.next_direction = None
        self.body_color = body_color
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
        new_head_x = head_snake_x + self.direction[0] * GRID_SIZE
        new_head_y = head_snake_y + self.direction[1] * GRID_SIZE
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
            rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, self.body_color, rect)
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

        head_rect = pygame.Rect(self.positions[0], (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, head_rect)
        pygame.draw.rect(screen, BORDER_COLOR, head_rect, 1)

        if self.last:
            last_rect = pygame.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)

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
        snake: Экземпляр змейки, для которой меняется направление.
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pygame.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pygame.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pygame.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT


def main():
    """
    Главная функция игры Змейка.

    Инициализирует Pygame, создаёт объекты Apple и Snake, запускает игровой
    цикл. Обрабатывает поедание яблока (увеличение длины) и столкновение с
    собой (сброс). Управляет отрисовкой и скоростью игры.
    """
    pygame.init()

    # Инициализация PyGame:
    # Тут нужно создать экземпляры классов.
    apple = Apple(APPLE_COLOR)
    apple.randomize_position()
    snake = Snake(SNAKE_COLOR, RIGHT)
    while True:
        clock.tick(SPEED)
        apple.draw()
        snake.draw()
        handle_keys(snake)
        snake.update_direction()
        if snake.get_head_position() == apple.position:
            snake.length += 1
            apple.randomize_position()
        snake.move()

        if snake.get_head_position() in snake.positions[1::]:
            snake.reset()
            apple.randomize_position()
        pygame.display.update()


if __name__ == '__main__':
    main()
