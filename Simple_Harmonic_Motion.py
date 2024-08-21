import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FFMpegWriter
import matplotlib.patches as patches
import matplotlib.transforms as transforms
import time

plt.rcParams['animation.ffmpeg_path'] = '/Users/nithin/Desktop/ffmpeg'

metadata = dict(title='SHM Animation', artist='Nithin V Shenoy')
writer = FFMpegWriter(fps=30, metadata=metadata)

fig,axes = plt.subplots(nrows=3,ncols=2,figsize=(9,9))
ax = axes[0,0]
pos_ax = axes[0,1]
vel_ax = axes[1,1]
acc_ax = axes[2,1]

ax.set_position([0.1,0.1,0.4,0.8])
axes[1,0].set_axis_off()
axes[2,0].set_axis_off()

class SHM():
    def __init__(self,mass,k,l,suspension,pos,vel,time_period,dt,damping = 0):
        self.mass = mass
        self.k = k
        self.l = l
        self.suspension = suspension.copy()
        self.pos = pos.copy()
        self.vel = vel.copy()
        self.r = ((self.pos[0]-self.suspension[0])**2 + (self.pos[1]-self.suspension[1])**2)**0.5
        self.damping = damping
        self.g = (0,-9.81)
        self.accel = []
        self.theta = np.arctan2(self.pos[0]-self.suspension[0],self.suspension[1]-self.pos[1])

        self.pos_hstry = [[],[]]
        self.vel_histry = [[],[]]
        self.acc_histry = [[],[]]

        self.time = 0
        self.time_period = time_period
        self.deltaTime = dt

    def update(self):
        self.accel = [self.g[0]-self.k*np.sin(self.theta)*(self.r-self.l)/self.mass,self.g[1]+self.k*np.cos(self.theta)*(self.r-self.l)/self.mass]
        self.vel[0] += self.accel[0]*self.deltaTime
        self.vel[1] += self.accel[1]*self.deltaTime
        self.pos[0] += self.vel[0]*self.deltaTime
        self.pos[1] += self.vel[1]*self.deltaTime

        self.pos_hstry[0].append(self.pos[0])
        self.pos_hstry[1].append(self.pos[1])
        self.vel_histry[0].append(self.vel[0])
        self.vel_histry[1].append(self.vel[1])
        self.acc_histry[0].append(self.accel[0])
        self.acc_histry[1].append(self.accel[1])

        self.time += self.deltaTime
        self.r = ((self.pos[0]-self.suspension[0])**2 + (self.pos[1]-self.suspension[1])**2)**0.5
        self.theta = np.arctan2(self.pos[0]-self.suspension[0],self.suspension[1]-self.pos[1])

shm = SHM(5,7,50,[50,0],[20,-50],[0,-10],10,8/writer.fps)
max_frames = writer.fps*shm.time_period
x_lim_min,x_lim_max,y_lim_min,y_lim_max = (999,-999,999,-999)
frame = 1
spring_img = plt.imread('Images/Spring_vertical_bgremoved.png')
spring_ax = ax.imshow(spring_img, extent=[shm.suspension[0]-8, shm.suspension[0]+8, shm.pos[1], shm.suspension[1]])
start = time.time()
with writer.saving(fig, "Animations/SHM.mp4", 200):
    while(frame<=max_frames):
        shm.update()
        circle = patches.Circle(shm.pos,2)
        ax.add_patch(circle)
        if(frame%10 == 0):
            print(f"{round(100*frame/max_frames,2)}% done")
        transform = transforms.Affine2D().rotate_around(shm.suspension[0], shm.suspension[1], shm.theta)
        spring_ax.set_extent([shm.suspension[0] - 8, shm.suspension[0] + 8, shm.suspension[1]-shm.r, shm.suspension[1]])
        spring_ax.set_transform(transform + ax.transData)

        pos_ax.clear()
        vel_ax.clear()
        acc_ax.clear()

        pos_ax.plot(shm.pos_hstry[0],shm.pos_hstry[1],'k-')
        vel_ax.plot(shm.vel_histry[0],shm.vel_histry[1],'b-')
        acc_ax.plot(shm.acc_histry[0],shm.acc_histry[1],'g-')

        ax.relim()
        ax.autoscale()
        for axis in axes.flatten():
            axis.relim()
            axis.autoscale()

        # Add abscissa and ordinate lines to pos_ax plot
        pos_ax.axhline(y=0, color='k', linewidth=0.5)  # Draw horizontal line at y=0
        pos_ax.axvline(x=0, color='k', linewidth=0.5)  # Draw vertical line at x=0

        # Add abscissa and ordinate lines to vel_ax plot
        vel_ax.axhline(y=0, color='k', linewidth=0.5)  # Draw horizontal line at y=0
        vel_ax.axvline(x=0, color='k', linewidth=0.5)  # Draw vertical line at x=0

        # Add abscissa and ordinate lines to acc_ax plot
        acc_ax.axhline(y=0, color='k', linewidth=0.5)  # Draw horizontal line at y=0
        acc_ax.axvline(x=0, color='k', linewidth=0.5)  # Draw vertical line at x=0

        xlim = ax.get_xlim()
        ylim = ax.get_ylim()

        if(xlim[0]<x_lim_min):
            x_lim_min = xlim[0]
        if(xlim[1]>x_lim_max):
            x_lim_max = xlim[1]
        if(ylim[0]<y_lim_min):
            y_lim_min = ylim[0]
        if(ylim[1]>y_lim_max):
            y_lim_max = ylim[1]

        ax.set_xlim(x_lim_min,x_lim_max)
        ax.set_ylim(y_lim_min,y_lim_max)

        ax.set_aspect(1)
        frame += 1
        writer.grab_frame()
end = time.time()
print(end-start)
