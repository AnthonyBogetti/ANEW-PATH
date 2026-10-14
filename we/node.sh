#!/bin/bash -l

set -x

WEST_JOBID=$1; shift

cd $(dirname $0)
export TMPDIR=/local/$SLURM_JOBID
export LOCAL=/local/$SLURM_JOBID
(source env.sh
echo -n "starting WEST client process on "; hostname
echo "current directory is $PWD"
echo "environment is:"
env | sort
w_run "$@" ) &> west-$SLURM_JOBID-$(hostname -s).log
