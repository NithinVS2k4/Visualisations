import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FFMpegWriter
plt.rcParams['animation.ffmpeg_path'] = "/Users/nithin/Desktop/ffmpeg"

fig = plt.figure()

center = (0,0)
scale = 0.25


def unit_vec(vec):
    mag = (vec[0]**2 + vec[1]**2)**0.5
    unit_vec = [vec[0]/mag,vec[1]/mag]
    return unit_vec

def scale_vec(vec,s):
    return [vec[0]*s,vec[1]*s]

class Hand():
    def __init__(self,pos,dirn,length,omega,idx):
        self.pos = pos
        self.dir = unit_vec(dirn).copy()
        self.len = length
        scaled_dir = scale_vec(self.dir,length).copy()
        self.end = [self.pos[0]+scaled_dir[0],self.pos[1]+scaled_dir[1]]
        self.omega = omega
        self.idx = idx

    def update(self):
        global deltaTime,stick_list
        if self.idx == 0:
            self.pos = center
        else:
            self.pos = stick_list[self.idx - 1].end.copy()
        theta = deltaTime*self.omega
        self.dir = [self.dir[0]*np.cos(theta)-self.dir[1]*np.sin(theta),self.dir[0]*np.sin(theta)+self.dir[1]*np.cos(theta)]
        scaled_dir = scale_vec(self.dir,self.len).copy()
        self.end = [self.pos[0]+scaled_dir[0],self.pos[1]+scaled_dir[1]]


metadata = dict(title='Movie',artist='codinglikemad')
writer = FFMpegWriter(fps=30,metadata=metadata)

time_period = 5
deltaTime = 1/writer.fps
max_frame = time_period*writer.fps
frame = 1
wave = []
x_waves = np.zeros((max_frame))

L = 10
O = 12.56/time_period
N = 10

with writer.saving(fig, "Animations/FourierWave.mp4",100):
    for n in range(1,N+1):

        stick_list = []
        frame = 1
        wave = []
        x_waves = np.zeros((max_frame))
        stick_list.append(Hand(center,[0,-1],L,O,0))
        for i in range(n-1):
            stick_list.append(Hand(stick_list[i].end.copy(),[0,(-1)**(i)],L/(2*i + 3),O*(2*i+3),i+1))

        while(frame<= max_frame):
            plt.clf()
            for hand in stick_list:
                hand.update()
                plt.plot([hand.pos[0],hand.end[0]],[hand.pos[1],hand.end[1]])

            wave.append(stick_list[n-1].end[1])
            x_waves = np.asarray(range(frame,0,-1))*deltaTime*4 + 20
            plt.plot(x_waves,wave,'r-')
            frame += 1

            plt.xlim(-15,35)
            plt.ylim(-15,35)

            writer.grab_frame()
