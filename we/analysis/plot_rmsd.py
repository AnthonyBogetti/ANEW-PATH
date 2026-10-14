import wedap
import numpy as np
import matplotlib.pyplot as plt

plt.rcParams.update({'font.size': 16, 'axes.linewidth': 1.5})

data_options = {"h5" : "analysis/west.h5.bak",
                "Xname" : "rmsd2a",
                "Yname" : "rmsd2b",
                "data_type" : "average",
                "cbar_label" : "-ln(P)",
                "xlabel" : "RMSD to A",
                "ylabel" : "RMSD to B",
                "xlim" : (0,10),
                "ylim" : (0,10),
                "cmap" : "viridis",
                }

plot = wedap.H5_Plot(**data_options)
plot.plot()

Xc = np.loadtxt("common_files/rmsd_ref.dat", skiprows=1, usecols=1)
Yc = np.loadtxt("common_files/rmsd_ref.dat", skiprows=1, usecols=2)

plt.scatter(Xc, Yc, color="black", marker="o", s=20, zorder=3)
plt.scatter(Xc, Yc, color="magenta", marker="o", s=10, zorder=3)


plt.savefig("analysis/rmsd.pdf")
