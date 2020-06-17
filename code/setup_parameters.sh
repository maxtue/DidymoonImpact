## create setups with different parameters
for porosity in 0 0.25 0.5 0.75
do
    for strength in 1e3 1e4 1e5 1e6 
    do
        for angle in 0 15 30 45
        do
            python3 setup_simulation.py --porosity $porosity --strength $strength --angle $angle --name "por${porosity}_str${strength}_ang${angle}"
        done
    done
done