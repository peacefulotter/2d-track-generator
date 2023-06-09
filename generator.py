# https://coolors.co/274c77-8fa7a7-c20114-db3a34-76bed0

import random 
from collections import namedtuple

from background import generate_background
from tiles import Direction, tiles
from constants import TILE_SIZE, TILE_MAX_WIDTH, TILE_MAX_HEIGHT
from window import render

Track = namedtuple("Track", "tile pos")
Candidate = namedtuple("Candidate", "tile next_pos place_pos hitbox")

def new_pos_small(pos, dir):
    x, y = pos
    next_pos = (0, 0)
    if dir == Direction.TOP:
        next_pos = (x, y - 1)
    elif dir == Direction.RIGHT:
        next_pos = (x + 1, y)
    elif dir == Direction.BOTTOM:
        next_pos = (x, y + 1)
    elif dir == Direction.LEFT:
        next_pos = (x - 1, y)
    return next_pos, next_pos

def new_pos_big(tile, pos, dir):
    endpoint = tile.b_side if other_side(tile.a_side) == dir else tile.a_side
    x, y = pos
    dx =  -1 if endpoint == Direction.LEFT else 1
    dy =  -1 if endpoint == Direction.TOP  else 1
    pdx = -1 if endpoint == Direction.LEFT else 0
    pdy = -1 if endpoint == Direction.TOP  else 0
    if dir == Direction.TOP:
        return (x + pdx, y - 2), (x + dx, y - 2)
    elif dir == Direction.RIGHT:
        return (x + 1, y + pdy), (x + 2, y + dy)
    elif dir == Direction.BOTTOM:
        return (x + pdx, y + 1), (x + dx, y + 2)
    return (x - 2, y + pdy), (x - 2, y + dy)

def other_side(side):
    return (side + 2) % 4

def special_range(a, b):
    if a < b:
        return range(a, b + 1)
    else:
        return range(b, a + 1) 
    
def tile_hitbox(pos, next_pos, dir):
    hitbox = [] 
    new_x, new_y = next_pos
    (start_x, start_y), _ = new_pos_small(pos, dir)
    for i in special_range(start_x, new_x):
        for j in special_range(start_y, new_y):
            hitbox.append((i, j))
    return hitbox

def can_place_tile(occupied, hitbox):
    for coords in hitbox:
        if coords in occupied:
            return False
    return True


def get_candidates(occupied, pos, dir) -> list[Candidate]:
    candidates = []
    for tile in tiles:
        match_with_dir = other_side(tile.a_side) == dir or other_side(tile.b_side) == dir
        if not match_with_dir:
            continue
        
        place_pos, next_pos = new_pos_big(tile, pos, dir) if tile.is_big else new_pos_small(pos, dir)
        hitbox = tile_hitbox(pos, next_pos, dir)
        
        if can_place_tile(occupied, hitbox):
            candidate = Candidate(tile, next_pos, place_pos, hitbox) 
            candidates.append(candidate)

    return candidates

def update_rect(track_rect, hitbox):
    (x1, y1), (x2, y2) = track_rect
    for (x, y) in hitbox:
        if x < x1:
            x1 = x
        elif x > x2:
            x2 = x
        if y < y1:
            y1 = y
        elif y > y2:
            y2 = y
    return (x1, y1), (x2, y2)

def try_generate(length):
    track = []
    track_rect = ((0, 0), (0, 0)) # top left - bottom right
    dir = Direction.TOP
    pos = (0, 0)
    occupied = [pos]
    for i in range(length):
        if i == 0:
            tile = tiles[0]
            track.append(Track(tile, pos))
            dir = tile.a_side
        else:
            candidates = get_candidates(occupied, pos, dir)
            if len(candidates) == 0:
                return None, None, None, False
            
            (tile, next_pos, place_pos, hitbox) = random.choice(candidates)
            
            occupied.extend(hitbox)
            track.append(Track(tile, place_pos))

            track_rect = update_rect(track_rect, hitbox)
            dir = tile.b_side if other_side(tile.a_side) == dir else tile.a_side
            pos = next_pos

    return track, occupied, track_rect, True

def center_track(track, occupied, track_rect):
    (min_x, min_y), (max_x, max_y) = track_rect
    width = max_x - min_x
    height = max_y - min_y
    dx = int((TILE_MAX_WIDTH - width) / 2. - min_x)
    dy = int((TILE_MAX_HEIGHT - height) / 2. - min_y)
    center_track_rect = ((min_x + dx, min_y + dy), (max_x + dx, max_y + dy))
    print(track_rect, center_track_rect, TILE_MAX_WIDTH, TILE_MAX_HEIGHT)
    for i in range(len(track)):
        t = track[i]
        x, y = t.pos
        track[i] = Track(t.tile, (x + dx, y + dy))
    for i in range(len(occupied)):
        x, y = occupied[i]
        occupied[i] = (x + dx, y + dy)
    return track, occupied, center_track_rect

def generate(length, seed=42, decor_amount=25):
    random.seed(seed)
    
    # track
    done = False
    while not done:
        track, occupied, track_rect, done = try_generate(length)
    
    # center
    track, occupied, track_rect = center_track(track, occupied, track_rect)

    # decor
    background, decor = generate_background(occupied, decor_amount)
    
    return track, occupied, track_rect, background, decor

if __name__ == '__main__':
    length = 40
    seed = 42
    track, occupied, track_rect, background, decor = generate(length, seed)
    debug = True

    import pygame
    from pygame.locals import *
    pygame.init()
    green = (0, 255, 0)
    blue = (0, 0, 128)
    font = pygame.font.Font('freesansbold.ttf', 32)

    def cb(screen):
        global track, occupied, track_rect, background, decor, seed, length
        left, middle, right = pygame.mouse.get_pressed()
        if right:
            length += 1
            track, occupied, track_rect, background, decor = generate(length, seed)
        if middle:
            length -= 1
            track, occupied, track_rect, background, decor = generate(length, seed)
        if left:
            seed += 1
            track, occupied, track_rect, background, decor = generate(length, seed)

        for bg in background:
            x, y = bg.pos
            x = x * TILE_SIZE 
            y = y * TILE_SIZE
            screen.blit(bg.img, (x, y))
            
        for d in decor:
            x, y = d.pos
            x = x * TILE_SIZE 
            y = y * TILE_SIZE
            screen.blit(d.img, (x, y))



        for i, t in enumerate(track):
            x, y = t.pos
            x = x * TILE_SIZE 
            y = y * TILE_SIZE
            img = t.tile.img
            screen.blit(img, (x, y))
            if debug:
                text = font.render(str(i), True, green, blue)
                screen.blit(text, (x, y))
        
        if debug:
            for (x, y) in occupied:
                x = x * TILE_SIZE + TILE_SIZE / 2
                y = y * TILE_SIZE + TILE_SIZE / 2
                pygame.draw.circle(screen, 'red', (x, y), 10)

            (left, top), (right, bottom) = track_rect
            width  = (right - left + 1) * TILE_SIZE
            height = (bottom - top + 1) * TILE_SIZE
            rect = pygame.Rect(left * TILE_SIZE, top * TILE_SIZE, width, height)
            pygame.draw.rect(screen, 'red', rect, width=3)

    render(cb)

