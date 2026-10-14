from westpa.analysis import Run
from westpa.analysis import HDF5MDTrajectory

run = Run.open("./west.h5")

iteration = run.iteration(57)

walker = iteration.walker(5)

trace = walker.trace()

trajectory = HDF5MDTrajectory()

traj = trajectory(trace)

traj.save("pathway3.dcd")
