import h5py

f = h5py.File("west.h5.bak", "r")
n_iters = f['summary'][:].shape[0]

for i in range(1,n_iters):
    aux1_str = "iterations/iter_"+str(i).zfill(8)+"/auxdata/rmsd2a"
    aux2_str = "iterations/iter_"+str(i).zfill(8)+"/auxdata/rmsd2b"
    aux1 = f[aux1_str][:,-1]
    aux2 = f[aux2_str][:,-1]
    for idx, val in enumerate(aux2):
        if val < 3:
            print(i, idx)
