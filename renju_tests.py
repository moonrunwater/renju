#!/usr/bin/env python
#-*-coding:utf-8-*-

import json
from random import randint

import renju

def test_play():
    grid = [[0 for x in range(renju.SIZE)] for y in range(renju.SIZE)]
    for i in range(100):
        x, y = renju.edge_play(grid)
        print("=====", i, (x, y))
    for i in range(100):
        x, y = renju.random_play(grid)
        print("=====", i, (x, y))
    for i in range(20):
        steps = [{'x':x, 'y':y} for x, y in [renju.edge_play(grid) for i in range(2)]]
        print("=====", i, steps)
        if renju.is_edge_trap(steps):
            print("!!!!! edge_trap")
    for i in range(100):
        steps = [{'x':x, 'y':y} for x, y in [renju.random_play(grid) for i in range(2)]]
        print("=====", i, steps)
        if renju.is_edge_trap(steps):
            print("!!!!! edge_trap")

def test_eval():
    src = '{"requests":[{"x":-1,"y":-1},{"x":6,"y":0},{"x":-1,"y":-1},{"x":4,"y":2},{"x":2,"y":2},{"x":4,"y":0},{"x":6,"y":1},{"x":2,"y":1},{"x":2,"y":3}],"responses":[{"x":1,"y":12},{"x":1,"y":9},{"x":5,"y":1},{"x":3,"y":3},{"x":5,"y":0},{"x":4,"y":1},{"x":3,"y":1},{"x":3,"y":2}]}'
    in_data = json.loads(src)
    reqs, rsps = in_data["requests"], in_data["responses"]
    grid, count = renju.build_grid_view(reqs, rsps)
    print(count)
    renju.eval_point(grid, renju.SELF, 3, 0)
    renju.eval_dv(grid, renju.SELF, 3, 4, (0, 1))

def test():
    x, y = 9, 9
    x, y = [i+j for i,j in zip((x, y), (1, -1))]
    print(x, y)
    x, y = (i+j for i,j in zip((x, y), (1, -1)))
    print(x, y)
    x, y = (i*j for i,j in zip((x, y), (1, -1)))
    print(x, y)
    print([-1 * i for i in (1, -1)])

    x, y = [7, 4]
    print(x, y)

    lst1 = [11, 10, 3, 19]
    print(sorted(lst1, reverse=True))
    print(lst1)

    lst2 = [11, 10, 3, 19]
    print(lst2.sort(reverse=True))
    print(lst2)

    print(sum([1, 3, 5]))

    block_pts = [(0, 0), (-12, 13)]
    distance = max(abs(block_pts[1][0] - block_pts[0][0]), abs(block_pts[1][1] - block_pts[0][1]))
    print(distance)


if __name__ == "__main__":    
    # test()
    test_eval()
