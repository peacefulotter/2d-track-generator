import pygame

from constants import WIDTH, HEIGHT

def render(cb):
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill("#264027")
        cb(screen)

        pygame.display.flip()
        clock.tick(10)

    pygame.quit()