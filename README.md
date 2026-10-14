# ANEW-PATH
A template simulation directory that can be used to setup and run adaptive ANM-driven weighted ensemble simulations with ProDy and WESTPA.

## How to use this template directory
To use this template, perform the following steps
1. Create a conda env that contains prody and westpa.
2. Make sure amber is installed or loaded from your modules.
3. Copy your Amber system topology into the common\_files folder and name it top.prmtop.
4. Take your MD-equilibrated endpoint structures and make pdbs of both structures with protein only (a.pdb and b.pdb)
   and then also with protein CA atoms only (a\_ca.pdb and b\_ca.pdb) and place the 4 files in common\_files as well.
5. If you want to simulate a to b direction, copy the equilibrated Amber rst file into the bstates folder and name it bstate.ncrst.
   Then, copy the a.pdb and a\_ca.pdb into bstates folder and rename them to bstate.pdb and bstate\_ca.pdb.
6. If you also want to simulate the b to a direction, do the same as in step 5 but with the structure b Amber rst file.
   Also, edit line 11 of score.py to be 'midpts = np.load("midpoints.npy")[::-1]' which basically just reverses the midpoint array.
7. Then, begin each simulation as you would any WESTPA run, with cd into $WEST\_SIM\_ROOT, bash init.sh and submit runwe.slurm
   (after you modify it to work with your cluster and scheduler).
8. Analysis scripts in the analysis foler can be used after pip installing the wedap package.
