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

ds_year = clipped_ds.resample(time='Y').sum(skipna=True)
ds_year *= 1000

# First, We will develop a land mask data array that we can use to mask out the nan values:
landmask_year = ds_year['tp'].sum(dim='time')>0
data_edited_year = ds_year['tp'].where(landmask_year)
print(data_edited_year)

index = 0
for year in range(startyear, endyear):
    # Select data for the current year
    data_edited_year = ds_year['tp'].where(landmask_year).sel(time=str(year))

    # Create a subplot
    plt.figure(figsize=(8, 6))
    # plt.subplot(1, 1, 1)  # You can adjust the subplot layout as needed

    # Plot the data for the current year
    p = data_edited_year.plot(cmap='jet', vmax=1600)

    # Customize subplot title and labels as needed
    plt.title(f'Year {year}', fontsize=13, fontweight='bold', color='b')
    plt.xlabel('Longitude', fontsize=11, fontweight='bold')
    plt.ylabel('Latitude', fontsize=11, fontweight='bold')

    # Add colorbar
    # cbar = plt.colorbar(p, shrink=0.75, label='Precipitation (mm)')
    # Save or show the subplot
    plt.savefig(ERA5_files_path+f'year_{year}_plot.png')  # Save the plot as an image file
    # plt.show()

