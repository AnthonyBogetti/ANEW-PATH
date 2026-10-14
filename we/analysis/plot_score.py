import numpy as np
import matplotlib.pyplot as plt
import h5py

plt.rcParams.update({'font.size': 16, 'axes.linewidth': 1.5})

f = h5py.File("analysis/west.h5.bak")

score_max = []

n_iters = f["summary"].shape[0]

for i in range(1, n_iters):
    s = "iterations/iter_"+str(i).zfill(8)+"/pcoord"
    score_max.append(np.max(f[s][:,-1]))

xs = np.arange(1,n_iters)[:-1]
ys = score_max[:-1]

fig, ax = plt.subplots()
ax.plot(xs, ys)
ax.set_xlabel('WE Iteration')
ax.set_ylabel('Max aANM Score')

plt.grid(axis='y')
plt.tight_layout()
plt.savefig("analysis/score.pdf")
