import numpy as np
import netCDF4 as nc
from config.idf_conf import IDF_BANDS, IDF_TIME_UNITS
from utils import gen_gcp_ids, generate_times
from cftime import date2num, num2pydate
from datetime import datetime, timedelta
from calendar import monthrange
import gc


time_start = datetime.now()

PRODUCT = 'MEPS'
START_DATE = datetime(2019, 7, 1, 0, 0, 0)

if PRODUCT == 'NORSHELF':
    from config.norshelf.processor import *
elif PRODUCT == 'MEPS':
    from config.meps.processor import *
elif PRODUCT == 'MYWAVE':
    from config.mywave.processor import *

DST.mkdir(exist_ok=True)
# Generate a list of timestamps for input files
n_hours = monthrange(START_DATE.year, START_DATE.month)[-1] * 24 + 1
src_times = generate_times(START_DATE, n_hours, TIME['output_step'])
i = 1

# Iterate through all files
for timestamp in src_times:
    # Iterate through all fields within the
    # try:
   #  ds = nc.Dataset(return_url(src_time=timestamp))
    # except OSError:
    #     print(f'{datetime.now() - time_start} ERROR')
    #     i += 1
    # print(return_url(src_time=timestamp))
   # print(ds[TIME_VAR_NAME])
#     for t_id in range(ds.dimensions[TIME_VAR_NAME].size): 
    for t_id in range(TIME['end_id'] - TIME['start_id']): 
        try:
            ds = nc.Dataset(return_url(src_time=timestamp))
        except OSError:
            print(f'{datetime.now() - time_start} ERROR')
            i += 1
            break

  #       ds = nc.Dataset(return_url(src_time=timestamp))
  #           raise ValueError
        # Convert field time to datetime object
        forecast_time = num2pydate(ds[TIME_VAR_NAME][t_id], ds[TIME_VAR_NAME].units)
        
        # if forecast_time != timestamp + timedelta(hours=t_id):
        #     raise ValueError
        
        # Generate idf file name
        idf_filename = f' {IDF_FILENAME_SUFF}_{forecast_time:%Y%m%dT%H}Z_idf_00.nc'
        print(f'{i:03d} | {timestamp:%Y-%m-%d %H:%M} | {forecast_time:%Y-%m-%d %H:%M} | {idf_filename}', end=' | ')
        idf_file_dst = DST / idf_filename
        # If file already exist then delete it before processing
        if idf_file_dst.exists():
            idf_file_dst.unlink()
        # Create clean nc file for idf formatted product
        data_idf = nc.Dataset(idf_file_dst, 'w', format='NETCDF4')
        # Create dimensions
        data_idf.createDimension('row', ds.dimensions[ROW_DIM_NAME].size)
        data_idf.createDimension('cell', ds.dimensions[CELL_DIM_NAME].size)
        data_idf.createDimension('time', 1)

    # if product_name == 'NORSHELF':
    #     time_id = np.where(ds['time'][:] == date2num(timestamp, ds['time'].units))[0][0]
    # else:
    #     time_id = HOUR
        
        for varname in DST_VARIABLES:
            if varname == 'time':
                band = data_idf.createVariable(varname, np.float32, ('time'))
                data = date2num(forecast_time, IDF_TIME_UNITS)
                band.units = IDF_TIME_UNITS
                band.long_name = 'time'
                band.standard_name = 'time'
                band.calendar = 'gregorian'
                band[:] = data
            else:
                band = process_data(ds, data_idf, varname, t_id)
        
        # Add IDF metadata                
        idf_meta = {
            'idf_version': 1.0,
            'idf_subsampling_factor': 0,
            'idf_spatial_resolution': RESOLUTION,
            'idf_spatial_resolution_units': 'm', 
            'idf_granule_id': idf_filename.replace('.nc', ''),
            'time_coverage_start': f'{forecast_time:%Y-%m-%dT%H:%M:%S}.000000Z',
            'time_coverage_end': f'{forecast_time + timedelta(minutes=59):%Y-%m-%dT%H:%M:%S}.000000Z'
        }

        for key, value in idf_meta.items():
            data_idf.setncattr(key, value)
            
        # Set GCP variablesds.dimensions[DATA_ROW_NAME].size)
        gcp_ids_row = gen_gcp_ids(data_idf.dimensions['row'].size, GCP_STEP['row'])
        gcp_ids_cell = gen_gcp_ids(data_idf.dimensions['cell'].size, GCP_STEP['cell'])
        data_idf.createDimension('row_gcp', len(gcp_ids_row))
        data_idf.createDimension('cell_gcp', len(gcp_ids_cell))
        for varname in IDF_BANDS.keys():
            band = data_idf.createVariable(
                varname, IDF_BANDS[varname]['datatype'], IDF_BANDS[varname]['dimensions'])
            if varname == 'lat_gcp':
                if PRODUCT == 'MYWAVE':
                    data = ds[LAT_VAR_NAME][:].T[gcp_ids_row, :][:, gcp_ids_cell]
                else:
                    data = ds[LAT_VAR_NAME][gcp_ids_row, :][:, gcp_ids_cell]
            elif varname == 'lon_gcp':
                if PRODUCT == 'MYWAVE':
                    data = ds[LON_VAR_NAME][:].T[gcp_ids_row, :][:, gcp_ids_cell]
                else:
                    data = ds[LON_VAR_NAME][gcp_ids_row, :][:, gcp_ids_cell]
            elif varname == 'index_row_gcp':
                data = gcp_ids_row.copy()
                data[-1] += 1
            elif varname == 'index_cell_gcp':
                data = gcp_ids_cell.copy()
                data[-1] += 1
            band[:] = data
            for attrname, attrvalue in IDF_BANDS[varname]['metadata'].items():
                band.setncattr(attrname, attrvalue)
        data_idf.close()
        print(f'{datetime.now() - time_start}')
        i += 1
