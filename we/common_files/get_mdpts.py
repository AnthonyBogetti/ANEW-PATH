import numpy as np
import math

rmsd_ref = np.loadtxt("rmsd_ref.dat", skiprows=1, usecols=(1,2))

ref = rmsd_ref.reshape(-1,2)

midpts = []

midpts.append(list(ref[0]))

for i in range(len(ref) - 1):
    p1 = ref[i]
    p2 = ref[i+1]
    mx = (p1[0] + p2[0]) / 2
    my = (p1[1] + p2[1]) / 2
    midpts.append((mx, my))
    
midpts.append(list(ref[-1]))

midpts = np.array(midpts)

np.save("midpoints.npy", midpts)
