import pandas as pd
import numpy as np
import rasterio
import fiona
from rasterio.mask import mask
from rasterio.features import shapes
from shapely.geometry import shape, mapping, MultiPolygon, Polygon
import geopandas as gpd
from shapely.ops import unary_union

crop_shapefile_path = 'C:/Data/Crop classification/Vehari/Harvest Check/Region2/Python/Maize.shp'
raster_file_path = 'C:/Data/Crop classification/Vehari/Harvest Check/Region2/Python/NDVI.tif'
output_file_path = 'C:/Data/Crop classification/Vehari/Harvest Check/Region2/Python/check/output_harvested_ndvi.tif'
output_shapefile_path = 'C:/Data/Crop classification/Vehari/Harvest Check/Region2/Python/check/output_harvested_polygons.shp'
output_excel_path = 'C:/Data/Crop classification/Vehari/Harvest Check/Region2/Python/check/output_harvested_polygons.xlsx'

def crop_harvest_alert(crop_shapefile_path, raster_file_path, output_file_path, output_shapefile_path):
    with rasterio.open(raster_file_path) as rasterBand:
        #reading the crop shapefile
        crop = fiona.open(crop_shapefile_path,"r")
        #creating list of polygons in the shape file
        shapes_1 = [feature["geometry"] for feature in crop]
        #clipping the raster tile with the farm polygons
        outImage, outTransform = mask(rasterBand,shapes_1, crop=True, all_touched = True)
        outMeta = rasterBand.meta
        outMeta.update({"driver": "GTiff","height": outImage.shape[1],"width": outImage.shape[2],"transform": outTransform})
        ndvi_masked = np.where((0 < outImage) & (outImage < 0.2), outImage, np.nan)

    with rasterio.open(output_file_path, "w", **outMeta) as src:
        src.write(ndvi_masked)
        #readingt the transformation matrix of the original file
        transform_1 = src.transform
        #vectorizing the raster file and converting into a list
        vectorized_shapes = list(shapes(ndvi_masked, mask=None, transform=transform_1))

        merged_shapes = []  # List to store merged shapes

        #Finding the harvested polygons
        for shape_info, value in vectorized_shapes:
            if 0 <= value <= 0.2:
                shape_object = shape(shape_info)
                if isinstance(shape_object, Polygon):
                    merged_shapes.append({'geometry': shape_object, 'value': value})

        # Create a GeoDataFrame with a single row containing the merged geometry
        gdf_merged = gpd.GeoDataFrame(merged_shapes, crs='4326')

        # Set the geometry column for the GeoDataFrame
        gdf_merged.set_geometry('geometry', inplace=True)

        #Reading the maize crop file
        file1 = gpd.read_file(crop_shapefile_path)

        # Perform intersection
        intersection_result = gpd.overlay(file1, gdf_merged, how='intersection') 

        # Dissolve the intersection result based on the 'ID' attribute
        dissolved_result = intersection_result.dissolve(by='ID')

        #changing the coordinate system to UTM calculate the area in meters
        dissolved_result = dissolved_result.to_crs(epsg=32642)
        # Calculate area in acres and add it to a new field
        dissolved_result['harvested_area'] = dissolved_result.geometry.area / 4046.86  # Square meters to acres conversion
        #changing the coordinate system to WGS84 for final mapping
        dissolved_result = dissolved_result.to_crs(epsg=4326)

        print(dissolved_result)


        # Save the GeoDataFrames to shapefiles
        dissolved_result.to_file(output_shapefile_path)

        #Converting the GeoDataframe to a Dataframe.
        df = dissolved_result.drop(columns='geometry')
        df.to_excel(output_excel_path,index=False)

#calling the function
crop_harvest_alert(crop_shapefile_path, raster_file_path, output_file_path, output_shapefile_path)