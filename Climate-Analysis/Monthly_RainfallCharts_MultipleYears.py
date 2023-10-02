import glob
import matplotlib.pyplot as plt
import xarray as xr
import os
import calendar
import pandas as pd
import datetime as dt
# import gcsfs
import geopandas as gpd
import rioxarray as rxr

Shape_file_path = 'C:/Users/LENOVO/OneDrive/Work/Python/DataAnalysis/DataAnalysis/Data/spatial-data/'
ERA5_files_path = 'D:/ERA5_Data/Pakistan/'

#Reading the shape file
gdf = gpd.read_file(Shape_file_path+'/Shapefiles/Pakistan.shp')

startyear = 2001
endyear = 2013

#Reading the nc file
nc_file  = xr.open_dataset(ERA5_files_path+'/ppt3.nc') #ppt1(1979-1990), ppt2(1991-2000), ppt3(2001-2012) ppt4(2013-2023)
# nc_file = nc_file.drop_vars('expver')
# tp_removed_dim = nc_file['tp'].isel(expver=0)
# nc_file['tp'] = tp_removed_dim

 # Set the CRS information for the NetCDF file
nc_file.rio.write_crs(gdf.crs, inplace=True)

# Clip the NetCDF file using the shapefile's geometry
clipped_ds = nc_file.rio.clip(gdf.geometry, gdf.crs)

clipped_ds = clipped_ds.drop_vars('spatial_ref')



for year in range(startyear,endyear):
    # date = f'{i}-01-01'
    # print(date)
    filtered_data = clipped_ds.sel(time=slice(f"{year}-01-01", f"{year}-12-31"))
    filtered_data
    ds_mon = filtered_data.resample(time='M').sum(skipna=True)
    ds_mon *= 1000

    # First, We will develop a land mask data array that we can use to mask out the nan values:
    landmask = ds_mon['tp'].sum(dim='time')>0
    data_edited = ds_mon['tp'].where(landmask)

    fig = plt.figure(figsize=[12,8], facecolor='w')
    plt.subplots_adjust(bottom=0.15, top=0.96, left=0.04, right=0.99, 
                        wspace=0.2, hspace=0.27) # wspace and hspace adjust the horizontal and vertical spaces, respectively.
    nrows = 3
    ncols = 4
    # plt.title('Monthly Precipitation sum for USA-2022')


    for i in range(1, 13):
        plt.subplot(nrows, ncols, i)
        dataplot = data_edited[i-1, :, :].where(landmask) # Remember that in Python, the data index starts at 0, but the subplot index start at 1.
        p = plt.pcolormesh(dataplot.longitude, dataplot.latitude, dataplot,
                    vmax = 600, vmin = 0, cmap = 'nipy_spectral_r',
                    ) 
        # plt.xlim([230,300])
        # plt.ylim([20,50])
        plt.title(calendar.month_name[i], fontsize = 13, 
                fontweight = 'bold', color = 'b')
        plt.xticks(fontsize = 11)
        plt.yticks(fontsize = 11)
        if i % ncols == 1: # Add ylabel for the very left subplots
            plt.ylabel('Latitude', fontsize = 11, fontweight = 'bold')
        if i > ncols*(nrows-1): # Add xlabel for the bottom row subplots
            plt.xlabel('Longitude', fontsize = 11, fontweight = 'bold')

    # Add a colorbar at the bottom:
    cax = fig.add_axes([0.25, 0.06, 0.5, 0.018])
    cb = plt.colorbar(cax=cax, orientation='horizontal', extend = 'max',)
    cb.ax.tick_params(labelsize=11)
    cb.set_label(label='Precipitation (mm)', color = 'k', size=14)
    # Add a label at the bottom
    fig.text(0.9, 0.03, f'Year ={year} ', fontsize=14, ha='center')
    plt.savefig(ERA5_files_path+f'year_{year}_plot.png')

