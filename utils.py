import numpy as np
from datetime import timedelta

def gen_gcp_ids(size, step):
    # NOTE: last gcp id should be the last row or cell
    gcp_ids = list(np.arange(0, size, step)) + [size - 1]
    return gcp_ids


def compute_scale_and_offset(arr):
    scale_factor = (arr.max() - arr.min()) / 255. 
    add_offset = arr.min()
    return scale_factor, add_offset


def generate_times(timestart, n_hours, delta):
    return [timestart + timedelta(hours=n) for n in range(0, n_hours, delta)]


def lcc_grid_convergence_angle(longitude, central_meridian=-25., central_latitude=77.5):
    """Calculate grid convergence angle for the Lambert Conic Conformal (LCC)
    projection

    Parameters
    ----------
    longitude: float
        Longitude of the grid point from the LCC domain
    central_meridian: float
        Central meridial of the LCC grid projection
    central_latitude: float
        Standard parallel of the LCC grid projection
    
    Returns
    ------
    azimuth: float
        Deviation of the LCC domain from the true north
    """
    azimuth = np.sin(np.deg2rad(central_latitude)) * (longitude - central_meridian)
    return azimuth
