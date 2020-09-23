#!/usr/bin/env python3

"""
Calculates the betafactor of impact momentum transfer from a miluphcuda .h5 file. 

Autoformatted with black.

Maximilian Rutz 03/Jul/2020
"""

import argparse
import numpy as np
import h5py
import pandas as pd


def parse_args():
    parser = argparse.ArgumentParser(
        description="Calculates the betafactor of impact momentum transfer from a miluphcuda .h5 file."
    )

    parser.add_argument(
        "--file",
        help="specify .h5 input file, default is /scratch/share/sph/burger_run5_30deg/impact.0300.h5",
        type=str,
        default="/scratch/share/sph/burger_run5_30deg/impact.0300.h5",
    )

    parser.add_argument(
        "--ejecta_thresh",
        help="height threshold for ejecta particles",
        type=float,
        default=0.0,
    )

    parser.add_argument(
        "--angle",
        help="angle of impact along x-direction",
        type=float,
        default=0.0,
    )

    return parser.parse_args()


def betafactor(file, ejecta_thresh, angle):
    # read data from miluphcuda .h5 file
    with h5py.File(file, "r") as hdf:
        df = pd.DataFrame(
            {
                "x": hdf.get("x")[:, 0],
                "y": hdf.get("x")[:, 1],
                "z": hdf.get("x")[:, 2],
                "v_x": hdf.get("v")[:, 0],
                "v_y": hdf.get("v")[:, 1],
                "v_z": hdf.get("v")[:, 2],
                "m": hdf.get("m"),
                "material_type": hdf.get("material_type"),
            }
        )

    # physical parameters
    r_didymoon = 75
    rho_didymoon = 2860.0
    M = 4 / 3 * np.pi * r_didymoon ** 3 * rho_didymoon
    G = 6.6743e-11

    # additional velocities
    df["v_abs"] = np.sqrt(df["v_x"] ** 2 + df["v_y"] ** 2 + df["v_z"] ** 2)
    df["v_escape"] = np.sqrt(2 * G * M / (r_didymoon + df.z))
    df["v_angle"] = np.sqrt((np.sin(angle) * df["v_x"]) ** 2 + (np.cos(angle) * df["v_z"] ** 2))

    # select ejecta particles
    filt_ejecta = (df["z"] > ejecta_thresh) & (df["v_z"] > 0) & (df["v_abs"] > df["v_escape"])

    # compute betafactor
    impactor_momentum = df.loc[df["material_type"] == 0]["m"] * 6000
    recoil_momentum = df[filt_ejecta]["m"] * df[filt_ejecta]["v_angle"]
    beta = (impactor_momentum.sum() + recoil_momentum.sum()) / impactor_momentum.sum()

    # print results
    # print(f"ejecta particles: {filt_ejecta.sum()}")
    # print(f"Betafactor: {beta:.2f}")
    return beta, recoil_momentum


if __name__ == "__main__":
    args = parse_args()
    betafactor(file=args.file, ejecta_thresh=args.ejecta_thresh, angle=args.angle)
