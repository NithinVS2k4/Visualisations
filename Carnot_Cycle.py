import numpy as np
import matplotlib.pyplot as plt

n = 1
R = 8.314

Th = 500
Tc = 250

V_1 = 2
V_3 = 16.98

P_1 = n*R*Th/V_1
P_3 = n*R*Tc/V_3

V_2 = ((P_3/(P_1*V_1))**1.5)*(V_3**2.5)
V_4 = ((P_1/(P_3*V_3))**1.5)*(V_1**2.5)

P_2 = n*R*Th/V_2
P_4 = n*R*Tc/V_4

k_1 = P_2*(V_2**(5/3))
k_2 = P_4*(V_4**(5/3))

print(f"{(P_1,V_1)},{(P_2,V_2)},{(P_3,V_3)},{(P_4,V_4)}")

def P_iso(n,R,V,T):
    return n*R*T/(V*1000)

def P_adia(V,k):
    return k/(V**(5/3)*1000)

rows = 1
cols = 1
fig,ax = plt.subplots(nrows=rows,ncols=cols,squeeze=False,figsize=(7,7))

V_iso_exp = np.linspace(V_1,V_2,100)
P_iso_exp = P_iso(n,R,V_iso_exp,Th)
V_adia_exp = np.linspace(V_2,V_3,100)
P_adia_exp = P_adia(V_adia_exp,k_1)
V_iso_com = np.linspace(V_4,V_3,100)
P_iso_com = P_iso(n,R,V_iso_com,Tc)
V_adia_com = np.linspace(V_1,V_4,100)
P_adia_com = P_adia(V_adia_com,k_2)


ax[0,0].plot(V_iso_exp,P_iso_exp)
ax[0,0].plot(V_adia_exp,P_adia_exp)
ax[0,0].plot(V_iso_com,P_iso_com)
ax[0,0].plot(V_adia_com,P_adia_com)

ax[0,0].relim()
ax[0,0].autoscale()

plt.ylabel('Pressure (kPa)')
plt.xlabel('Volume (m³)')

plt.show()
