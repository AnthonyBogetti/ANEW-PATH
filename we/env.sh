#!/bin/bash

source ~/.bashrc
conda activate westpa

module load amber/2024 cuda12.2 openmpi

export WEST_SIM_ROOT="$PWD"
export TMPDIR=$WEST_SIM_ROOT/tmp
export SIM_NAME=$(basename $WEST_SIM_ROOT)
export WM_ZMQ_MASTER_HEARTBEAT=100
export WM_ZMQ_WORKER_HEARTBEAT=100
