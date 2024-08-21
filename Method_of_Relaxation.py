import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mlib
from datetime import datetime

# Parameters
grid_size = 64
x_interval = (0, 2*np.pi)
y_interval = (0, 2*np.pi)
iterations = 10

x_values = np.linspace(x_interval[0],x_interval[1],grid_size)
y_values = np.linspace(y_interval[0],y_interval[1],grid_size)
# Boundary Conditions
bcs_left = np.sin(y_values) + np.sin(x_interval[0])
bcs_right = np.sin(y_values) + np.sin(x_interval[1])
bcs_top = np.sin(y_interval[1]) + np.sin(x_values)
bcs_bottom = np.sin(y_interval[0]) + np.sin(x_values)
bcs = [bcs_left,bcs_top,bcs_right,bcs_bottom]

def plot_colored_grid(data):
    plt.figure(frameon=True)
    bounds = [data.min(), data.max()]
    norm = mlib.colors.Normalize(vmin=bounds[0], vmax=bounds[1])
    plt.imshow(data, cmap='viridis', norm=norm, origin='lower', extent=[x_interval[0], x_interval[1], y_interval[0], y_interval[1]])
    plt.colorbar(label='Potential')
    plt.title('Potential Distribution')
    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')

potential_array = np.zeros((grid_size,grid_size),dtype='float64')

def method_of_relaxation(bcs,pot_array):
    bcs_left,bcs_top,bcs_right,bcs_bottom = bcs
    gs = pot_array.shape[0] #gs --> Grid size
    for i in range(gs):
        for j in range(gs):
            #Bulk of the potential table
            if (gs-1>i>0) and (gs-1>j>0):
                pot_array[i,j] = np.sum(pot_array[i-1,j-1:j+2]) + np.sum(pot_array[i+1,j-1:j+2]) + pot_array[i,j-1] + pot_array[i,j+1]
                pot_array[i,j] /= 8
            #At the edges and corners
            else:
                #Edges
                if (i==0) and (gs-1>j>0):
                    pot_array[i,j] = np.sum(bcs_top[j-1:j+2]) + np.sum(pot_array[i+1,j-1:j+2]) + pot_array[i,j-1] + pot_array[i,j+1]
                    pot_array[i,j] /= 8
                if (i==gs-1) and (gs-1>j>0):
                    pot_array[i,j] = np.sum(bcs_bottom[j-1:j+2]) + np.sum(pot_array[i-1,j-1:j+2]) + pot_array[i,j-1] + pot_array[i,j+1]
                    pot_array[i,j] /= 8
                if (gs-1>i>0) and (j==0):
                    pot_array[i,j] = np.sum(bcs_left[i-1:i+2]) + np.sum(pot_array[i-1:i+2,j+1]) + pot_array[i-1,j] + pot_array[i+1,j]
                    pot_array[i,j] /= 8
                if (gs-1>i>0) and (j== gs-1):
                    pot_array[i,j] = np.sum(bcs_right[i-1:i+2]) + np.sum(pot_array[i-1:i+2,j-1]) + pot_array[i-1,j] + pot_array[i+1,j]
                    pot_array[i,j] /= 8
                #Corners
                if (i==0) and (j==0):
                    pot_array[i,j] = pot_array[1,0] + pot_array[1,1] + pot_array[0,1] + np.sum(bcs_left[gs-2:gs]) + np.sum(bcs_top[0:2])
                    pot_array[i,j] /= 7
                if (i==0) and (j==gs-1):
                    pot_array[i,j] = pot_array[0,gs-2] + pot_array[1,gs-2] + pot_array[1,gs-1] + np.sum(bcs_top[gs-2:gs]) + np.sum(bcs_right[0:2])
                    pot_array[i,j] /= 7
                if (i==gs-1) and (j==0):
                    pot_array[i,j] = pot_array[gs-2,0] + pot_array[gs-2,1] + pot_array[gs-1,1] + np.sum(bcs_left[0:2]) + np.sum(bcs_bottom[0:2])
                    pot_array[i,j] /= 7
                if (i==gs-1) and (j== gs-1):
                    pot_array[i,j] = pot_array[gs-1,gs-2] + pot_array[gs-2,gs-2] + pot_array[gs-2,gs-1] + np.sum(bcs_bottom[gs-2:gs]) + np.sum(bcs_right[gs-2:gs])
                    pot_array[i,j] /= 7

    return pot_array

start = datetime.now()
for i in range(iterations):
    print(f"{round(100*(i+1)/iterations,3)}% done")
    potential_array = method_of_relaxation(bcs,potential_array)
end = datetime.now()

time_taken = (end-start).total_seconds()
print(f"Time taken for computation: {round(time_taken,2)}s")
plot_colored_grid(potential_array)

x_values, y_values = np.meshgrid(x_values,y_values)

fig_3d = plt.figure(figsize=(8,5),dpi=100)
axes = fig_3d.add_axes([0,0,1,1],projection='3d')

axes.view_init(45,-105)

axes.plot_surface(x_values,y_values,potential_array,rstride=2,cstride=2,cmap='viridis')
axes.set_xlabel('x axis')
axes.set_ylabel('y axis')
axes.set_zlabel('z axis')

plt.show()
