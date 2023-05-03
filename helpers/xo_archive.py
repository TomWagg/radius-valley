from requests import request
from collections import defaultdict

BASE_URL = "https://exoplanetarchive.ipac.caltech.edu/TAP/sync?query=select+"

def get_exoplanet_parameters(search_name, which="default", custom_cond=None,
                             columns=["pl_name", "pl_letter", "pl_orbper", "pl_orbincl", "pl_orbeccen",
                                      "pl_trandep", "pl_tranmid", "pl_trandur", "pl_ratror",
                                      "pl_imppar", "st_dens"]):
    """Get parameters for exoplanets from the Exoplanet Archive using their TAP service

    See here for more information: https://exoplanetarchive.ipac.caltech.edu/docs/TAP/usingTAP.html

    Parameters
    ----------
    search_name : `str`
        Substring against which to match the planet name, e.g. "Kepler-5 " <- the space is important so you
        just get Kepler-5 and not Kepler-50 or Kepler-503 etc. Leave as `None` to ignore name conditions.
    which : `str`, optional
        Which table of parameters to draw from, one of ["default", "all", "composite"]. The default parameters
        are from a single paper that is currently flagged as the main reference. "all" will give you many rows
        for each planet, one row per publication per planet. "composite" combines the known parameters from
        many papers into a single row - NOTE composite values may not be self-consistent. By default "default"
    custom_cond : `str`, optional
        Custom condition against which to match, by default None
    columns : `list`, optional
        Which columns to select from the tables. See here:
        https://exoplanetarchive.ipac.caltech.edu/docs/API_PS_columns.html for a list of potential choices.
        Note the columns are different for the "all" and "composite".
        By default ["pl_name", "pl_letter", "pl_orbper", "pl_orbincl", "pl_orbeccen", "pl_trandep",
                    "pl_tranmid", "pl_trandur", "pl_ratror", "pl_imppar", "st_dens"]

    Returns
    -------
    parameters : `list`
        A list of dictionaries, each corresponding to a row from the table

    Examples
    --------
    A query for the composite parameters of the Kepler-444 system::
        get_exoplanet_parameters("Kepler-444 ", which="composite")

    A query for the default parameters of the Kepler-29 system::
        get_exoplanet_parameters("Kepler-29 ")

    A query for the default parameters of just Kepler-9b::
        get_exoplanet_parameters("Kepler-9 ", custom_cond="pl_letter='b'")
    """
    # decide which table to pull from
    table = "ps" if which in ["default", "all"] else "pscomppars"
    from_table = f" from {table} where "

    # specify conditions on the planet name and whether to get the default parameters
    name_cond = f"lower(pl_name)+like+'%{search_name.lower()}%'" if search_name is not None else ""
    default_cond = "default_flag=1" if which == "default" else ""
    if search_name is not None and which == "default":
        default_cond = " and " + default_cond

    # add a custom condition if desired
    if custom_cond is not None:
        default_cond += f" and {custom_cond}"

    # force the format to be JSON
    fmt = "&format=JSON"

    # combine into URL and perform the request
    url = BASE_URL + ','.join(columns) + from_table + name_cond + default_cond + fmt
    r = request(method="GET", url=url)

    # print out an error if it failed, otherwise return the JSON
    if r.status_code != 200:
        print(f"Request failed with code {r.status_code}: Error message follows")
        print("=======================================================")
        print(r.text.rstrip())
        print("=======================================================")
        print(f"URL used: {url}")
    else:
        return r.json()


def transpose_parameters(parameters):
    """Transform a list of dictionaries of parameters into a dictionary of lists

    Parameters
    ----------
    parameters : `list`
        List of dictionaries of parameters

    Returns
    -------
    transposed : `dict`
        Dictionary of columns, each of which are a list of values (one for each planet)
    """
    transposed = defaultdict(list)
    keys = parameters[0].keys()
    for i in range(len(parameters)):
        for key in keys:
            transposed[key].append(parameters[i][key])
    return dict(transposed)