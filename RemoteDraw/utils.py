import pygame


WINDOW_SIZE = (900, 600)
LINE_THICK = 3


def pygame_start(name):
    pygame.init()
    window = pygame.display.set_mode(WINDOW_SIZE)
    window.fill((255, 255, 255))
    pygame.display.set_caption(name)
    pygame.display.update()
    return window


def draw_point(window, x, y):
    pygame.draw.circle(window, (0, 0, 0), (x, y), LINE_THICK)
    return window


def draw_line(window, x_from, y_from, x_to, y_to):
    pygame.draw.line(window, (0, 0, 0), (x_from, y_from), (x_to, y_to), LINE_THICK)
    return window
