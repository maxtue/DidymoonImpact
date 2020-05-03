# DidymoonImpact
Computational physics simulations for the NASA/ESA asteroid deflection mission DART/Hera in 2022: 
https://www.esa.int/Safety_Security/Hera

## Motivation
Can an asteroid coming for our earth be redirected by a satelite impact? To find out, NASA is sending a small satellite to the Didymos System with arrival in 2022. The satellite will crash into the smaller Didymos B, informally called Didymoon. ESA will later look at the results with its own HERA mission. \
Numerical simulations before the mission can support its execution. Many material properties of the Didymoon asteroid are unknown and the exact impact conditions might vary. This project therefore simulates the outcome of the DART impact for different parameters.

![alt text](https://www.esa.int/var/esa/storage/images/esa_multimedia/images/2018/06/dart_impact/17534515-2-eng-GB/DART_impact_pillars.jpg)

## Tech used
- All simulations were run with [miluphcuda](https://github.com/christophmschaefer/miluphcuda), a [Smoothed particle hydrodynamics](https://en.wikipedia.org/wiki/Smoothed-particle_hydrodynamics) code capable of parallel computing on NVIDIA GPUs. 
- The setup of initial conditions for the simulation (such as particle positions and veolicities) as well as the data analysis was done in Python.
- Visualization of the simulation results was done with [ParaView](https://www.paraview.org/).

## Credits
[miluphcuda](https://github.com/christophmschaefer/miluphcuda) is build and maintained mainly by Christoph Schaefer in the computational physics group ([CPT](https://uni-tuebingen.de/fakultaeten/mathematisch-naturwissenschaftliche-fakultaet/fachbereiche/physik/institute/astronomie-astrophysik/institut/computational-physics/willkommen/)) at the University of Tuebingen.

## A last note
If the [2013 Chelyabinsk Meteor](https://www.youtube.com/watch?v=tq02C_3FvFo) had come down over Paris instead of Siberia, the DART/Hera mission would have gotten even more more funding...
