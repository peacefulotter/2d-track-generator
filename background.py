import random
import pygame

from constants import TILE_SIZE, TILE_MAX_WIDTH, TILE_MAX_HEIGHT

def load_background_img(path, mult, rendering_order):
    size = mult * TILE_SIZE
    img = pygame.image.load(f'./decor/{path}.png')
    img = pygame.transform.scale(img, (size, size))
    return img, rendering_order

files = [
    ('Bush_01', 1, 1), ('Bush_02', 2, 1),
    ('Rock_01', 1, 0), ('Rock_02', 1, 0), 
    ('Rock_01', 2, 0), ('Rock_02', 2, 0), 
    ('Tree_01', 4, 2), ('Tree_02', 3, 2)
]
background_images = [
    load_background_img(path, mult, rendering_order) 
    for path, mult, rendering_order in files
]


class Background:
    def __init__(self, pos):
        self.pos = pos
        self.img, self.rendering_order = random.choice(background_images)
        self.img = pygame.transform.rotate(self.img, random.random() * 360)
    
    def __lt__(self, other):
         return self.rendering_order < other.rendering_order
    

def generate_background(visited, decor_amount=50) -> list[Background]:
    def get_random_coords():
        return (random.randint(0, TILE_MAX_WIDTH), random.randint(0, TILE_MAX_HEIGHT))
    
    background = []
    for _ in range(decor_amount):
        coords = get_random_coords()
        while coords in visited:
            coords = get_random_coords()
        background.append(Background(coords))
    background.sort()
    return background