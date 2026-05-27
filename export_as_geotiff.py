from osgeo import gdal,osr
import numpy as np

def export_geotiff(topo,filename,xmin,xmax,ymin,ymax):
    proj = osr.SpatialReference()
    proj.ImportFromEPSG(32615)

    datout = np.squeeze(topo)

    datout[np.isnan(datout)] = -9999
    driver = gdal.GetDriverByName('GTiff')
    cols,rows = np.shape(datout)
    
    output_filename = filename[0:-4]+'.tif'
    ds = driver.Create(output_filename, rows, cols, 1, gdal.GDT_Float32, [ 'COMPRESS=LZW' ] )
    if proj is not None:
        ds.SetProjection(proj.ExportToWkt())

    xres = (xmax - xmin) / float(rows)
    yres = (ymax - ymin) / float(cols)

    geotransform = (xmin, xres, 0, ymax, 0, -yres)

    ds.SetGeoTransform(geotransform)
    ss_band = ds.GetRasterBand(1)
    ss_band.WriteArray(datout)
    ss_band.SetNoDataValue(-9999)
    ss_band.FlushCache()
    ss_band.ComputeStatistics(False)
    ss_band.SetUnitType('mm')