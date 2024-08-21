import numpy as np
import pygame

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
EMERALD = (80, 200, 120)
GREY = (60, 60, 60)
BLACK = (0, 0, 0)

pygame.init()
screen = pygame.display.set_mode((800, 600))

charge_array = np.zeros((600, 600), dtype='float64')
electric_field = np.zeros((600, 600, 2), 'float64')
charge_locations = []

vector_density = 0.04  # Dynamics : 0.04, Statics : 0.16
vector_length = 12  # 12
vector_origin_marker = False  # False
vector_head_marker = True  # True
vec_color_offset = 0  # 0
scaling = 0.1  # Doesnt matter tbh
max_mag = 0
charge_unit = 1e-6
mass = 1e-13  # 1e-5
collision_radius = 8  # 8
grid = True
snap_to_grid = False
trace = True
k = (10 ** 12) / (4 * np.pi * 8.854187817)
dt = 0.0001
dt_original = dt

MIN_R = 99

font_size = 20
font = pygame.font.SysFont("Helvetica",font_size)

# Making class for charges
class Charge:
    def __init__(self, charge, pos, vel, ind):
        # Initialising the object parameters
        self.charge = charge
        self.pos = pos
        self.vel = vel
        self.id = ind
        trace_arr[self.id - 1].append(self.pos)

    # Main update function for dynamic sims
    def update(self, charges):
        global MIN_R

        for charge in charges:
            if charge is not None:
                if self.id < charge.id:
                    # If ids are different, calculate force, acceleration, velocity and position
                    delta_x = self.pos[0] - charge.pos[0]
                    delta_y = self.pos[1] - charge.pos[1]
                    r_2 = delta_x ** 2 + delta_y ** 2
                    if r_2**0.5 < MIN_R:
                        MIN_R = r_2**0.5
                    force = k * self.charge * charge.charge / r_2
                    force_x = force * (delta_x / (r_2 ** 0.5))
                    force_y = force * (delta_y / (r_2 ** 0.5))
                    accel = (force_x / mass, force_y / mass)
                    self.vel = [self.vel[0] + accel[0]*dt, self.vel[1] + accel[1]*dt]
                    charge.vel = [charge.vel[0]-accel[0]*dt,charge.vel[1]-accel[1]*dt]
                    charge.pos = (charge.pos[0] + charge.vel[0]*dt,charge.pos[1]+charge.vel[1]*dt)
                    self.pos = (self.pos[0] + self.vel[0]*dt, self.pos[1] + self.vel[1]*dt)


        # Removes the charge if it goes out of bounds
        if not (0 <= self.pos[0] <= 600) or not (0 <= self.pos[1] <= 600):
            charge_obj_arr[self.id - 1] = None
        trace_arr[self.id - 1].append(self.pos)

        # Checks for collision (As of right now it can only handle unlike charge collision)
        for charge in charges:
            if charge is not None:
                if self.id != charge.id:
                    delta_x = self.pos[0] - charge.pos[0]
                    delta_y = self.pos[1] - charge.pos[1]
                    r = np.sqrt(delta_x ** 2 + delta_y ** 2)
                    delta_x_next = delta_x + self.vel[0]*dt - charge.vel[0]*dt
                    delta_y_next = delta_y + self.vel[1]*dt - charge.vel[1]*dt
                    r_next = np.sqrt(delta_x_next ** 2 + delta_y_next ** 2)
                    if r <= collision_radius or r_next<=collision_radius:
                        self.charge += charge.charge
                        self.vel[0] += charge.vel[0]
                        self.vel[1] += charge.vel[1]
                        charge_obj_arr[charge.id - 1] = None
                        if self.charge == 0:
                            charge_obj_arr[self.id - 1] = None


# Updates the charge array
def update_array(charges):
    charge_array = np.zeros((600, 600), dtype='float64')
    charge_locations = []
    for charge in charges:
        if charge is not None:
            charge_array[int(charge.pos[0]), int(charge.pos[1])] = charge.charge
            charge_locations.append(charge.pos)

    return charge_array, charge_locations


# Calculates electric field
def calculate_vector_field(charges, vector_density):
    global scaling, charge_locations
    electric_field = np.zeros((600, 600, 2))
    vector_spacing = int(1 / vector_density)
    x, y = charges.shape
    max_magnitude = 0

    for i in range(x):
        for j in range(y):
            if (charges[i, j] == 0) and (i % vector_spacing == 0) and (j % vector_spacing == 0):
                vector = [0, 0]
                for charge_pos in charge_locations:
                    x1, y1 = (int(charge_pos[0]), int(charge_pos[1]))
                    q = charges[x1, y1]
                    dist = np.sqrt(((i - x1) * scaling) ** 2 + ((j - y1) * scaling) ** 2)
                    vector[0] += k * q * (i - x1) * scaling / (dist ** 3)
                    vector[1] += k * q * (j - y1) * scaling / (dist ** 3)
                electric_field[i, j, 0], electric_field[i, j, 1] = vector
                magnitude = np.sqrt(vector[0] ** 2 + vector[1] ** 2)
                if magnitude > max_magnitude:
                    max_magnitude = magnitude

    return electric_field, max_magnitude


