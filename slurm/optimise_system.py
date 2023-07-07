import argparse

import exoplanet as xo
import lightkurve as lk
import astropy.units as u
import matplotlib.pyplot as plt
import numpy as np

import os
import sys
sys.path.append('../helpers')
import data
import xo_archive
import fit

from astropy.time import Time

def main():
    parser = argparse.ArgumentParser(description='Optimise the parameters of an exoplanet system')
    parser.add_argument('-s', '--system_id', default=0, type=int,
                        help='ID of the system that you want to fit')
    parser.add_argument('-f', '--file_name', default="systems.txt", type=str,
                        help='File containing list of systems and IDs')
    parser.add_argument('-o', '--output_folder', default=".", type=str,
                        help='Path to folder in which to place output')
    parser.add_argument('-m', '--mission', default="Kepler", type=str,
                        help='Which mission to get observations from')
    parser.add_argument('-e', '--exp_time', default=1800, type=int,
                        help='Exposure time data to select')
    args = parser.parse_args()

    matched_name = None
    with open(args.file_name, "r") as f:
        for line in f:
            sys_id, sys_name = line.split(",")
            if int(sys_id) == args.system_id:
                matched_name = sys_name.replace("\n", "")
                break

    if matched_name is None:
        raise ValueError("Unknown system ID")
    
    print(f"Running optimisation for system: {matched_name}")

    # Collect the planetary parameters with xo_archive
    # composite values are collected (keep track of where for stellar)
    planet_parameters = xo_archive.get_exoplanet_parameters(matched_name, which="composite")
    n_planets = len(planet_parameters)

    # Create a list of all the parameters in the system
    param_lists = xo_archive.transpose_parameters(planet_parameters)

    print("Found initial parameters for the systems:")
    print(planet_parameters)

    flat_lc = data.get_flattened_lc(matched_name, mission=args.mission, exptime=args.exp_time)

    # Remove Outliers
    lc = data.remove_outliers(flat_lc, param_lists["pl_orbper"], param_lists["pl_tranmid"],
                              param_lists["pl_trandur"], transit_sigma_upper=5)

    # Folded light curves are created here
    # for i in range(len(planet_parameters)):
    #     lc.fold(period=planet_parameters[i]["pl_orbper"],
    #             epoch_time=Time(planet_parameters[i]["pl_tranmid"] * u.day, format="jd").bkjd).scatter(label=planet_parameters[i]["pl_name"])

    print("Lightcurve retrieved, flattened and outliers removed, commencing fit...")

    # create list of new parameters based on given parameters
    map_soln, model = fit.optimise_model(lc, param_lists)

    np.save(os.path.join(args.output_folder, f"{matched_name.rstrip()}-opt-params-1.py"), map_soln)

    # Re-optimizing the parameters: "new_soln_1"
    updated_params = {}
    updated_params["pl_orbper"] = map_soln["period"]
    updated_params["pl_tranmid"] = Time(map_soln["t0"], format="bkjd").jd
    updated_params["pl_ratror"] = map_soln["r"]
    updated_params["pl_imppar"] = map_soln["b"]
    updated_params["berger_dens"] = [map_soln["rho_star"]]
    new_soln_1, model = fit.optimise_model(lc, updated_params, u_init=map_soln["u"])

    np.save(os.path.join(args.output_folder, f"{matched_name.rstrip()}-opt-params-2.py"), new_soln_1)
    
    # Re-optimizing the parameters: "new_soln_2"
    updated_params = {}
    updated_params["pl_orbper"] = new_soln_1["period"]
    updated_params["pl_tranmid"] = Time(new_soln_1["t0"], format="bkjd").jd
    updated_params["pl_ratror"] = new_soln_1["r"]
    updated_params["pl_imppar"] = new_soln_1["b"]
    updated_params["berger_dens"] = [new_soln_1["rho_star"]]
    new_soln_2, model = fit.optimise_model(lc, updated_params, u_init=new_soln_1["u"])

    np.save(os.path.join(args.output_folder, f"{matched_name.rstrip()}-opt-params-3.py"), new_soln_2)

    print("Fitting complete!")

    # Optimized LC
    t = lc["time"].value
    y = lc["flux"].value
    for i in range(n_planets):
        plt.figure()
        p = new_soln_2["period"][i]
        t0 = new_soln_2["t0"][i]

        # Plot the folded data
        x_fold = (t - t0 + 0.5 * p) % p - 0.5 * p
        plt.scatter(
            x_fold, y, label="data", zorder=-1000, s=0.1, color="black"
        )
        # Plot the folded model within 0.3 days of the transit
        inds = np.argsort(x_fold)
        inds = inds[np.abs(x_fold)[inds] < 0.3]
        pred = new_soln_2["light_curves"][inds, i] + new_soln_2["mean"]
        plt.plot(x_fold[inds], pred, color="firebrick", label="optimised model")
        plt.ylabel("relative flux")
        plt.xlabel("time [days]")
        _ = plt.xlim(t.min(), t.max())
        plt.legend(fontsize=10, loc=4)
        plt.xlim(-0.5 * p, 0.5 * p)
        plt.xlabel("Time since transit [days]")
        plt.ylabel("Relative flux")
        plt.title(param_lists["pl_name"][i])
        plt.xlim(-0.3, 0.3)
        plt.savefig(os.path.join(args.output_folder, f"{matched_name.rstrip()}-opt-fit-{param_lists['pl_name'][i]}.pdf"),
                    format="pdf", bbox_inches="tight")
        plt.show()

if __name__ == "__main__":
    main()