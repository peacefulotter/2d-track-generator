
# Inspired by https://www.gamedeveloper.com/programming/generating-procedural-racetracks

import math
import numpy as np
from itertools import pairwise
from random import random
from scipy.spatial import ConvexHull

from window import render
from constants import WIDTH, HEIGHT, PADDING

def get_points(seed):
    number_points = 20
    points = np.empty((number_points, 2))
    np.random.seed(seed)
    points[:, 0] = np.random.randint(PADDING, WIDTH  - PADDING, size=(number_points, ))
    points[:, 1] = np.random.randint(PADDING, HEIGHT - PADDING, size=(number_points, ))
    return points

def dist(a, b):
    return np.linalg.norm(a - b)

def dist2(a, b):
    return dist(a, b) ** 2

def pushApart(polygon):
    import math
    dst = 100 
    dst2 = dst*dst; 
    for i in range(len(polygon)):
        for j in range(i + 1, len(polygon)):
            # print(dist2(polygon[i], polygon[j]), dst2)
            if dist2(polygon[i], polygon[j]) >= dst2:
                continue  
            hx = polygon[j][0] - polygon[i][0]  
            hy = polygon[j][1] - polygon[i][1]  
            hl = math.sqrt(hx*hx + hy*hy)
            hx /= hl
            hy /= hl  
            dif = dst - hl  
            hx *= dif
            hy *= dif  
            polygon[j][0] += hx;  
            polygon[j][1] += hy;  
            polygon[i][0] -= hx;  
            polygon[i][1] -= hy;  

def rotate_via_numpy(xy, radians):
    """Use numpy to build a rotation matrix and take the dot product."""
    # https://gist.github.com/LyleScott/e36e08bfb23b1f87af68c9051f985302
    x, y = xy
    c, s = np.cos(radians), np.sin(radians)
    j = np.matrix([[c, s], [-s, c]])
    m = np.dot(j, [x, y])
    return float(m.T[0]), float(m.T[1])

def nonConvex(polygon):
    rSet = [];  
    disp = [0, 0];  
    difficulty = 1 # the closer the value is to 0, the harder the track should be. Grows exponentially.  
    maxDisp = 100.   # Again, this may change to fit your units.  
    length = polygon.shape[0]
    for i in range(length):  
        dispLen = (random() ** difficulty) * maxDisp 
        disp = rotate_via_numpy([0, 1], random() * 2 * np.pi) 
        disp = (disp / np.linalg.norm(disp)) * dispLen
        newPoint = (polygon[i] + polygon[(i+1) % length]) / 2 + disp
        rSet.append( polygon[i] )
        rSet.append( newPoint )
    return rSet

def add_closest_points(vertices, points):
    polygon = []
    passed = []
    print(points)
    print("=============")
    for v in range(len(vertices) - 1):
        a = vertices[v]
        candidates = np.array([point for i, point in enumerate(points) if i != a and i not in passed])
        indices = np.array([i for i in range(len(points)) if i != a and i not in passed])
        closest = np.linalg.norm(np.abs(candidates - points[a]), axis=1).argmin()
        print(points[a], candidates[closest], points[indices[closest]])
        print("-----------")
        passed.extend((a, indices[closest]))
        polygon.extend((points[a], candidates[closest]))
    polygon.append(points[vertices[-1]])
    return np.array(polygon)

def get_angle(a, b, c):
    ang = math.degrees(math.atan2(c[1]-b[1], c[0]-b[0]) - math.atan2(a[1]-b[1], a[0]-b[0]))
    return ang + 360 if ang < 0 else ang

def drop_angles(points, min_angle=60):
    # Impossible without backtracking (I think)
    prev = points[0]
    polygon = [prev]
    for i in range(1, len(points) - 1):
        a, b, c = prev, points[i], points[i + 1]
        angle = get_angle(a, b, c)
        if angle >= min_angle and angle <= 360 - min_angle:
            polygon.append(b)
        prev = b
    return np.array(polygon)

