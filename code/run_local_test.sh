## Creating test file from default
cp material.cfg material_test.cfg

## Checking simulation folder
if [ -d test ]; then
echo 'Directory test already exists!'; exit 1;
fi

## Creating simulation folder
mkdir test && cd test
cp ../impact.0000 ../material_test.cfg ../ANEOS.basaltm.table ../miluphcuda ../weibull ../create_xdmf.py .

## Assigning flaws to particles according to weibull distribution
./weibull -v -k 1e61 -m 16.0 -P -f impact.0000 -o impact_damage_test.0000 -n `wc -l impact.0000` -t 0

## Starting miluphcuda
./miluphcuda -v -H -f impact_damage_test.0000 -m material_test.cfg -n 1 -t 0.001 -I rk2_adaptive -Q 1e-5 > output_test.log 2> error_test.log

## Creating xdmf from h5 files
./create_xdmf.py --input impact_damage_test.*.h5 --output parav_impact_damage_test.xdmf

## Saving ls output with writing-times of files
ls -ltrh > ls_output.log