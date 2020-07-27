# DidymoonImpact
Computational physics simulations for the NASA asteroid deflection mission DART:
https://dart.jhuapl.edu/

## Motivation
Can an asteroid coming for earth be redirected by a planned impact? To find out, NASA is sending a small spacecraft to the Didymos asteroid binary. The spacecraft will crash into the smaller Didymos B, informally called Didymoon. ESA will later look at the results with its own HERA mission.\
\
Numerical simulations ahead of the mission support its planning and execution. Many material properties of the Didymoon asteroid are unknown and the exact impact conditions might vary. This project simulates the outcome of the DART impact for different parameters.\
\
![](https://github.com/maxtue/DidymoonImpact/blob/master/MasterThesis/images/dart_mission.jpg)

## Tech used
- All simulations were run with [miluphcuda](https://github.com/christophmschaefer/miluphcuda), a [Smoothed particle hydrodynamics](https://en.wikipedia.org/wiki/Smoothed-particle_hydrodynamics) code capable of parallel computing on NVIDIA GPUs.
- The setup of initial conditions for the simulation (such as particle positions and velocities) as well as the data analysis was done in Python.
- Visualization of the simulation results was done with [ParaView](https://www.paraview.org/).

## Credits
[Miluphcuda](https://github.com/christophmschaefer/miluphcuda) is build and maintained mainly by Christoph Schaefer in the computational physics group ([CPT](https://uni-tuebingen.de/fakultaeten/mathematisch-naturwissenschaftliche-fakultaet/fachbereiche/physik/institute/astronomie-astrophysik/institut/computational-physics/willkommen/)) at the University of Tuebingen.

## A last note
If the [2013 Chelyabinsk Meteor](https://www.youtube.com/watch?v=tq02C_3FvFo) had come down over Paris instead of Siberia, the DART mission would have gotten even more funding...