def divertify(polygon, amplitude=200):
    _polygon = []
    side = 1
    for a, b in pairwise(polygon):
        x = [a[0], b[0]]
        y = [a[1], b[1]]
        between = np.array([0.25, 0.5, 0.75]) # np.sort(np.random.random(3)) # 
        new_x = np.interp(between, [0, 1], x)
        new_y = np.interp(between, [0, 1], y)
        normal = np.array([y[0] - y[1], x[1] - x[0]])
        normal = normal / np.linalg.norm(normal)
        # side = 1 if np.random.random() < 0.5 else -1 # -1 or 1
        deltas = side * amplitude * np.cos( (between - 0.5) * np.pi ) # map to [-pi/2, pi/2] then apply cos
        offsets = np.array([normal * delta for delta in deltas]).T
        middles = np.c_[new_x + offsets[0], new_y + offsets[1]]
        _polygon.extend((a, *middles, b))
        side *= -1
    return _polygon

def cubic_spline(polygon):
    from scipy.interpolate import interp1d
    # Linear length along the line:
    # print(polygon)
    distance = np.cumsum(np.sqrt(np.sum( np.diff(polygon, axis=0)**2, axis=1 )))
    distance = np.insert(distance, 0, 0) / distance[-1]

    # interpolations_methods = ['slinear', 'quadratic', 'cubic']
    alpha = np.linspace(0, 1, 10)
    interpolator = interp1d(distance, polygon, kind='cubic', axis=0)
    return interpolator(alpha)

def interpolate(polygon):
    from scipy.interpolate import interp1d
    x, y = polygon.T
    t = np.arange(len(x))
    ti = np.linspace(0, t.max(), 100 * t.size)
    xi = interp1d(t, x, kind='quadratic')(ti)
    yi = interp1d(t, y, kind='quadratic')(ti)
    return np.c_[xi, yi]

def chaikins_corner_cutting(coords, refinements=3):
    coords = np.copy(coords)
    for _ in range(refinements):
        new_coords = []
        for a, b in pairwise(coords):
            p1 = 3/4 * a + 1/4 * b
            p2 = 1/4 * a + 3/4 * b
            new_coords.extend((p1, p2))
        coords = new_coords
    return coords

if __name__ == '__main__':
    import pygame
    colors = ['yellow', 'orange', 'red', 'blue']

    def generate_track(seed):
        points = get_points(seed)
        
        hull = ConvexHull(points)
        vertices = hull.vertices
        vertices = np.append(vertices, vertices[0])

        polygon = points[vertices]
        polygon2 = divertify(polygon)
        polygon3 = chaikins_corner_cutting(polygon2)
        # polygon2 = divertify(polygon)
        # polygon3 = interpolate(polygon2)
        # polygon3 = drop_angles(polygon2)
        # polygon4 = cubic_spline(polygon3)
        
        # polygons = [polygon2]
        return polygon3

    # line_colors = [pygame.Color(int(np.random.random() * 255), int(np.random.random() * 255), int(np.random.random() * 255)) for _ in range(len(polygon3))]

    seed = 42
    polygon = generate_track(seed)
    active = True

    def cb(screen):
        global polygon, active, seed
        pygame.draw.lines(surface=screen, color='yellow', closed=False, points=polygon, width=5)
        left, _, right = pygame.mouse.get_pressed()
        if left and active:
            print('Regenerating...')
            active = False
            seed += 1
            polygon = generate_track(seed)
        elif right and active:
            print('Regenerating...')
            active = False
            seed -= 1
            polygon = generate_track(seed)
        elif not left and not right and not active:
            active = True
        # for i, polygon in enumerate(polygons):
        #     pygame.draw.lines(surface=screen, color=colors[i], closed=False, points=polygon, width=5)
        # for i, (a, b) in enumerate(pairwise(polygon3)):
        #     color = line_colors[i] # pygame.Color(colors[i], 0, 0)(i / len(polygon3))
        #     pygame.draw.line(surface=screen, color=color, start_pos=a, end_pos=b, width=5)
        # for point in points:
        #     pygame.draw.circle(surface=screen, color='white', center=point, radius=6)

    # polygon2 = nonConvex(polygon)
    # polygon3 = np.copy(polygon2)
    # for _ in range(15):  
    #     pushApart(polygon3)
    render(cb)

