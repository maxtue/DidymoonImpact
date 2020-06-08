#!/usr/bin/env python3
import argparse
import os
from pathlib import Path

# get command line arguments
parser = argparse.ArgumentParser()
parser.add_argument("-q", help="queueing type", default="local")
parser.add_argument("-n", help="name of runscript", default="test")
parser.add_argument("-s", help="number of output steps", default=1)
parser.add_argument("-t", help="real time of one step", default=0.0001)
parser.add_argument("-a", help="impact angle", default=0.0)
parser.add_argument("-y", help="target strength", default=1e3)
parser.add_argument("-p", help="target porosity", default=0.5)
args = parser.parse_args()
queueing_type = args.q
testname = args.n
num_steps = args.s
step_time = args.t
angle = args.a
strength = args.y
porosity = args.p

# open and thereby name runscript
filename = "run_" + queueing_type + "_" + testname + ".sh"
if testname != "test":
    Path("parameterstudy_runscripts/").mkdir(parents=True, exist_ok=True)
    filename = "parameterstudy_runscripts/" + filename
f = open(filename, "w")

# sbatch script format for kamino and endor
if queueing_type == "sbatch":
    f.write(
        "#!/bin/bash\n"
        "set -e\n\n"
        "#SBATCH --partition=gpu\n"
        f"#SBATCH -J {testname}\n"
        "#SBATCH --gres=gpu:1\n"
        "#SBATCH --time=07-00\n\n"
    )

# pbs script format for binac
elif queueing_type == "pbs":
    f.write(
        "#!/usr/bin/env bash\n"
        "set -e\n\n"
        "#PBS -l walltime=720:00:00\n"
        "#PBS -l nodes=1:ppn=1:gpus=1:exclusive_process\n"
        "#PBS -q gpu\n\n"
        "cd $PBS_O_WORKDIR\n"
        "module load devel/cuda/10.0\n"
        "unset CUDA_VISIBLE_DEVICES\n"
        "LD_LIBRARY_PATH=$LD_LIBRARY_PATH:~/local/lib\n\n"
    )

# no head
elif queueing_type == "local":
    f.write("#!/bin/bash\n" "set -e\n\n")
else:
    raise ValueError("Unknown queueing type")

f.write(
    "## Starting in the folder of the shell script\n"
    'cd "$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"\n\n'
)

f.write(
    "## Checking for simulation folder\n"
    f"if [ {testname} == 'test' ]; then\n"
    "rm -rf test;\n"
    f"elif [ -d ../../data/{testname} ]; then\n"
    f"echo 'Directory {testname} already exists in /data!'; exit 1;\n"
    "fi\n\n"
)

f.write(
    "## Creating simulation folder\n"
    f"if [ {testname} == 'test' ]; then\n"
    "mkdir test && cd test\n"
    "else\n"
    f"mkdir ../../data/{testname} && cd ../../data/{testname}\n"
    "fi\n\n"
)

f.write(
    "## Creating initial input file\n"
    f"#python3 ../../code/create_initial.py -a {angle} -p {porosity}\n\n"
    f"cp ../impact.0000 impact_{testname}.0000\n\n"
)

f.write(
    "## Creating material.cfg testfile\n"
    f"python3 ../../code/create_material.py -y {strength}\n\n"
)

f.write(
    "## Copying files into simulation folder\n"
    "cp ../../code/config_files/ANEOS.basaltm.table ../../code/miluphcuda ../../data_analysis/create_xdmf.py .\n\n"
)


f.write(
    "## Starting miluphcuda\n"
    f"./miluphcuda -v -H -f impact_{testname}.0000 -m material.cfg -n {num_steps} -t {step_time} > output_{testname}.log 2> error_{testname}.log\n\n"
)

f.write(
    "## Creating xdmf from h5 files\n"
    f"./create_xdmf.py --input impact_{testname}.*.h5 --output parav_impact_{testname}.xdmf\n\n"
)

f.write("## Saving ls output with times of files\n" "ls -ltrh > ls_output.log\n")

f.close()

# make file executable
os.chmod("./" + filename, 0o775)
