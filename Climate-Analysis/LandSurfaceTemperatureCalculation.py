
import rasterio
import numpy as np

path = 'D:/fatima group/LandSat'
#Openning Raster Bands
band4=rasterio.open(path+'/LC09_L2SP_150039_20230310_20230312_02_T1_SR_B4.TIF')
band5=rasterio.open(path+'/LC09_L2SP_150039_20230310_20230312_02_T1_SR_B5.TIF')
band10=rasterio.open(path+'/LC09_L2SP_150039_20230310_20230312_02_T1_ST_B10.TIF')

#Reading raster bands as float
red=band4.read(1).astype('float64')
nir=band5.read(1).astype('float64')
tir1=band10.read(1).astype('float64')

# Suppress/hide the warning
np.seterr(invalid='ignore')
#ndvi calculation
ndvi=np.where(
    (nir+red)==0.,
    0,
    (nir-red)/(nir+red)
)

image=rasterio.open(path+'/ndvi.tiff','w',driver='Gtiff',
                    width=band5.width,
                    height=band5.height,
                   count=1,
                   crs=band5.crs,
                   transform=band5.transform,
                   dtype='float64')
image.write(ndvi,1)
image.close()

a=np.max(ndvi)
b=np.min(ndvi)

TOA_10=0.0003342*tir1+0.1
BT1=(1321.08/(np.log((774.89/(TOA_10+1)))))
pv=(((ndvi-b)/(a-b))**2)
e=0.004*pv+0.986
LST=((BT1 / (1 + (0.00115 * BT1 / 1.4388) *  np.log(e))))-273

image=rasterio.open(path+'/LST.tiff','w',driver='Gtiff',
                    width=band5.width,
                    height=band5.height,
                   count=1,
                   crs=band5.crs,
                   transform=band5.transform,
                   dtype='float64')
image.write(LST,1)
image.close()

print('code is executed')