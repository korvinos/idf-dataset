from pathlib import Path
from urllib.parse import urlunparse
from itertools import product
import numpy as np
from utils import compute_scale_and_offset


def _build_data_name(params):
    var3d = f'[{TIME["start_id"]}:{TIME["step"]}:{TIME["end_id"]}][0:1:{Y}][0:1:{X}]'
    return f'{params[0]}_{params[1]}{var3d}' if params[1] != '' else f'{params[0]}{var3d}'


AGGREGATED = False
SCHEME = 'https'
NETLOCK = 'thredds.met.no'
PATH = Path('thredds/dodsC/fou-hi/mywavewam4archive')
DST = Path('./product/mywave_idf')
IDF_FILENAME_SUFF = 'MyWave_wam4_WAVE_'
GCP_STEP = {'row': 10, 'cell': 10}
ROW_DIM_NAME = 'y'    # name of the equivalent to ROW dimension in the origianl dataset
CELL_DIM_NAME = 'x'    # name of the equivalent to CELL dimension in the origianl dataset
TIME_VAR_NAME = 'time'
LON_VAR_NAME = 'longitude'
LAT_VAR_NAME = 'latitude'
RESOLUTION = 4000   # spatial resolution in meters
X = 623
Y = 1025
TIME = {
    'output_step': 6,   # timestep of src product outputs (e.g every 6 hours motel output) None for aggregated files 
    'start_id': 6,      # Id of the first time stamp to be extracted from the src file
    'end_id': 12,        # Id + 1 of last time stamp to me extracted from the src file
    'step': 1,     # Time step of extracted files (e.g. 1 for every hour between <start_id> and <end_id>)
}
ROW_DIM_NAME = 'rlon'    # name of the equivalent to ROW dimension in the origianl dataset
CELL_DIM_NAME = 'rlat'    # name of the equivalent to CELL dimension in the origianl dataset

data_var_list = product(['hs', 'tmp', 'thq'], ['', 'sea', 'swell'])
meta_var_list = [f'time[{TIME["start_id"]}:{TIME["step"]}:{TIME["end_id"]}]', 'latitude', 'longitude', 'projection_3', 'depth']
data_var_query = [_build_data_name(name) for name in data_var_list] 
VARIABLES = data_var_query + meta_var_list
DST_VARIABLES = ['time', 'hs', 'tmp', 'hs_sea', 'hs_swell', 'depth']


def return_url(**kwargs):
    # create filename based on the 
    filename = f'MyWave_wam4_WAVE_{kwargs["src_time"]:%Y%m%dT%H}Z.nc'
    file_path = PATH / f'{kwargs["src_time"]:%Y/%m/%d}' / filename
    return urlunparse((SCHEME, NETLOCK, file_path.__str__(), '', ','.join(VARIABLES), ''))


def process_data(src_dataset, dst_dataset, varname, time_id):
    band = dst_dataset.createVariable(varname, np.uint8, ('time', 'row', 'cell'), fill_value=-9999.)
    if varname == 'depth':
        a = src_dataset[varname][:].T
        mask = np.isnan(a)
        a[mask] = -9999.
        data = np.ma.masked_array(
            data=a, mask=mask, fill_value=-9999.)
    else:
        data = src_dataset[varname][time_id, :, :].T # np.moveaxis(ds[varname][:], [1, 2], [2, 1])
    scale, offset = compute_scale_and_offset(data)
    band.setncattr('scale_factor', scale)
    band.setncattr('add_offset', offset)
    band[:] = data
    
