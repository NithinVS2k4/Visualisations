import numpy as np
from scipy.integrate import odeint
import sympy as sm

import pygame

pygame.init()
screen = pygame.display.set_mode((600, 600))
FPS = 30

t = sm.symbols('t')
m1, m2, g = sm.symbols('m1 m2 g', positive=True)
the1, the2 = sm.symbols(r'\theta_1, \theta_2', cls=sm.Function)

the1 = the1(t)
the2 = the2(t)

x1 = sm.sin(the1)
y1 = -sm.cos(the1)

x2 = x1 + sm.sin(the2)
y2 = y1 - sm.cos(the2)

the1_d = sm.diff(the1, t)
the1_dd = sm.diff(the1_d, t)

x1_d = sm.diff(x1, t)
y1_d = sm.diff(y1, t)

the2_d = sm.diff(the2, t)
the2_dd = sm.diff(the2_d, t)

x2_d = sm.diff(x2, t)
y2_d = sm.diff(y2, t)

T_1 = 0.5 * m1 * (x1_d ** 2 + y1_d ** 2)
T_2 = 0.5 * m2 * (x2_d ** 2 + y2_d ** 2)

V_1 = m1 * g * y1
V_2 = m2 * g * y2

L = T_1 + T_2 - (V_1 + V_2)

LE1 = sm.diff(sm.diff(L, the1_d), t) - sm.diff(L, the1)
LE2 = sm.diff(sm.diff(L, the2_d), t) - sm.diff(L, the2)

LE1 = LE1.simplify()
LE2 = LE2.simplify()

solutions = sm.solve([LE1, LE2], the1_dd, the2_dd)

LEF1 = sm.lambdify((the1, the2, the1_d, the2_d, t, m1, m2, g), solutions[the1_dd])
LEF2 = sm.lambdify((the1, the2, the1_d, the2_d, t, m1, m2, g), solutions[the2_dd])

initial_conditions = [1.0, 0.0, 2.0, 0.0]
m1_val = 1
m2_val = 1.5
g_val = 9.81


def sys_of_odes(y, t, m1, m2, g):
    the1, the1_d, the2, the2_d = y

    the1_dd = LEF1(the1, the2, the1_d, the2_d, t, m1, m2, g)
    the2_dd = LEF2(the1, the2, the1_d, the2_d, t, m1, m2, g)

    return [the1_d, the1_dd, the2_d, the2_dd]


time_period = 30
time_points = np.linspace(0, time_period, FPS * time_period)


def get_sol(sol):
    x1_pend = np.sin(sol[:, 0])
    y1_pend = -np.cos(sol[:, 0])
    x2_pend = x1_pend + np.sin(sol[:, 2])
    y2_pend = y1_pend - np.cos(sol[:, 2])

    return (x1_pend, y1_pend, x2_pend, y2_pend)


# Gives 2D array of y vector at different time points
solution = odeint(sys_of_odes, initial_conditions, time_points, args=(m1_val, m2_val, g_val))

the1_sol = solution[:, 0]
the1_d_sol = solution[:, 1]
the2_sol = solution[:, 2]
the2_d_sol = solution[:, 3]

x1_pend = np.sin(the1_sol)
y1_pend = -np.cos(the1_sol)
x2_pend = x1_pend + np.sin(the2_sol)
y2_pend = y1_pend - np.cos(the2_sol)

init_condn_arr = []
traced_points_arr = []
hue_arr = []

automate = True
if automate:
    num_of_pends = 100
    offset = 1e-9
    for k in range(num_of_pends):
        init_condn_arr.append([1.0, 0.0, 2.0 + k * offset, 0.0])
        traced_points_arr.append([])
        hue_arr = np.linspace(250, 290, num_of_pends)
else:
    init_condn_arr = [[1.0, 0.0, 2.0, 0.0], [1.0, 0.0, 2.00000001, 0.0], [1.0, 0.0, 2.00000002, 0.0]]
    traced_points_arr = [[], [], []]
    hue_arr = [360, 240, 120]

traced_points_arr_empty = traced_points_arr

solution_arr = []
point_arr = []


for p in range(len(init_condn_arr)):
    solution_arr.append(odeint(sys_of_odes, init_condn_arr[p], time_points, args=(m1_val, m2_val, g_val)))
    screen.fill((0,0,0))
    pygame.draw.rect(screen, (255, 255, 255), (200, 280, 200, 40), width=3)
    pygame.draw.rect(screen, (0, 255, 0), (203, 283, 194 * (p + 1) / len(init_condn_arr), 34))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
    pygame.display.update()

for p in range(len(solution_arr)):
    point_arr.append(get_sol(solution_arr[p]))

color = pygame.Color((255, 255, 255))
color.hsla = (0, 80, 50, 100)

rgb = False
rgb_rate = 0.5


def draw(i, double_pend_points, q):
    global traced_points

    x1_pen, y1_pen, x2_pen, y2_pen = double_pend_points

    l = 150
    r1 = 5 * int(m1_val ** (1 / 3))
    r2 = 5 * int(m2_val ** (1 / 3))

    suspension = (300, 100)

    x1 = suspension[0] + l * x1_pen
    x2 = suspension[0] + l * x2_pen
    y1 = suspension[1] - l * y1_pen
    y2 = suspension[1] - l * y2_pen

    bob1_pos = (x1[i], y1[i])
    bob2_pos = (x2[i], y2[i])
    traced_points_arr[q].append([x2[i], y2[i]])

    pygame.draw.line(screen, (255, 255, 255), suspension, bob1_pos, 2)
    pygame.draw.line(screen, (255, 255, 255), bob1_pos, bob2_pos, 2)

    if i > 1:
        if rgb:
            color.hsla = ((i * rgb_rate) % 360, 80, 50, 10)
        else:
            color.hsla = (hue_arr[q], 80, 50, 10)
        pygame.draw.lines(screen, color, False, traced_points_arr[q], 2)

    pygame.draw.circle(screen, (255, 0, 0), bob1_pos, r1)
    pygame.draw.circle(screen, (0, 0, 255, 20), bob2_pos, r2)


running = True
clock = pygame.time.Clock()
frame = 0
diffusion_time = 0.5

while running:
    clock.tick(FPS)
    screen.fill((0, 0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    for q in range(len(point_arr)):
        draw(frame, point_arr[q], q)

    frame += 1

    if frame / FPS > diffusion_time:
        for traced_points in traced_points_arr:
            traced_points.pop(0)

    if frame >= FPS * time_period:
        frame = 0
        traced_points_arr = traced_points_arr_empty

    pygame.display.update()

pygame.quit()
