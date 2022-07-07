import numpy as np


IDF_TIME_UNITS = 'days since 1970-01-01 00:00:00.000000Z'
IDF_BANDS = {
    'lat_gcp': {
        'dimensions': ('row_gcp', 'cell_gcp'),
        'datatype': 'f4',
        'metadata': {
            'long_name': 'ground control points latitude',
            'standard_name': 'latitude',
            'units': 'degrees_north',
            'axis': 'Y',
            'comment': 'geographical coordinates, WGS84 projection'}},
    'lon_gcp': {
        'dimensions': ('row_gcp', 'cell_gcp'),
        'datatype': 'f4',
        'metadata': {
            'long_name': 'ground control points longitude',
            'standard_name': 'longitude',
            'units': 'degrees_east',
            'axis': 'X',
            'comment': 'geographical coordinates, WGS84 projection'}},
    'index_row_gcp': {
        'dimensions': ('row_gcp'),
        'datatype': np.int32,
        'metadata': {
            'long_name': 'index of ground control points in row dimension',
            'comment': 'index goes from 0 (start of first pixel) to dimension value (end of last pixel)'}},
    'index_cell_gcp': {
        'dimensions': ('cell_gcp'),
        'datatype': np.int32,
        'metadata': {
            'long_name': 'index of ground control points in cell dimension',
            'comment': 'index goes from 0 (start of first pixel) to dimension value (end of last pixel)'}},
}
