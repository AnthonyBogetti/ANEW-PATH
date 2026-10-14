#!/bin/bash

if [ -n "$SEG_DEBUG" ] ; then
  set -x
  env | sort
fi

cd $WEST_SIM_ROOT
mkdir -pv $WEST_CURRENT_SEG_DATA_REF
cd $WEST_CURRENT_SEG_DATA_REF

# Link files here
ln -sv $WEST_SIM_ROOT/common_files/top.prmtop .
ln -sv $WEST_SIM_ROOT/common_files/a_ca.pdb .
ln -sv $WEST_SIM_ROOT/common_files/b_ca.pdb .
ln -sv $WEST_SIM_ROOT/bstates/bstate_ca.pdb .
ln -sv $WEST_SIM_ROOT/common_files/score.py .
ln -sv $WEST_SIM_ROOT/common_files/rmsd_ref.dat .
ln -sv $WEST_SIM_ROOT/common_files/midpoints.npy .

# Change random seed
if [ "$WEST_CURRENT_SEG_INITPOINT_TYPE" = "SEG_INITPOINT_CONTINUES" ]; then
  sed "s/RAND/$WEST_RAND16/g" $WEST_SIM_ROOT/common_files/md.in > md.in
  ln -sv $WEST_PARENT_DATA_REF/seg.ncrst ./parent.ncrst
  ln -sv $WEST_PARENT_DATA_REF/seg.pdb ./parent.pdb
elif [ "$WEST_CURRENT_SEG_INITPOINT_TYPE" = "SEG_INITPOINT_NEWTRAJ" ]; then
  sed "s/RAND/$WEST_RAND16/g" $WEST_SIM_ROOT/common_files/md.in > md.in
  ln -sv $WEST_PARENT_DATA_REF ./parent.ncrst
  ln -sv $WEST_SIM_ROOT/bstates/bstate.pdb ./parent.pdb
fi

module load amber

pmemd.cuda -O -i md.in -o seg.log -p top.prmtop -c parent.ncrst -r seg.ncrst -x seg.nc

# Autoimage parent+segment trajectory and calculate auxdata while we're at it
# Replaced 'autoimage' with the unwrap/center/image sequence for disjointed chains
SOLUTE_MASK="!(:WAT,HOH,Na+,Cl-,K+,Mg2+)"

COMMAND="         parm top.prmtop\n"
COMMAND="$COMMAND trajin parent.ncrst\n"
COMMAND="$COMMAND trajin seg.nc\n"
COMMAND="$COMMAND unwrap $SOLUTE_MASK\n"
COMMAND="$COMMAND center $SOLUTE_MASK mass origin\n"
COMMAND="$COMMAND image origin center familiar\n"
COMMAND="$COMMAND strip !@CA\n"
COMMAND="$COMMAND trajout comb_ca.dcd\n"
COMMAND="$COMMAND go"

echo -e "$COMMAND" | cpptraj

COMMAND="         parm bstate_ca.pdb\n"
COMMAND="$COMMAND trajin comb_ca.dcd\n"
COMMAND="$COMMAND reference a_ca.pdb [a]\n"
COMMAND="$COMMAND reference b_ca.pdb [b]\n"
COMMAND="$COMMAND rmsd 2a ref [a] out rmsd_curr.dat\n"
COMMAND="$COMMAND rmsd 2b ref [b] out rmsd_curr.dat\n"
COMMAND="$COMMAND go"

echo -e "$COMMAND" | cpptraj

# Calculate pcoord(s) and save
python score.py > score.dat
cat score.dat > $WEST_PCOORD_RETURN

# Save auxdata
cat rmsd_curr.dat | tail -n +2 | awk {'print $2'} > $WEST_RMSD2A_RETURN
cat rmsd_curr.dat | tail -n +2 | awk {'print $3'} > $WEST_RMSD2B_RETURN

# Save segmnet trajectory to HDF5 file
cp top.prmtop $WEST_TRAJECTORY_RETURN
cp seg.nc $WEST_TRAJECTORY_RETURN

cp top.prmtop $WEST_RESTART_RETURN
cp seg.ncrst $WEST_RESTART_RETURN/parent.ncrst

cp seg.log $WEST_LOG_RETURN

# Clean up
rm -f md.in top.prmtop seg.nc comb.nc mdinfo run_coords.npy *.dcd
