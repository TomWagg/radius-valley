import lightkurve as lk
import astropy.units as u
import numpy as np

from astropy.time import Time


def get_flattened_lc(name, mission=None, exptime=None):
    # search for relevant data
    search_results = lk.search_targetpixelfile(name, mission=mission, exptime=exptime)

    # download the related TargetPixelFiles
    tpfs = search_results.download_all()

    # convert TPFs to light curves using Pixel Level Decorrelation
    lcs = [tpf.to_lightcurve(method="pld") for tpf in tpfs]

    # collect light curves together
    lcc = lk.LightCurveCollection(lightcurves=lcs)

    # switch the collection and flatten it
    flat_lc = lcc.stitch().flatten()
    return flat_lc


def remove_outliers(lc, periods, t0s, durations, regular_sigma=5, transit_sigma=5.6, transit_sigma_upper=1):
    # get two outlier masks, one more lenient than the other 
    _, outlier_mask = lc.remove_outliers(return_mask=True, sigma=regular_sigma)
    _, extreme_outlier_mask = lc.remove_outliers(return_mask=True, sigma=transit_sigma,
                                                 sigma_upper=transit_sigma_upper)

    # count the number of planets in transit per timestep
    total_in_transit = np.zeros(len(lc.time))
    for p, t0, t_duration in zip(periods, t0s, durations):
        phase = (lc.time - Time(t0, format="jd")).to(u.day).value % p
        half_transit = 0.5 * (t_duration * u.hour).to(u.day).value
        in_transit = (phase < half_transit) | (phase > p - half_transit)
        total_in_transit += in_transit.astype(int)

    # get a mask for whether there are *any* planets in transit
    any_in_transit = total_in_transit > 0

    # combine them into masks
    no_extreme_outliers_ever = ~extreme_outlier_mask
    no_regular_outliers_outside_transit = ~(outlier_mask & (~any_in_transit))

    # return the fully masked lc
    return lc[no_extreme_outliers_ever & no_regular_outliers_outside_transit]