# Normalises a vector to a unit vector
def normalize(v):
    norm = np.linalg.norm(v)
    if norm == 0:
        return v
    return v / norm


# Draws the vectors
def draw_vec(vector, vector_pos, max_mag):
    direction = normalize(vector)
    magnitude = np.sqrt(vector[0] ** 2 + vector[1] ** 2)
    vector_end = [vector_pos[0] + vector_length * direction[0], vector_pos[1] + vector_length * direction[1]]
    pygame.draw.line(screen, (vec_color_offset + (255 - vec_color_offset) * (magnitude / max_mag) ** 0.15, 0, 0),
                     vector_pos, vector_end, 3)
    if vector_origin_marker:
        pygame.draw.circle(screen, BLUE, vector_pos, 1)
    if vector_head_marker:
        pygame.draw.circle(screen, EMERALD, vector_end, 1)

def draw_rect(topleft_pos, size, fill=False):
    x,y = topleft_pos
    if fill:
        pygame.draw.rect(screen,WHITE,pygame.Rect((x,y),(size,size)),width=size)
    else:
        pygame.draw.rect(screen,WHITE,pygame.Rect((x,y),(size,size)),width=1)

def draw_options_bar():
    global font, font_size,charge_unit_text,option_arr
    global bottom_line
    option_text_arr = ["Paused(P)", "Visual grid(G)", "Snap-to-grid(S)","Trace(T)","Vectors(V)"]
    screen.blit(font.render(" ͟O͟pt͟i͟o͟n͟s͟",True,WHITE),(660,10))
    for i in range(len(option_text_arr)):
        screen.blit(font.render(option_text_arr[i],True,WHITE),(620,int(40+i*font_size*8/5)))
        draw_rect((760, int(40 + i * font_size * 8 / 5)), font_size, fill=option_arr[i])

    screen.blit(font.render("q =                   μC",True,WHITE),(620,bottom_line))
    charge_text = font.render(charge_unit_text,True,WHITE)
    charge_text_rect = charge_text.get_rect(center=(705,bottom_line+font_size-10))
    screen.blit(charge_text,charge_text_rect)
    pygame.draw.line(screen,WHITE,(600,bottom_line-20),(800,bottom_line-20))
    pygame.draw.line(screen,WHITE,(660,bottom_line+font_size),(750,bottom_line+font_size))




# Main draw function
def draw(electric_field, vector_density, max_mag):
    global charge_array, option_arr
    vector_spacing = int(1 / vector_density)
    x, y, _ = electric_field.shape
    # Draws the grid, charges and vectors
    for i in range(x):
        for j in range(y):
            if i % vector_spacing == 0:
                if grid : pygame.draw.line(screen, GREY, (0, i), (600, i))
                if j % vector_spacing == 0:
                    if grid : pygame.draw.line(screen, GREY, (j, 0), (j, 600))
                    if not (electric_field[i, j, 0] == 0 and electric_field[i, j, 1] == 0):
                        if vectors : draw_vec(electric_field[i, j], [i, j], max_mag)

            if charge_array[i, j] != 0:
                if charge_array[i, j] > 0:
                    pygame.draw.circle(screen, (255, 170, 51), (i, j), 3)
                if charge_array[i, j] < 0:
                    pygame.draw.circle(screen, (0, 150, 255), (i, j), 3)
    pygame.draw.line(screen,WHITE,(600,0),(600,600),2)

    # Draws the pause/play icon
    if paused:
        screen.blit(pause_img, (530, 20))
    else:
        screen.blit(play_img, (540, 25))

    # Draws the path traced by charges
    if trace:
        for index, trace_row in enumerate(trace_arr):
            if len(trace_row) > 1:
                color_value = 100 + 155 * index / len(trace_arr)
                color = (color_value, color_value, color_value)
                pygame.draw.lines(screen, color, False, trace_row, 2)

    draw_options_bar()


running = True
update = True
static = False
paused = True
vectors = True
charge_obj_arr = []
updated_charge = 0
index = 0
mouse_pos = None
trace_arr = []

setting_charge = False
charge_unit_text = "1"

clock = pygame.time.Clock()
FPS = 30

option_arr = [paused,grid,snap_to_grid,trace,vectors]
bottom_line = int(40+len(option_arr)*font_size*8/5) + 20

