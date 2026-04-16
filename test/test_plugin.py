

from qgis import processing
from qgis.core import QgsRasterLayer

def test_plugin(qgis_processing,qgis_iface):
    import shift

    x_min = 776302
    y_min=214895
    x_max=831861
    y_max= 254345

    x_shift=50000
    y_shift=-10000

    plugin = shift.classFactory(qgis_iface)

    plugin.initGui()

    create_outputs = processing.run("native:createrandomnormalrasterlayer", {'EXTENT':f'{x_min},{x_max},{y_min},{y_max} [EPSG:27562]','TARGET_CRS':'EPSG:27562','PIXEL_SIZE':1000,'OUTPUT_TYPE':0,'MEAN':0,'STDDEV':1,'CREATION_OPTIONS':None,'OUTPUT':'TEMPORARY_OUTPUT'})

    initial_raster=create_outputs['OUTPUT']

    shift_outputs = processing.run("shift:shift", {'INPUT':initial_raster,'X_SHIFT':x_shift,'Y_SHIFT':y_shift,'OUTPUT':'TEMPORARY_OUTPUT'})

    out_layer = QgsRasterLayer(shift_outputs['OUTPUT'])

    assert out_layer.extent().xMinimum() == x_min + x_shift
    assert out_layer.extent().xMaximum() == x_max + x_shift
    assert out_layer.extent().yMinimum() == y_min + y_shift
    assert out_layer.extent().yMaximum() == y_max +y_shift

    plugin.unload()
