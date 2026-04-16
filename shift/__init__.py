def classFactory(iface):
    """Load the plugin class.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    from .main import ShiftPlugin

    return ShiftPlugin(iface)
