import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.animation import FFMpegWriter

plt.rcParams['animation.ffmpeg_path'] = "/Users/nithin/Desktop/ffmpeg"

fig, ax = plt.subplots()
path, = ax.plot([], [], 'k-')

metadata = dict(title='Projectile Motion', artist='Nithin V Shenoy')
writer = FFMpegWriter(fps=30, metadata=metadata)

class Projectile():
    def __init__(self, pos, speed, angle, time_period, dt):
        self.speed = speed
        self.pos = pos
        self.init_angle = angle
        self.x_history = [self.pos[0]]
        self.y_history = [self.pos[1]]
        self.pos_max = pos.copy()
        self.pos_min = pos.copy()
        self.vel = [speed * np.cos(angle * np.pi / 180), speed * np.sin(angle * np.pi / 180)]
        self.accel = [0, -9.81]
        self.time_period = time_period
        self.time = 0
        self.deltaTime = dt

    def update(self):
        self.pos[0] += self.vel[0] * self.deltaTime
        self.pos[1] += self.vel[1] * self.deltaTime
        self.vel[0] += self.accel[0] * self.deltaTime
        self.vel[1] += self.accel[1] * self.deltaTime
        self.time += self.deltaTime
        self.x_history.append(self.pos[0])
        self.y_history.append(self.pos[1])
        if (self.pos[1] > self.pos_max[1]):
            self.pos_max = self.pos.copy()
        if self.pos[1] < self.pos_min[1]:
            self.pos_min = self.pos.copy()

proj1 = Projectile([0, 0], 20, 30, 5, 1 / writer.fps)

max_frame = proj1.time_period * writer.fps
frame = 1

with writer.saving(fig, "Animations/projectileMotion.mp4", 200):
    while frame <= max_frame:
        path.set_data(proj1.x_history, proj1.y_history)
        proj1.update()
        ax.relim()
        ax.autoscale()
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()

        y_interval = ylim[1] - ylim[0]
        x_interval = xlim[1] - xlim[0]

        if (y_interval>=x_interval):
            plt.xlim(xlim[0],xlim[0]+y_interval)
        if(x_interval> y_interval):
            plt.ylim(ylim[0],ylim[0]+x_interval)
        writer.grab_frame()
        frame += 1

    # Plot dashed lines for max and min heights at the end of the animation
    ax.plot([0, proj1.pos_max[0]], [proj1.pos_max[1], proj1.pos_max[1]], 'r--',linewidth=0.85)
    ax.plot([0, proj1.pos_min[0]], [proj1.pos_min[1], proj1.pos_min[1]], 'r--',linewidth=0.85)
    ax.plot([0,ax.get_xlim()[1]],[0,0],'k--',linewidth=0.85)
    plt.text(proj1.pos_max[0],proj1.pos_max[1],f"{round(proj1.pos_max[1],2)} m",horizontalalignment='center', verticalalignment='bottom')
    plt.text(proj1.pos_min[0],proj1.pos_min[1],f"{round(proj1.pos_min[1],2)} m",horizontalalignment='center', verticalalignment='top')
    ax.plot([0,ax.get_xlim()[1]*0.1],[0,ax.get_xlim()[1]*0.1*np.tan(proj1.init_angle*np.pi/180)],'b--',linewidth=0.75)

    if (y_interval>=x_interval):
        plt.xlim(0,y_interval)
        plt.ylim(proj1.pos_min[1],proj1.pos_min[1]+y_interval)
    if(x_interval> y_interval):
        plt.xlim(0,x_interval)
        plt.ylim(proj1.pos_min[1],proj1.pos_min[1]+x_interval)

    radius = 0.05*ax.get_xlim()[1]
    arc = patches.Arc((0,0),2*radius,2*radius,angle=0,theta1=0,theta2=proj1.init_angle,linewidth=1)
    ax.add_patch(arc)
    plt.text(radius*np.cos(proj1.init_angle*np.pi/360),0,f"{proj1.init_angle}°",horizontalalignment='left',fontsize=6,verticalalignment='bottom')

    writer.grab_frame()
