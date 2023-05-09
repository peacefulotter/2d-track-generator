import pygame
from enum import IntEnum

from constants import TILE_SIZE

class Direction(IntEnum):
    TOP = 0
    RIGHT = 1
    BOTTOM = 2
    LEFT = 3

class Tile:
    def __init__(self, index, orientation, a_side, b_side, is_big=False):
        self.index = index
        self.orientation = orientation
        self.a_side = a_side
        self.b_side = b_side
        self.is_big = is_big
        self.img = self.load_img()

    def load_img(self):
        size = TILE_SIZE * (2 if self.is_big else 1)
        img = pygame.image.load(f'tiles/test-{self.index}.png')
        img = pygame.transform.rotate(img, self.orientation * 90)
        img = pygame.transform.scale(img, (size, size))
        return img

    def __repr__(self) -> str:
        return self.__str__()
    
    def __str__(self) -> str:
        return f'({self.index}, {self.orientation}, {self.a_side}:{self.b_side})' 


def straight(idx):
    return [
        Tile(idx, 0, Direction.RIGHT, Direction.LEFT),   
        Tile(idx, 1, Direction.TOP, Direction.BOTTOM),
    ]

def turn(idx, is_big=False):
    return [
        Tile(idx, 0, Direction.BOTTOM, Direction.LEFT, is_big),   
        Tile(idx, 1, Direction.RIGHT, Direction.BOTTOM, is_big),   
        Tile(idx, 2, Direction.TOP, Direction.RIGHT, is_big),   
        Tile(idx, 3, Direction.TOP, Direction.LEFT, is_big),
    ]

tiles = [
    *straight(1),
    *turn(2),
    *turn(3, is_big=True),
]

if __name__ == '__main__':
    from window import render
    def cb(screen):
        for i, tile in enumerate(tiles):
            x = i * TILE_SIZE
            screen.blit(tile.img, (x, 0))

    render(cb)