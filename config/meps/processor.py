from pathlib import Path
from urllib.parse import urlunparse
from datetime import timedelta
import numpy as np
from config.norshelf.processor import AGGREGATED
from utils import compute_scale_and_offset, lcc_grid_convergence_angle
from seadoppler.utils.vector import direction_from, uv_components


AGGREGATED = False
SCHEME = 'https'
NETLOCK = 'thredds.met.no'
PATH = Path('thredds/dodsC/meps25epsarchive')
DST = Path('./product/meps_idf')
IDF_FILENAME_SUFF = 'meps_subset_2_5km'
GCP_STEP = {'row': 10, 'cell': 10}
ROW_DIM_NAME = 'y'    # name of the equivalent to ROW dimension in the origianl dataset
CELL_DIM_NAME = 'x'    # name of the equivalent to CELL dimension in the origianl dataset
TIME_VAR_NAME = 'time'
LON_VAR_NAME = 'longitude'
LAT_VAR_NAME = 'latitude'
RESOLUTION = 2500   # spatial resolution in meters
# Grid constants
X = 888
Y = 948
HOUR = 4 # Number of hours extracted from the dataset
ESNEMBLE_MEMBER = 0 # Determenistic
HEIGHT = 0 # DUMMY ID (only one height is available in target datasets)
GCA = None # Grid convergence angle
VAR5D = f'[0:{HOUR}][{HEIGHT}][{ESNEMBLE_MEMBER}][0:{Y}][0:{X}]'
VARIABLES = [f'time[0:{HOUR}]', 'latitude', 'longitude', 'projection_lambert',
             'x', 'y', f'x_wind_10m{VAR5D}', f'y_wind_10m{VAR5D}']
DST_VARIABLES = ['time', 'u10m', 'v10m']

def return_url(**kwargs):
    # Gen src file dataname (all data in separate files)
    filename = f'meps_subset_2_5km_{kwargs["src_time"]:%Y%m%dT%H}Z.nc'
    file_path = PATH / f'{kwargs["src_time"]:%Y/%m/%d}' / filename
    return urlunparse((SCHEME, NETLOCK, file_path.__str__(), '', ','.join(VARIABLES), ''))


def process_data(src_dataset, dst_dataset, varname, **kwargs):
    GCA = lcc_grid_convergence_angle(
        longitude=src_dataset[LON_VAR_NAME][:].data,
        central_meridian=src_dataset['projection_lambert'].longitude_of_central_meridian,
        central_latitude=src_dataset['projection_lambert'].latitude_of_projection_origin
    )
    wind_speed = np.hypot(src_dataset['y_wind_10m'][0, 0, 0, :, :], src_dataset['x_wind_10m'][0, 0, 0, :, :])
    wind_dir_model = direction_from(src_dataset['y_wind_10m'][0, 0, 0, :, :], src_dataset['x_wind_10m'][0, 0, 0, :, :])
    wind_direction = (wind_dir_model + GCA) % 360
    # import ipdb; ipdb.set_trace()
    u, v = uv_components(wind_speed, wind_direction, 'meteo')
    
    if varname == 'u10m':
        band = dst_dataset.createVariable(varname, np.uint8, ('time', 'row', 'cell'), fill_value=-9999.)
        data = u[:]
        scale, offset = compute_scale_and_offset(data)
        band.setncattr('scale_factor', scale)
        band.setncattr('add_offset', offset)
        band[:] = data
        band.units = "m/s" 
    elif varname == 'v10m':
        band = dst_dataset.createVariable(varname, np.uint8, ('time', 'row', 'cell'), fill_value=-9999.)
        data = v[:]
        scale, offset = compute_scale_and_offset(data)
        band.setncattr('scale_factor', scale)
        band.setncattr('add_offset', offset)
        band[:] = data
        band.units = "m/s" 
