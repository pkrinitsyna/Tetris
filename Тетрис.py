import pygame
import random

pygame.init()

WINDOW_WIDTH = 400
WINDOW_HEIGHT = 800
BLOCK_DIMENSION = 20
COLUMNS = WINDOW_WIDTH // BLOCK_DIMENSION
ROWS = WINDOW_HEIGHT // BLOCK_DIMENSION
MOVE_SPEED = 0.1

BLACK = (0, 0, 0)  # Черный цвет
WHITE = (255, 255, 255)  # Белый цвет
GRAY = (128, 128, 128)  # Серый цвет
RED = (255, 0, 0)  # Красный цвет
GREEN = (0, 255, 0)  # Зеленый цвет
BLUE = (0, 0, 255)  # Синий цвет
CYAN = (0, 255, 255)  # Cyan (голубой)
MAGENTA = (255, 0, 255)  # Пурпурный
YELLOW = (255, 255, 0)  # Желтый цвет
BEZHEVIY = (245, 245, 220)  # Бежевый цвет

COLOR_PALETTE = [CYAN, BLUE, MAGENTA, YELLOW, GREEN, RED]
SHAPE_TEMPLATES = [
    [[1, 1, 1, 1]],  # Фигура "I"
    [[1, 1, 1], [0, 1, 0]],  # Фигура "T"
    [[1, 1, 1], [1, 0, 0]],  # Фигура "L"
    [[1, 1, 1], [0, 0, 1]],  # Фигура "J"
    [[1, 1], [1, 1]],  # Фигура "O"
    [[0, 1, 1], [1, 1, 0]],  # Фигура "S"
    [[1, 1, 0], [0, 1, 1]]  # Фигура "Z"
]

class Tetromino:
    def __init__(self, pos_x, pos_y, shape_matrix):
        self.x = pos_x
        self.y = pos_y

        self.shape = [
            shape_matrix,
            self.rotate_matrix(shape_matrix),
            self.rotate_matrix(self.rotate_matrix(shape_matrix)),
            self.rotate_matrix(self.rotate_matrix(self.rotate_matrix(shape_matrix)))
        ] # Возможные состояния при поворотах фигуры
        self.color = random.choice(COLOR_PALETTE)
        self.rotation_state = 0
    
    def rotate(self):
        self.rotation_state = (self.rotation_state + 1) % len(self.shape)  # Переход к следующему состоянию

    def get_image(self):
        return self.shape[self.rotation_state]  # Возвращаем текущую форму фигуры

    def rotate_matrix(self, matrix):
        return [list(row) for row in zip(*matrix[::-1])]  # Вращаем матрицу (на 90 градусов по часовой стрелке)
    
