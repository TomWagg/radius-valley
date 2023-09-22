import lightkurve as lk
import astropy.units as u
import numpy as np

from astropy.time import Time


def get_flattened_lc(name, mission=None, exptime=None):
    """Returns stitched and flattened light curve of a target using MAST data archive 

    Parameters
    ----------
    name : `str`
        Target name. Can be name of system, e.g. "Kepler-109", or particular planet, e.g. "Kepler-109 b"
    mission : `str` 
        Which mission to download data from, e.g. "Kepler", "K2", or "TESS"
    exptime : `int` or "long", "short", "fast", optional 
           Exposure time of desired data products. "long" selects 10 minute and 30 minute data products, 
           "short" selects 1 and 2 minute data, and "fast" selects 20 second data. Can also pass an int of the 
           exact exposure time in seconds. 
           For example, exptime=1800 calls for 30 minute data products. 
           By default, all cadence modes are returned (this may make it timeout). 

    Returns
    -------
    flat_lc : `lightkurve LightCurve object`
        Stitched and flattened light curve 
    """     
    # Search MAST data archive for target pixel files
    search_results = lk.search_targetpixelfile(name, mission=mission, exptime=exptime)

    # download the related TargetPixelFiles
    tpfs = search_results.download_all()

    # convert TPFs to light curves using Pixel Level Decorrelation
    lcs = [tpf.to_lightcurve(method="pld") for tpf in tpfs]

    # collect light curves together
    lcc = lk.LightCurveCollection(lightcurves=lcs)

    # stitch the collection into a single light curve
    # and flatten it (removes long-term trends using scipy’s Savitzky-Golay filter)
    flat_lc = lcc.stitch().flatten()
    return flat_lc


def remove_outliers(lc, periods, t0s, durations, regular_sigma=5, transit_sigma=5.6, transit_sigma_upper=5):
    """Removes outliers from light curve using sigma clipping (removing flux values that are greater or smaller 
    than the median value by a number of standard deviations). Removes the most extreme outliers from the entire light curve, 
    and removes "less extreme" outliers as long as there is no planet transiting. 

    Parameters
    ----------
    lc : :class:`~lightkurve.Lightcurve` 
        Stitched light curve of planetary system to remove outliers from 
    
    periods : `list`
        A list of orbital periods (in days) of each planet in the system 
    
    t0s : `list`
        A list of transit midpoints (in Julian dates) of each planet in the system 
    
    durations : `list`
        A list of transit durations (in hours) of each planet in the system 
    
    regular_sigma : `float`
        The number of standard deviations for both upper and lower clipping limit while no planet is transiting. Default is 5. 
    
    transit_sigma : `float`
        The number of standard deviations for clipping limit during entire light curve (whether planet is transiting or not), to 
        catch the most obvious outliers. Default is 5.6 (more leniant than regular_sigma). Overrided by transit_sigma_upper for 
        upper clipping limit. 
    
    transit_sigma_upper : `float`
        The number of standard deviations for upper clipping limit during entire light curve (whether planet is transiting or 
        not), to catch the most obvious outliers. Default is 5 (more strict than transit_sigma because planets do not cause flux
        values to go above median flux). 

    Returns
    -------
    new_lc : :class:`~lightkurve.Lightcurve`
        Light curve with extreme outliers removed during entire series and less extreme outliers removed outside of when 
        a planet is transiting. 
    """ 
    # get two outlier masks, one more lenient than the other 
    # returns points that have been removed 
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
    new_lc = lc[no_extreme_outliers_ever & no_regular_outliers_outside_transit]
    return new_lc