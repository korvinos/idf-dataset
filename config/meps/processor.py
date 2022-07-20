from pathlib import Path
from urllib.parse import urlunparse
from datetime import timedelta
import numpy as np
from config.norshelf.processor import AGGREGATED
from utils import compute_scale_and_offset, lcc_grid_convergence_angle
from seadoppler.utils.vector import direction_from, uv_components


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

TIME = {
    'output_step': 6,   # timestep of src product outputs (e.g every 6 hours motel output) None for aggregated files 
    'start_id': 0,      # Id of the first time stamp to be extracted from the src file
    'end_id': 6,        # Id + 1 of last time stamp to me extracted from the src file
    'step': 1,     # Time step of extracted files (e.g. 1 for every hour between <start_id> and <end_id>)
}
FILE_HOUR = 6 # Time step of the files in output (e.g. one file every 6 hours)

HOUR_START = 0 # ID of start hour extracted from the datset
HOUR_END = 6 # ID of end hour extracted from the dataset
ESNEMBLE_MEMBER = 0 # Determenistic
HEIGHT = 0 # DUMMY ID (only one height is available in target datasets)
GCA = None # Grid convergence angle
VAR5D = f'[{TIME["start_id"]}:{TIME["step"]}:{TIME["end_id"]}][{HEIGHT}][{ESNEMBLE_MEMBER}][0:{Y}][0:{X}]'
VARIABLES = [f'time[{TIME["start_id"]}:{TIME["step"]}:{TIME["end_id"]}]',
             'latitude', 'longitude', 'projection_lambert', 'x', 'y', f'x_wind_10m{VAR5D}', f'y_wind_10m{VAR5D}']
DST_VARIABLES = ['time', 'u10m', 'v10m']


def return_url(**kwargs):
    # Gen src file dataname (all data in separate files)
    filename = f'meps_subset_2_5km_{kwargs["src_time"]:%Y%m%dT%H}Z.nc'
    file_path = PATH / f'{kwargs["src_time"]:%Y/%m/%d}' / filename
    return urlunparse((SCHEME, NETLOCK, file_path.__str__(), '', ','.join(VARIABLES), ''))


def process_data(src_dataset, dst_dataset, varname, time_id):
    GCA = lcc_grid_convergence_angle(
        longitude=src_dataset[LON_VAR_NAME][:].data,
        central_meridian=src_dataset['projection_lambert'].longitude_of_central_meridian,
        central_latitude=src_dataset['projection_lambert'].latitude_of_projection_origin
    )
    wind_speed = np.hypot(src_dataset['y_wind_10m'][time_id, 0, 0, :, :], src_dataset['x_wind_10m'][time_id, 0, 0, :, :])
    wind_dir_model = direction_from(src_dataset['y_wind_10m'][time_id, 0, 0, :, :], src_dataset['x_wind_10m'][time_id, 0, 0, :, :])
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
