#!/usr/bin/env python
#-*-coding:utf-8-*-


import json
from random import randint

# 棋盘 15 * 15
SIZE = 15
# 己方棋子颜色 1, 对手棋子颜色 -1
SELF, OPPONENT = 1, -1

def build_grid_view(reqs, rsps):
    '''
    根据 reqs、rsps，标记棋盘布局 grid，统计已下的子数 count
    '''
    grid = [[0 for x in range(SIZE)] for y in range(SIZE)]
    count = 0
    # 排除 {"x":-1,"y":-1}，
    for req in reqs:
        if req['x'] > -1:
            grid[req['x']][req['y']] = OPPONENT
            count += 1
    for rsp in rsps:
        if rsp['x'] > -1:
            grid[rsp['x']][rsp['y']] = SELF
            count += 1

    # 己方持黑，对方换手
    if len(reqs) > 2 and reqs[2]['x'] == -1:
        grid[reqs[1]['x']][reqs[1]['y']] = SELF
        grid[rsps[0]['x']][rsps[0]['y']] = OPPONENT
        grid[rsps[1]['x']][rsps[1]['y']] = OPPONENT

    # 己方持白，主动换手
    if len(rsps) > 1 and rsps[1]['x'] == -1:
        grid[reqs[0]['x']][reqs[0]['y']] = SELF
        grid[reqs[1]['x']][reqs[1]['y']] = SELF
        grid[rsps[0]['x']][rsps[0]['y']] = OPPONENT

    return grid, count

# 方向向量 direction vector
#            (0,1)
#   (-1,1) \   |   /(1,1)
#            \ | /
# (-1,0) ------|------ (1,0)
#            / | \
#  (-1,-1) /   |   \ (1,-1)
#           (0,-1)

# 横竖撇捺 四个方向
DVS = (
    (0,   1),# 上; (0,  -1),# 下
    (1,   0),# 右; (-1,  0),# 左
    (1,   1),# 右上; (-1, -1),# 左下
    (1,  -1) # 右下; (-1,  1),# 左上
)

def in_grid(x, y):
    '''
    坐标是否落在棋盘范围
    '''
    return 0 <= x < SIZE and 0 <= y < SIZE

# 每个连珠的级别分
GRADE = 10

def eval_dv(grid, color, m, n, dv):
    '''
    在 x, y 点的某个方向上做出评估，返回 stars, score
    '''
    # stars - 顺、反方向一起的连珠
    stars = 0
    # 连珠后是否是活手: 活手为 1 分，否则 -1 分
    live = [-1, -1]
    # 顺、反方向最近的堵点(连珠后是越界或对手子)
    block_pts = [(0, 0), (SIZE-1, SIZE-1)]

    # 顺、反方向分别用 1、-1 表示
    for i,v in enumerate([1, -1]):
        # 顺、反方向，一开始要重置 x, y 为 m, n
        x, y = m, n
        # 顺、反方向，方向向量
        dx, dy = v*dv[0], v*dv[1]

        # 计算连珠数
        x, y = x + dx, y + dy # 步进 x, y = [p+d for p,d in zip((x, y), (dx, dy))]
        while in_grid(x, y) and grid[x][y] == color:
            stars += 1
            x, y = x + dx, y + dy

        # 连珠后是否是活手
        live[i] = 1 if in_grid(x, y) and grid[x][y] == 0 else -1
        # 找到最近的堵点
        while in_grid(x, y) and grid[x][y] == 0:
            x, y = x + dx, y + dy
        block_pts[i] = (x, y)

    distance = max(abs(block_pts[1][0] - block_pts[0][0]), abs(block_pts[1][1] - block_pts[0][1]))
    if distance < 6:
        stars = 0 # 不能容纳五连珠，连珠没有意义，置为 0

    return stars, stars * GRADE + sum(live)

