#!/bin/bash
set -x
cd $WEST_SIM_ROOT || exit 1

cd common_files

cpptraj -i rmsd_ref.in

python get_mdpts.py

cd ../

# Calculate pcoord
echo 0 > $WEST_PCOORD_RETURN

cp $WEST_SIM_ROOT/common_files/top.prmtop $WEST_TRAJECTORY_RETURN
cp $WEST_STRUCT_DATA_REF $WEST_TRAJECTORY_RETURN

cp $WEST_SIM_ROOT/common_files/top.prmtop $WEST_RESTART_RETURN
cp $WEST_STRUCT_DATA_REF $WEST_RESTART_RETURN/parent.ncrst
