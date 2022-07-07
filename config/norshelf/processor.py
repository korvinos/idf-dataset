from pathlib import Path
from urllib.parse import urlunparse
from datetime import timedelta
import numpy as np
from utils import compute_scale_and_offset

AGGREGATED = True   
SCHEME = 'https'
NETLOCK = 'thredds.met.no'
PATH = Path('thredds/dodsC/sea_norshelf_his_ZDEPTHS_agg')
VARIABLES = ['time', 'u_eastward', 'v_northward', 'lat', 'lon']
DST_VARIABLES = ['time', 'u_eastward', 'v_northward']
DST = Path('./product/norshelf_idf')
IDF_FILENAME_SUFF = 'sea_norshelf_his_ZDEPTHS'
GCP_STEP = {'row': 10, 'cell': 10}
DIMENSIONS = {'depth': 0}
ROW_DIM_NAME = 'eta_rho'    # name of the equivalent to ROW dimension in the origianl dataset
CELL_DIM_NAME = 'xi_rho'    # name of the equivalent to CELL dimension in the origianl dataset
TIME_VAR_NAME = 'time'
LON_VAR_NAME = 'lon'
LAT_VAR_NAME = 'lat'
RESOLUTION = 2400   # spatial resolution in meters
DEPTH = 0

def return_url(**kwargs):
    return urlunparse((SCHEME, NETLOCK, PATH.__str__(), '', ','.join(VARIABLES), ''))

def process_data(src_dataset, dst_dataset, varname, **kwargs):
    band = dst_dataset.createVariable(varname, np.uint8, ('time', 'row', 'cell'), fill_value=-9999.)
    data = src_dataset[varname][kwargs['time_id'], DEPTH, :, :]
    scale, offset = compute_scale_and_offset(data)
    band.setncattr('scale_factor', scale)
    band.setncattr('add_offset', offset)
    band[:] = data
    for attrname in src_dataset[varname].ncattrs():
        if attrname not in ['_FillValue', '_ChunkSizes', 'grid_mapping', 
                            'add_offset', 'scale_factor']:
             band.setncattr(attrname, src_dataset[varname].getncattr(attrname))
    return band
    