play_img = pygame.image.load("play_icon.png").convert_alpha()
play_img = pygame.transform.scale(play_img, (30, 40))
pause_img = pygame.image.load("pause_icon.png").convert_alpha()
pause_img = pygame.transform.scale(pause_img, (50, 50))

print("""
Options:
    Q/LMB : Places +1μC charge
    E : Places -1μC charge
    C : Clears everything
    P : Pauses/Plays the simulation (Default: Paused)
    V : Toggles field vectors (Default: Enabled)
    G : Toggles visual grid (Default: Enabled)
    S : Toggles snap to grid (Default: Disabled)
    T : Toggles tracing (Default : Enabled)""")

while running:
    clock.tick(FPS)
    screen.fill((0, 0, 0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if setting_charge:
                if event.key == pygame.K_BACKSPACE:
                    charge_unit_text = charge_unit_text[:-1]
                elif event.key == pygame.K_RETURN:
                    if len(charge_unit_text)>=1:
                        charge_unit = float(charge_unit_text) * 1e-6
                    setting_charge = False
                else:
                    charge_unit_text += event.unicode
            else:
                if event.key == pygame.K_q:
                    update = True
                    mouse_pos = pygame.mouse.get_pos()
                    if mouse_pos[0]<=600:
                        if snap_to_grid:
                            vector_spacing = int(1 / vector_density)
                            mouse_pos = (int(np.round(mouse_pos[0] / vector_spacing) * vector_spacing),
                                         int(np.round(mouse_pos[1] / vector_spacing) * vector_spacing))
                        charge_array[mouse_pos[0], mouse_pos[1]] += charge_unit
                        charge_locations.append(mouse_pos)
                        updated_charge = charge_unit
                        trace_arr.append([])
                if event.key == pygame.K_e:
                    update = True
                    mouse_pos = pygame.mouse.get_pos()
                    if mouse_pos[0]<=600:
                        if snap_to_grid:
                            vector_spacing = int(1 / vector_density)
                            mouse_pos = (int(np.round(mouse_pos[0] / vector_spacing) * vector_spacing),
                                         int(np.round(mouse_pos[1] / vector_spacing) * vector_spacing))
                        charge_array[mouse_pos[0], mouse_pos[1]] -= charge_unit
                        charge_locations.append(mouse_pos)
                        updated_charge = -1 * charge_unit
                        trace_arr.append([])
                if event.key == pygame.K_p:
                    paused = not paused
                    option_arr[0] = not option_arr[0]
                if event.key == pygame.K_g:
                    grid = not grid
                    option_arr[1] = not option_arr[1]
                if event.key == pygame.K_s:
                    snap_to_grid = not snap_to_grid
                    option_arr[2] = not option_arr[2]
                if event.key == pygame.K_t:
                    trace = not trace
                    option_arr[3] = not option_arr[3]
                if event.key == pygame.K_v:
                    vectors = not vectors
                    option_arr[4] = not option_arr[4]
                if event.key == pygame.K_x:
                    if dt == dt_original:
                        dt = 2*dt_original
                    else:
                        dt = dt_original
                if event.key == pygame.K_c:
                    trace_arr = []
                    charge_obj_arr = []
                    charge_array = np.zeros((600, 600), dtype='float64')
                    electric_field = np.zeros((600, 600, 2), 'float64')
                    index = 0

        if event.type == pygame.MOUSEBUTTONDOWN:
            update = True
            mouse_pos = pygame.mouse.get_pos()
            if mouse_pos[0]<=600:
                if snap_to_grid:
                    vector_spacing = int(1 / vector_density)
                    mouse_pos = (int(np.round(mouse_pos[0] / vector_spacing) * vector_spacing),
                                 int(np.floor(mouse_pos[1] / vector_spacing) * vector_spacing))
                charge_array[mouse_pos[0], mouse_pos[1]] += charge_unit
                charge_locations.append(mouse_pos)
                updated_charge = charge_unit
                trace_arr.append([])
            else:
                if (750>mouse_pos[0]>660) and (bottom_line+font_size>mouse_pos[1]>bottom_line-font_size):
                    charge_unit_text = ""
                    setting_charge = True
                mouse_pos = None
    if not static:
        if update and mouse_pos is not None:
            index += 1
            charge_obj_arr.append(Charge(updated_charge, mouse_pos, [0, 0], index))
        if not paused:
            for charge in charge_obj_arr:
                if charge is not None:
                    charge.update(charge_obj_arr)
            if len(charge_obj_arr) > 0:
                charge_array, charge_locations = update_array(charge_obj_arr)

        update = True
    if update:
        electric_field, max_mag = calculate_vector_field(charge_array, vector_density)
        draw(electric_field, vector_density, max_mag)
        pygame.display.update()
        update = False
    mouse_pos = None
pygame.quit()
