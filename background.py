import random
import pygame
from perlin_noise import PerlinNoise

from constants import TILE_SIZE, TILE_MAX_WIDTH, TILE_MAX_HEIGHT

noise = PerlinNoise(octaves=3, seed=1)

def load_decor_img(path, mult, rendering_order):
    size = mult * TILE_SIZE * (random.random() + 0.5)
    img = pygame.image.load(f'./decor/{path}.png')
    img = pygame.transform.scale(img, (size, size))
    return img, rendering_order

decor_details = [
    ('Bush_01', 1, 1), ('Bush_02', 2, 1),
    ('Rock_01', 1, 0), ('Rock_02', 1, 0), 
    ('Rock_01', 2, 0), ('Rock_02', 2, 0), 
    ('Tree_01', 4, 2), ('Tree_02', 3, 2)
]

decor_images = [
    load_decor_img(path, mult, rendering_order) 
    for path, mult, rendering_order in decor_details
]

def load_background_img(path):
    img = pygame.image.load(f'./background/{path}.png')
    img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    return img

background_images = [
    load_background_img(path) 
    for path in ['grass', 'soil', 'water']
]


class Decor:
    def __init__(self, pos):
        self.pos = pos
        self.img, self.rendering_order = random.choice(decor_images)
        self.img = pygame.transform.rotate(self.img, random.random() * 360)
    
    def __lt__(self, other):
        return self.rendering_order < other.rendering_order
    
class Background:
    def __init__(self, pos, img):
        self.pos = pos
        self.img = img
    

def generate_background(visited, decor_amount=50) -> list[Decor]:
    def get_random_coords():
        return (random.randint(0, TILE_MAX_WIDTH), random.randint(0, TILE_MAX_HEIGHT))
    
    background = []
    for i in range(TILE_MAX_WIDTH):
        for j in range(TILE_MAX_HEIGHT):
            lvl = noise([ i / float(TILE_MAX_HEIGHT), j / float(TILE_MAX_HEIGHT) ]) 
            if lvl < 0:
                idx = 0
            elif lvl < 0.4:
                idx = 1
            else:
                idx = 2
            img = background_images[idx]
            background.append(Background((i, j), img))

    decor = []
    for _ in range(decor_amount):
        coords = get_random_coords()
        while coords in visited:
            coords = get_random_coords()
        decor.append(Decor(coords))
    decor.sort()
    
    return background, decor