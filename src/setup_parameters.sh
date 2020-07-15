## create setups with different parameters
rm -rf parameterstudy_runscripts/
for porosity in 0.0 0.17 0.33 0.50
do
    for strength in 1e3 1e4 1e5 1e6
    do
        for angle in 0 45
        do
            python3 setup_simulation.py --queue pbs --porosity $porosity --strength $strength --angle $angle --name "por${porosity#*.}_str${strength}_ang${angle}"
        done
    done
done 

read -p "Submit all scripts to pbs via qsub? (y/n) " RESP
if [ "$RESP" = "y" ]; then
    cd parameterstudy_runscripts/
    for filename in ./*.sh;do
        qsub $filename
    done
fi 