class TetrisGame:
    def __init__(self, screen):
        self.screen = screen  # Создание экрана, на котором будет отрисовываться игра
        self.grid = [[BLACK for q in range(COLUMNS)] for q in range(ROWS)]
        self.current_piece = self.generate_new_piece()  # Генерация текущей фигуры
        self.next_piece = self.generate_new_piece()      # Генерация следующей фигуры
        self.score = 0  # Начальный счет, равный 0
        self.is_game_over = False  # Флаг окончания игры
        self.move_dx = 0  # Перемещение по X
        self.move_dy = 0  # Перемещение по Y

    def generate_new_piece(self):
        return Tetromino(COLUMNS // 2 - 2, 0, random.choice(SHAPE_TEMPLATES))  # Фигурка начинается в середине #экрана
    
    def check_collision(self, offset_x=0, offset_y=0):
        for y, row in enumerate(self.current_piece.get_image()):  # Проходим по строкам фигуры
            for x, cell in enumerate(row):  # Проходим по ячейкам ряда
                if cell:  # Если ячейка фигуры занята
                    # Проверяем, не выходит ли фигура за границы или не сталкивается ли с другой фигурой:
                    if (x + self.current_piece.x + offset_x < 0 or 
                        x + self.current_piece.x + offset_x >= COLUMNS or 
                        y + self.current_piece.y + offset_y >= ROWS or 
                        self.grid[y + self.current_piece.y + offset_y][x + self.current_piece.x + offset_x] != BLACK): #Проверяет, не занята ли ячейка, в которую может попасть фигура, цветом, отличным от чёрного (то есть  #другой фигурой)
                        return True  # Если есть столкновение
        return False  # Если нет столкновений
    
    def lock_piece(self):
        for y, row in enumerate(self.current_piece.get_image()):  # Проходим по фигуре
            for x, cell in enumerate(row):  # Проходим по ячейкам
                if cell:  # Если ячейка занята
                    grid_y = y + self.current_piece.y  # Вычисляем координаты на сетке
                    grid_x = x + self.current_piece.x
                    if 0 <= grid_y < ROWS and 0 <= grid_x < COLUMNS:  # Проверка границ сетки
                        self.grid[grid_y][grid_x] = self.current_piece.color  # Блокируем ячейку цветом фигуры
        self.clear_filled_lines()  # Очищаем заполненные линии
        self.current_piece = self.next_piece  # Передаём состояние текущей фигуры следующей
        self.next_piece = self.generate_new_piece()  # Генерируем новую фигуру
        if self.check_collision():  # Проверяем на столкновения
            self.is_game_over = True  # Если есть столкновение, игра окончена (is_game_over=True)

    def clear_filled_lines(self):
        # Находим заполненные линии
        lines_to_clear = [i for i, row in enumerate(self.grid) if all(cell != BLACK for cell in row)]
        for i in lines_to_clear:  # Удаляем заполненные линии
            del self.grid[i]
            self.grid.insert(0, [BLACK for _ in range(COLUMNS)])  # Добавляем новую пустую линию сверху
        self.score += 100  # Увеличиваем счет
    
    def move_piece(self, delta_x):
        if not self.check_collision(delta_x, 0):  # Проверка на столкновение при перемещении
            self.current_piece.x += delta_x  # Перемещение фигуры
    
    def drop_piece(self):
        if not self.check_collision(0, 1):  # Проверка на столкновение при падении
            self.current_piece.y += 1  # Перемещение фигуры вниз
        else:
            self.lock_piece()  # Если есть столкновение, блокируем фигуру
    
    def rotate_piece(self):
        self.current_piece.rotate()  # Вращаем фигуру
        if self.check_collision():  # Проверка на столкновение после вращения, по умолчанию проверка через if #возвращает true. То есть, такую проверку можно записать так: if self.check_collision() == true:
        # В случае столкновения, возвращаем фигуру в исходное состояние, то есть делаем 3 вращения
            self.current_piece.rotate()
            self.current_piece.rotate()
            self.current_piece.rotate()

    def draw_grid(self):
        for y in range(ROWS):  # Проходим по строкам сетки
            for x in range(COLUMNS):  # Проходим по столбцам сетки
                pygame.draw.rect(self.screen, GRAY, (x * BLOCK_DIMENSION, y * BLOCK_DIMENSION, BLOCK_DIMENSION, BLOCK_DIMENSION), 1)  # Рисуем сетку
                if self.grid[y][x] != BLACK:  # Проверка с помощью цвета ячейки, занята ли она
                    pygame.draw.rect(self.screen, self.grid[y][x], (x * BLOCK_DIMENSION, y * BLOCK_DIMENSION, BLOCK_DIMENSION, BLOCK_DIMENSION))  # Если занята, то рисуем заблокированную ячейку

    def draw_piece(self, piece):
        for y, row in enumerate(piece.get_image()):  # Проходим по фигуре
            for x, cell in enumerate(row):  # Проходим по ячейкам
                if cell:  # Если ячейка занята 
                    pygame.draw.rect(
                        self.screen,
                        piece.color,
                        (
                            (x + piece.x) * BLOCK_DIMENSION,
                            (y + piece.y) * BLOCK_DIMENSION,
                            BLOCK_DIMENSION,
                            BLOCK_DIMENSION,
                        ),
                    )  # Рисуем фигуру на экране
    
    def draw_next_piece(self):
        for y, row in enumerate(self.next_piece.get_image()):  # Проходим по следующей фигуре
            for x, cell in enumerate(row):  # Проходим по ячейкам
                if cell:  # Если ячейка занята
                    pygame.draw.rect(
                        self.screen,
                        self.next_piece.color,
                        (
                            (x + COLUMNS + 1) * BLOCK_DIMENSION,
                            (y + 1) * BLOCK_DIMENSION,
                            BLOCK_DIMENSION,
                            BLOCK_DIMENSION,
                        ),
                    )  # Рисуем следующую фигуру справа от основной сетки
    
    def render(self):
        self.screen.fill(BLACK)  # Заливаем экран черным цветом
        self.draw_grid()  # Отрисовываем сетку
        self.draw_piece(self.current_piece)  # Отрисовываем текущую фигуру
        self.draw_next_piece()  # Отрисовываем следующую фигуру
        font = pygame.font.SysFont("Arial", 25)  # Шрифт для отображения счета
        score_text = font.render(f"Счет: {self.score}", True, WHITE)  # Текст с текущим счетом
        self.screen.blit(score_text, (10, 10))  # Отображаем счет на экране
        pygame.display.update()  # Обновляем экран

    def update_game_state(self):
        """Обновление состояния игры"""
        if not self.is_game_over:  # Если игра не окончена
            self.drop_piece()  # Фигура продолжает падать
        else:
            font = pygame.font.SysFont("Helvetica", 50)  # Шрифт для текста "Игра окончена"
            game_over_text = font.render("Игра окончена", True, BEZHEVIY)  # Создаем текст
            self.screen.blit(
                game_over_text,
                (
                    WINDOW_WIDTH // 2 - game_over_text.get_width() // 2,  # Центрируем текст по X
                    WINDOW_HEIGHT // 2 - game_over_text.get_height() // 2 - WINDOW_HEIGHT // 8,  # Центрируем текст по Y
                ),
            )
            pygame.display.update()  # Обновляем экран
            pygame.time.wait(3000)  # Ждем 3 секунды
            pygame.quit()  # Закрываем игру
            exit()  # Выход из программы

def main():
    # Установка параметров окна
    screen = pygame.display.set_mode((WINDOW_WIDTH + 6 * BLOCK_DIMENSION, WINDOW_HEIGHT))  # Создаем окно
    pygame.display.set_caption("Тетрис")  # Заголовок окна

    clock = pygame.time.Clock()  # Создаем объект для управления временем
    game = TetrisGame(screen)  # Создаем экземпляр игры
    running = True  # Флаг для цикла игры
    keys_pressed = set()  # Множество для отслеживания нажатых клавиш
    fall_speed = 500  # Время между падениями в миллисекундах
    last_move_time = pygame.time.get_ticks()  # Время последнего движения
    last_fall_time = pygame.time.get_ticks()  # Время последнего падения
    
    while running:  # Основной игровой цикл
        current_time = pygame.time.get_ticks()  # Получаем текущее время
        for event in pygame.event.get():  # Обработка событий
            if event.type == pygame.QUIT:  # Если нажата кнопка закрытия
                running = False  # Завершаем цикл
            if event.type == pygame.KEYDOWN:  # Если нажата клавиша
                if event.key in {pygame.K_LEFT, pygame.K_RIGHT, pygame.K_DOWN, pygame.K_UP}:  # Если это 
                #клавиши управления
                    keys_pressed.add(event.key)  # Добавляем клавишу в множество нажатых клавиш
            if event.type == pygame.KEYUP:  # Если клавиша отпущена
                if event.key in {pygame.K_LEFT, pygame.K_RIGHT, pygame.K_DOWN, pygame.K_UP}:  # Если это 
                #клавиши управления
                    keys_pressed.discard(event.key)  # Удаляем клавишу из множества нажатых клавиш
                    # Управление движением фигуры
                    
        if pygame.K_LEFT in keys_pressed:  # Если нажата клавиша влево
            game.move_piece(-1)  # Перемещаем фигуру влево
        if pygame.K_RIGHT in keys_pressed:  # Если нажата клавиша вправо
            game.move_piece(1)  # Перемещаем фигуру вправо
        if pygame.K_DOWN in keys_pressed:  # Если нажата клавиша вниз
            game.move_piece(0)  # Перемещаем фигуру (в этом случае не перемещаем, а просто сбрасываем вниз)
            game.drop_piece()  # Сбрасываем фигуру вниз
        if pygame.K_UP in keys_pressed:  # Если нажата клавиша вверх
            game.rotate_piece()  # Вращаем фигуру

        # Ускоренное падение фигуры
        if current_time - last_fall_time > fall_speed:  # Если прошло достаточно времени для падения
            game.drop_piece()  # Сбрасываем фигуру вниз
            last_fall_time = current_time  # Обновляем время последнего падения

        # Обновление экрана
        game.render()  # Отрисовываем текущую сцену

        # Обновление состояния игры
        game.update_game_state()  # Проверяем и обновляем состояние игры

        # Устанавливаем частоту кадров
        clock.tick(10)  # Ограничиваем FPS до 10
main()  # Запускаем основную функцию