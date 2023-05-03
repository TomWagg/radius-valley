import exoplanet as xo
import lightkurve as lk
import astropy.units as u
import matplotlib.pyplot as plt
import numpy as np

from astropy.time import Time

import pymc3 as pm
import pymc3_ext as pmx

def optimise_model(lc, initial_guesses, texp=0.5 / 24, u_init=[0.3, 0.2]):
    n_planets = len(initial_guesses["pl_orbper"])
    t0s_bkjd = Time(initial_guesses["pl_tranmid"], format="jd").bkjd

    with pm.Model() as model:

        # The baseline flux
        mean = pm.Normal("mean", mu=1.0, sd=1.0)

        # The time of a reference transit for each planet
        t0 = pm.Normal("t0", mu=t0s_bkjd, sd=1.0, shape=n_planets)

        # The log period; also tracking the period itself
        logP = pm.Normal("logP", mu=np.log(initial_guesses["pl_orbper"]), sd=0.1, shape=n_planets)
        period = pm.Deterministic("period", pm.math.exp(logP))

        # The Kipping (2013) parameterization for quadratic limb darkening parameters
        limb_dark = xo.distributions.QuadLimbDark("u", testval=u_init)

        r = pm.Uniform(
            "r", lower=0.001, upper=0.1, shape=n_planets, testval=initial_guesses["pl_ratror"]
        )
        b = xo.distributions.ImpactParameter(
            "b", ror=r, shape=n_planets, testval=initial_guesses["pl_imppar"]
        )

        # fix stellar density across the stars
        log_rho_star = pm.Normal("log_rho_star",
                                mu=np.log10(initial_guesses["st_dens"][0]), sd=1)
        rho_star = pm.Deterministic("rho_star", 10**(log_rho_star))

        # Set up a Keplerian orbit for the planets
        orbit = xo.orbits.KeplerianOrbit(period=period, t0=t0, b=b, rho_star=rho_star)

        # Compute the model light curve using starry
        light_curves = xo.LimbDarkLightCurve(limb_dark[0], limb_dark[1]).get_light_curve(
            orbit=orbit, r=r, t=lc["time"].value, texp=texp
        )
        light_curve = pm.math.sum(light_curves, axis=-1) + mean

        # Here we track the value of the model light curve for plotting purposes
        pm.Deterministic("light_curves", light_curves)

        # The likelihood function assuming known Gaussian uncertainty
        pm.Normal("obs", mu=light_curve, sd=lc["flux_err"].value, observed=lc["flux"].value)

        # Fit for the maximum a posteriori parameters given the simulated dataset
        map_soln = pmx.optimize(start=model.test_point)

        return map_soln