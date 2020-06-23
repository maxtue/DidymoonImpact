## create setups with different parameters
for porosity in 0.0 0.17 0.33 0.5
do
    for strength in 1e3 1e4 1e5 1e6
    do
        for angle in 0 45
        do
            python3 setup_simulation.py --queue pbs --porosity $porosity --strength $strength --angle $angle --name "por${porosity}_str${strength}_ang${angle}"
        done
    done
done