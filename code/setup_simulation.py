#!/usr/bin/env python3
import argparse
import os
from pathlib import Path

# get command line arguments
parser = argparse.ArgumentParser()
parser.add_argument("--queue", help="queueing type", default="local")
parser.add_argument("--name", help="name of runscript", default="test")
parser.add_argument("--steps", help="number of output steps", default=300)
parser.add_argument("--time", help="real time of one step", default=0.0001)
parser.add_argument(
    "--particles", help="desired number of target particles", default=30000
)
parser.add_argument("--angle", help="impact angle", default=0.0)
parser.add_argument("--strength", help="target strength", default=1e3)
parser.add_argument("--porosity", help="target porosity", default=0.5)
args = parser.parse_args()


# open and thereby name runscript
filename = "run_" + args.queue + "_" + args.name + ".sh"
if args.name != "test":
    Path("parameterstudy_runscripts/").mkdir(parents=True, exist_ok=True)
    filename = "parameterstudy_runscripts/" + filename
f = open(filename, "w")

# sbatch script format for kamino and endor
if args.queue == "sbatch":
    f.write(
        "#!/bin/bash\n"
        "set -e\n\n"
        "#SBATCH --partition=gpu\n"
        f"#SBATCH -J {args.name}\n"
        "#SBATCH --gres=gpu:1\n"
        "#SBATCH --time=07-00\n\n"
    )

# pbs script format for binac
elif args.queue == "pbs":
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
elif args.queue == "local":
    f.write("#!/bin/bash\n" "set -e\n\n")
else:
    raise ValueError("Unknown queueing type")

f.write("## Starting in the folder of the shell script\n" 'cd "$(dirname "$0")"\n\n')

f.write(
    "## Checking for simulation folder\n"
    f"if [ {args.name} == 'test' ]; then\n"
    "rm -rf test;\n"
    f"elif [ -d ../../data/{args.name} ]; then\n"
    f"echo 'Directory {args.name} already exists in /data!'; exit 1;\n"
    "fi\n\n"
)

f.write(
    "## Creating simulation folder\n"
    f"if [ {args.name} == 'test' ]; then\n"
    "mkdir test && cd test\n"
    "else\n"
    f"mkdir -p ../../data/{args.name} && cd ../../data/{args.name}\n"
    "fi\n\n"
)

f.write(
    "## Creating initial input file\n"
    f"python3 ../../../impact_ini/impact_ini.py --outfile impact_{args.name}.0000 --N_targ_des --angle {args.angle} --alpha_targ {args.porosity} --sml_fact 2.1 --weibull_m 16.0 --weibull_k 1e61 --damage 0.0 --stress 0.0 --alpha_proj 1.0 --pressure 0.0\n\n"
    f"#cp ../../code/impact.0000 impact_{args.name}.0000\n\n"
)

f.write(
    "## Creating material.cfg testfile\n"
    f"python3 ../../code/create_material.py -y {args.strength}\n\n"
)

f.write(
    "## Copying files into simulation folder\n"
    "cp ../../../miluphcuda/miluphcuda ../../data_analysis/create_xdmf.py .\n\n"
)

f.write(
    "## Starting miluphcuda\n"
    f"./miluphcuda -v -H -f impact_{args.name}.0000 -m material.cfg -n {args.steps} -t {args.time} > output_{args.name}.log 2> error_{args.name}.log\n\n"
)

f.write(
    "## Creating xdmf from h5 files\n"
    f"./create_xdmf.py --input impact_{args.name}.*.h5 --output parav_impact_{args.name}.xdmf\n\n"
)

f.write("## Saving ls output with times of files\n" "ls -ltrh > ls_output.log\n")

f.close()

# make file executable
os.chmod("./" + filename, 0o775)