def eval_point(grid, color, x, y):
    '''
    在 x, y 点的横竖撇捺四个方向上做出评估，并降序排序
    '''
    score_dvs = [0 for i in range(len(DVS))]
    for i, dv in enumerate(DVS):
        stars, score = eval_dv(grid, color, x, y, dv)
        score_dvs[i] = {'stars': stars, 'score': score}
    # 先根据 stars，再根据 score 降序排序
    score_dvs.sort(key=lambda e:(e['stars'], e['score']), reverse=True)
    return score_dvs

def eval_shape(grid, color):
    '''
    评估整个棋盘的形势：扫描棋盘上的每一个空子，在空子的横竖撇捺四个方向上做出评估
    '''
    shape = [[None for x in range(SIZE)] for y in range(SIZE)]
    for x in range(SIZE):
        for y in range(SIZE):
            if grid[x][y] == 0:
                shape[x][y] = eval_point(grid, color, x, y)
    return shape

# 最大分
MAX = 999999999

def evaluate(shape):
    '''
    计算落子在哪个空子点，能得到最大分
    '''
    max_x, max_y, max = -1, -1, -MAX
    for x in range(SIZE):
        for y in range(SIZE):
            # 空子，才会参与形势评估
            if not shape[x][y]:
                continue
            # 已经四连珠，直接下子
            if shape[x][y][0]['stars'] == 4:
                return x, y, MAX
            # 横竖撇捺 四个方向，都参与计算，得出该子对整体棋局的影响值
            ss = shape[x][y]
            total = ss[0]['score'] * 1000 + ss[1]['score'] * 100 + ss[2]['score'] * 10 + ss[3]['score'] 
            if max < total:
                max, max_x, max_y = total, x, y
    return max_x, max_y, max

def ai_play(grid):
    '''
    计算己方落子形势、对手落子形势，返回得分最高的下子坐标
    对手与己方形势相同，优先进攻
    '''
    # 计算己方落子形势、对手落子形势
    shape_attack = eval_shape(grid, SELF)
    shape_defend = eval_shape(grid, OPPONENT)
    max_x_a, max_y_a, max_a = evaluate(shape_attack)
    max_x_d, max_y_d, max_d = evaluate(shape_defend)
    # 进攻形势、防守形势比较（形势相同，优先进攻）
    if max_a >= max_d:
        return max_x_a, max_y_a
    else:
        return max_x_d, max_y_d

def random_play(grid):
    '''
    随机下子
    '''
    while True:
        x, y = randint(0, SIZE-1), randint(0, SIZE-1)
        if grid[x][y] == 0:
            return x, y

# 棋盘边界
EDGE_POINTS = [0, SIZE-1]

def edge_play(grid):
    '''
    落子在棋盘边界
    '''
    x = EDGE_POINTS[randint(0, 1)]
    for y in range(SIZE):
        if grid[x][y] == 0:
            break
    return (x, y) if randint(0, 1) == 0 else (y, x)

def is_edge_trap(steps):
    '''
    是否故意设置陷阱：所有子都下在棋盘边缘
    '''
    for step in steps:
        if step['x'] not in EDGE_POINTS and step['y'] not in EDGE_POINTS:
            return False
    return True


def main():
    src = input()
    # src = '{"requests":[{"x":11,"y":10},{"x":12,"y":10}],"responses":[{"x":10,"y":12}]}'

    in_data = json.loads(src)
    reqs, rsps = in_data["requests"], in_data["responses"]

    # 黑棋的第一回合，request 为 {"x": -1, "y": -1}
    role = 'BLACK' if reqs[0]['x'] == -1 else 'WHITE'
    grid, count = build_grid_view(reqs, rsps)

    if role == 'WHITE' and count == 3:
        if is_edge_trap(reqs[0:1]):# 对手故意设置陷阱，两子都下在棋盘边界，不换手
            x, y = ai_play(grid)
        else:# 否则换手
            x, y = -1, -1
    elif count < 3:
        if role == 'WHITE':# 持白，第一子主动下在边缘位置
            x, y = edge_play(grid)
        else:# 持黑，前两子随机下
            x, y = random_play(grid)
    else:
        x, y = ai_play(grid)

    # 标准输出下子坐标
    print(json.dumps({"response":{ "x":x, "y":y}}))


main()
