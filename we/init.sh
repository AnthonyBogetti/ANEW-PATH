#!/bin/bash

# Set up simulation environment
source env.sh

# Clean up from previous/ failed runs
rm -rf traj_segs seg_logs istates west.h5 wetest.* west.log west-* west_zmq* *.pdf
mkdir   seg_logs traj_segs istates

# Set pointer to bstate and tstate
BSTATE_ARGS="--bstate-file $WEST_SIM_ROOT/bstates/bstates.txt"

# Run w_init
w_init \
  $BSTATE_ARGS \
  --segs-per-state 4 \
  --work-manager=threads "$@"
