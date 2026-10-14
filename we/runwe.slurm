#!/bin/bash
#SBATCH --job-name=a2b
#SBATCH --partition=gpu_long
#SBATCH --nodes=1
#SBATCH --gres=gpu:5
#SBATCH --ntasks-per-node=5
#SBATCH --output=job_logs/slurm.out
#SBATCH --error=job_logs/slurm.err

set -x
cd $SLURM_SUBMIT_DIR
source env.sh || exit 1

env | sort

cd $WEST_SIM_ROOT

# Make sure environment is set
source env.sh

# Clean up
rm -f west.log
touch west.log

rm -rf $WEST_SIM_ROOT/tmp/*

which mpirun
python -c "import mpi4py; print(mpi4py.__version__)"
echo $SLURM_NTASKS

export OMPI_MCA_pml=ob1
export OMPI_MCA_btl="self,tcp"
export OMPI_MCA_opal_warn_on_missing_libcuda=0

# Run w_run
mpirun -n $SLURM_NTASKS \
          w_run --work-manager=mpi "$@"  &> west.log
