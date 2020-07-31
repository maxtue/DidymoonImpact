#!/usr/bin/env python3
import argparse
import os
from pathlib import Path

# get command line arguments
parser = argparse.ArgumentParser()
parser.add_argument("--angle", help="impact angle", default=0.0, type=float)
parser.add_argument("--name", help="name of runscript", default="test")
parser.add_argument("--particles", help="number of particles", default=80000, type=int)
parser.add_argument("--porosity", help="target porosity", default=0.5, type=float)
parser.add_argument("--queue", help="queueing type", default="local")
parser.add_argument("--steps", help="number of output steps", default=300)
parser.add_argument("--strength", help="target strength", default=1e3, type=float)
parser.add_argument("--time", help="real time of one step", default=0.001)
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
        "#!/bin/bash\n" "#SBATCH --partition=gpu\n" f"#SBATCH -J {args.name}\n" "#SBATCH --time=07-00\n\n" "set -e\n\n"
    )

# pbs script format for binac
elif args.queue == "pbs":
    f.write(
        "#!/usr/bin/env bash\n"
        f"#PBS -N {args.name}\n"
        f"#PBS -o {args.name}_log\n"
        f"#PBS -e {args.name}_error\n"
        "#PBS -M maximilian.rutz@student.uni-tuebingen.de\n"
        "#PBS -l walltime=720:00:00\n"
        "#PBS -l nodes=1:ppn=1:gpus=1\n"
        "#PBS -q gpu\n\n"
        "set -e\n"
        "cd $PBS_O_WORKDIR\n"
        "module load devel/cuda/10.1\n"
        "module load lib/hdf5/1.8.16-gnu-4.9\n"
        "module list\n"
        "unset CUDA_VISIBLE_DEVICES\n"
        "LD_LIBRARY_PATH=$LD_LIBRARY_PATH:~/local/lib\n\n"
    )

# no head
elif args.queue == "local":
    f.write("#!/bin/bash\n" "set -e\n\n")
else:
    raise ValueError("Unknown queueing type")

# f.write("## Starting in the folder of the shell script\n" 'cd "$(dirname "$0"); pwd"\n\n')

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
    f"python3 ../../../impact_ini/impact_ini.py --outfile impact_{args.name}.0000 --angle {args.angle} --alpha_targ {1.0 / (1.0 - args.porosity)} --N_targ_des {args.particles} --output_format 'SOLIDPOROUS' --cubic_proj 1 --sml_fact 2.1 \n\n"
)

f.write(
    "## Creating material.cfg testfile\n"
    f"python3 ../../src/create_material.py --porosity {args.porosity} --strength {args.strength}\n\n"
)

f.write(
    "## Copying files into simulation folder\n"
    "cp ../../../miluphcuda/miluphcuda ../../data_analysis/create_xdmf.py .\n\n"
)

f.write(
    "## Starting miluphcuda\n"
    f"./miluphcuda -v -H -A -f impact_{args.name}.0000 -m material.cfg -n {args.steps} -t {args.time} > output_{args.name}.log 2> error_{args.name}.log\n\n"
)

f.write("## Saving ls output with times of files\n" "ls -ltrh > ls_output.log\n")

f.write(
    "## Creating xdmf from h5 files\n"
    f"./create_xdmf.py --input impact_{args.name}.*.h5 --output parav_impact_{args.name}.xdmf\n\n"
)

f.close()

# make file executable
os.chmod("./" + filename, 0o775)
