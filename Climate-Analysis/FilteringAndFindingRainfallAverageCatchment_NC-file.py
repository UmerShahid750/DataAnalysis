import xarray as xr
import os
import pandas as pd


#replace the folder path to where the files are present
folder = 'D:/ERA5_Data/Pakistan/'
files = os.listdir(folder)

#Enter the bounds of the region
min_lon = 71.10
min_lat = 32.17
max_lon = 71.98
max_lat = 33.24

df1 = pd.DataFrame()
for file in files:
    #Check for reading precipitation files only
    if str(file).__contains__('ppt'):
        #creating path of file
        path = os.path.join(folder,file)
        print(path)
        data = xr.open_dataset(path)
        #Filtering the dataset to the bounds of the region
        data_filtered = data.sel(latitude=slice(max_lat,min_lat), longitude=slice(min_lon,max_lon))
        df = data_filtered.to_dataframe().reset_index()
        #creating a date column from time values of dataframe
        df['date'] = pd.to_datetime(df['time']).dt.date
        #Finding sum of rainfall at one location for a single day
        rainfall = df.groupby(['date','longitude','latitude'],as_index=False)['tp'].sum()
        #averaging the rainfall for cathcmment average over a single day
        rainfall = rainfall.groupby(['date'],as_index=False)['tp'].mean()
        #adding the data to another dataframe (use concat function if append does not work)
        df1 = df1.append([rainfall], ignore_index=True)

df1['tp in mm'] = df1['tp']*1000
df1.drop('tp', inplace=True, axis=1)

# df1.to_csv(folder+'/cathcment_average.csv')


