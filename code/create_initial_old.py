"""
Author      : Maximilian Rutz and Oliver Wandel
Purpose     : initial conditions for sph 3D impact simulations
"""

import numpy as np
import argparse

ROOT_TWO_THIRDS = np.sqrt(2.0 / 3.0)
ROOT_THREE = np.sqrt(3.0)


def main():
    # get command line arguments
    args = parse()

    # shapes input
    delta = (np.sqrt(0.5) * 4 / 3 * np.pi * args.r ** 3 / args.n) ** (1 / 3)
    shape_targ_sim = 1
    shape_targ_bound = 2
    shape_proj = 0
    r_inner_targ = 1 * args.r  # - delta * 6  # target simulation radius
    r_outer_targ = args.r  # target boundary radius
    a_cube_proj = 1.0  # determines projectile size
    m_proj = 500.0  # impactor mass
    phi = args.a  # projectile path to target surface normal in 360 degrees
    sin_phi = np.sin(phi / 180.0 * np.pi)
    cos_phi = np.cos(phi / 180.0 * np.pi)
    v_impact = 6000  # absolute value of impact velocity
    dist_targ_proj = 0.0015 * v_impact  # distance target and projectile

    # positions
    x_targ_start = -r_outer_targ
    x_targ_stop = 0
    y_targ_start = -r_outer_targ
    y_targ_stop = r_outer_targ
    z_targ_start = -r_outer_targ
    z_targ_stop = r_outer_targ
    x_proj_start = dist_targ_proj
    x_proj_stop = dist_targ_proj  # + a_cube_proj
    y_proj_start = 0  # -0.5 * a_cube_proj
    y_proj_stop = 0  # 0.5 * a_cube_proj
    z_proj_start = 0  # -0.5 * a_cube_proj
    z_proj_stop = 0  # 0.5 * a_cube_proj

    # dynamics
    vx_targ = 0
    vy_targ = 0
    vz_targ = 0
    vx_proj = -cos_phi * v_impact
    vy_proj = -sin_phi * v_impact
    vz_proj = 0

    # material input
    rho_targ_bulk = 2860.0
    rho_proj_bulk = 2700.0
    alpha_jutzi_targ = 1.0 / (1.0 - args.p)  # target distention
    alpha_jutzi_proj = 1.0  # projectile distention
    rho_targ = rho_targ_bulk / alpha_jutzi_targ
    rho_proj = rho_proj_bulk / alpha_jutzi_proj
    energy = 0.0
    pressure = 0.0
    mat_targ_sim = 0  # basalt simulation
    mat_targ_bound = 1  # basalt boundary
    mat_proj = 2  # aluminium
    flaws = 0
    damage = 0.0
    Sxx = 0.0
    Sxy = 0.0
    Sxz = 0.0
    Syx = 0.0
    Syy = 0.0
    Syz = 0.0
    Szx = 0.0
    Szy = 0.0
    Szz = 0.0

    # particle mass
    mass_targ = rho_targ * pow(delta, 3) / np.sqrt(2.0)
    mass_proj = rho_proj * pow(delta, 3) / np.sqrt(2.0)
    # dryrun to get cube particle particle number
    n_proj = particle_number_dryrun(
        delta,
        x_proj_start,
        x_proj_stop,
        y_proj_start,
        y_proj_stop,
        z_proj_start,
        z_proj_stop,
    )
    mass_proj = m_proj / n_proj  # total projectile mass by number of
    # particles

    # open file to write data into
    f = open("impact.0000", "w")

    # write target simulation particles
    n_targ_sim = print_particles(
        f,
        delta,
        shape_targ_sim,
        r_inner_targ,
        r_outer_targ,
        x_targ_start,
        x_targ_stop,
        y_targ_start,
        y_targ_stop,
        z_targ_start,
        z_targ_stop,
        vx_targ,
        vy_targ,
        vz_targ,
        sin_phi,
        cos_phi,
        mass_targ,
        rho_targ,
        energy,
        mat_targ_sim,
        flaws,
        damage,
        Sxx,
        Sxy,
        Sxz,
        Syx,
        Syy,
        Syz,
        Szx,
        Szy,
        Szz,
        alpha_jutzi_targ,
        pressure,
    )

    # write target boundary particles
    n_targ_bound = print_particles(
        f,
        delta,
        shape_targ_bound,
        r_inner_targ,
        r_outer_targ,
        x_targ_start,
        x_targ_stop,
        y_targ_start,
        y_targ_stop,
        z_targ_start,
        z_targ_stop,
        vx_targ,
        vy_targ,
        vz_targ,
        sin_phi,
        cos_phi,
        mass_targ,
        rho_targ,
        energy,
        mat_targ_bound,
        flaws,
        damage,
        Sxx,
        Sxy,
        Sxz,
        Syx,
        Syy,
        Syz,
        Szx,
        Szy,
        Szz,
        alpha_jutzi_targ,
        pressure,
    )

    # print input related information
    print(
        "Input dependent values:\n"
        "Radius: %e, NumPart: %d, Angle: %e, Delta: %e\n"
        % (args.r, args.n, args.a, delta)
    )

    # print target information
    mass_targ_sim = mass_targ * n_targ_sim
    mass_targ_bound = mass_targ * n_targ_bound
    print(
        "Target number of simulation particles: %d\n"
        "Target simulation mass: %e\n"
        "Target number of boundary particles: %d\n"
        "Target boundary mass: %e\n\n"
        "Target total number of particles: %d\n"
        "Target total mass: %e\n"
        % (
            n_targ_sim,
            mass_targ_sim,
            n_targ_bound,
            mass_targ_bound,
            n_targ_sim + n_targ_bound,
            mass_targ_sim + mass_targ_bound,
        )
    )

    # write projectile simulation particles
    n_proj = print_particles(
        f,
        delta,
        shape_proj,
        r_inner_targ,
        r_outer_targ,
        x_proj_start,
        x_proj_stop,
        y_proj_start,
        y_proj_stop,
        z_proj_start,
        z_proj_stop,
        vx_proj,
        vy_proj,
        vz_proj,
        sin_phi,
        cos_phi,
        mass_proj,
        rho_proj,
        energy,
        mat_proj,
        flaws,
        damage,
        Sxx,
        Sxy,
        Sxz,
        Syx,
        Syy,
        Syz,
        Szx,
        Szy,
        Szz,
        alpha_jutzi_proj,
        pressure,
    )

    # close data file
    f.close()

    # print projectile information
    mass_proj = mass_proj * n_proj
    print(
        "Projectile number of particles: %d\n"
        "Projectile mass: %e\n" % (n_proj, mass_proj,)
    )


