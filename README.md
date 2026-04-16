# Shift Raster Layer QGIS Plugin

A processing algorithm for QGIS for moving a raster layer. 

Once installed you will find the tool in the processing toolbox.

The x and y values will be in the same units as the coordinate refence system of the layer. (i.e. if the layer is in a metre-based CRS, x and y will move will be in metres; if in degrees it will be in degrees)

Compatible with batch processing if you want to move lots of rasters at the same time.

Works on all rasters that open with gdal (that's most rasters in qgis, but not web maps for example)