def print_particles(
    f,
    delta,
    shape_type,
    inner_radius,
    outer_radius,
    x_start,
    x_stop,
    y_start,
    y_stop,
    z_start,
    z_stop,
    vx,
    vy,
    vz,
    sin_phi,
    cos_phi,
    mass,
    rho,
    energy,
    mat,
    flaws,
    damage,
    Sxx,
    Sxy,
    Sxz,
    Syx,
    Syy,
    Syz,
    Szx,
    Szy,
    Szz,
    alpha_jutzi,
    pressure,
):
    # print particles to output file f
    # write data for cubical, cylindrical or hemispherical target
    n_particles = 0
    x_count = 0
    y_count = 0
    z_count = 0

    z = z_start
    while z <= z_stop:
        y = y_start
        # shift for hcp lattice
        if z_count % 4 == 1 or z_count % 4 == 2:
            y += 0.5 * delta
        while y <= y_stop:
            x = x_start
            # shift for hcp lattice
            if z_count % 4 == 1 or z_count % 4 == 3:
                x += delta * ROOT_TWO_THIRDS  # height of tetrahedon
            while x <= x_stop:
                # write particles within specified shape
                if shape_condition(shape_type, inner_radius, outer_radius, x, y, z):
                    x_print = x
                    y_print = y
                    z_print = z
                    # rotate particles of the cube
                    if shape_type == 0:
                        y_print, z_print = rotate_around_axis(y, z, sin_phi, cos_phi)
                    f.write(
                        "%e %e %e %e %e %e "
                        "%e %.10e %e %d %d %e "
                        "%e %e %e %e %e %e %e %e %e "
                        "%e %e\n"
                        % (
                            x_print,
                            y_print,
                            z_print,
                            vx,
                            vy,
                            vz,
                            mass,
                            rho,
                            energy,
                            mat,
                            flaws,
                            damage,
                            Sxx,
                            Sxy,
                            Sxz,
                            Syx,
                            Syy,
                            Syz,
                            Szx,
                            Szy,
                            Szz,
                            alpha_jutzi,
                            pressure,
                        )
                    )
                    # add up number of simulation particles
                    n_particles += 1
                # increment x1
                x += delta * 2 * ROOT_TWO_THIRDS
                x_count += 1
            # increment y1
            y += delta
            y_count += 1
        # increment z1
        z += delta * 0.25 * ROOT_THREE  # half height equilateral triangle
        z_count += 1
    return n_particles


def shape_condition(shape_type, inner_radius, outer_radius, x, y, z):
    # cube
    if shape_type == 0:
        return True
    # hemisphere
    elif shape_type == 1:
        return np.sqrt(pow(x, 2) + pow(y, 2) + pow(z, 2)) <= inner_radius
    # hemishperical shell
    elif shape_type == 2:
        return np.sqrt(pow(x, 2) + pow(y, 2) + pow(z, 2)) > inner_radius and (
            np.sqrt(pow(x, 2) + pow(y, 2) + pow(z, 2)) <= outer_radius
        )
    else:
        print("%d is not an accepted shape. Exiting.\n", shape_type)
        exit(1)


def rotate_around_axis(y, z, sin_phi, cos_phi):
    # rotate positions by impact angle around an axis
    y = cos_phi * y + sin_phi * z
    z = cos_phi * z - sin_phi * y
    return y, z


def particle_number_dryrun(delta, x_start, x_stop, y_start, y_stop, z_start, z_stop):
    # write data for cubical, cylindrical or hemispherical target
    n_particles = 0
    x_count = 0
    y_count = 0
    z_count = 0

    z = z_start
    while z <= z_stop:
        y = y_start
        # shift for hcp lattice
        if z_count % 4 == 1 or z_count % 4 == 2:
            y += 0.5 * delta
        while y <= y_stop:
            x = x_start
            # shift for hcp lattice
            if z_count % 4 == 1 or z_count % 4 == 3:
                x += delta * ROOT_TWO_THIRDS  # height of tetrahedon
            while x <= x_stop:
                n_particles += 1
                # increment x1
                x += delta * 2 * ROOT_TWO_THIRDS
                x_count += 1
            # increment y1
            y += delta
            y_count += 1
        # increment z1
        z += delta * 0.25 * ROOT_THREE  # half height equilateral triangle;
        z_count += 1
    return n_particles


def parse():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-n",
        help="Approximate Number of target simulation particles",
        type=float,
        default=1e5,
    )
    parser.add_argument("-r", help="Radius of hemisphere", type=float, default=12.0)
    parser.add_argument("-p", help="Porosity of target", type=float, default=0.5)
    parser.add_argument(
        "-a", help="Impact angle of projectile in degrees", type=float, default=0
    )
    args = parser.parse_args()
    return args


main()
