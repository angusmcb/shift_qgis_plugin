from qgis.core import (
    QgsProcessingProvider,
    QgsApplication,
    QgsProcessingParameterRasterLayer,
    QgsProcessingParameterNumber,
    QgsProcessingAlgorithm,
    QgsProcessingContext,
    QgsProcessingFeedback,
    QgsProcessingParameterRasterDestination,
)

from typing import Any


class ShiftPlugin:
    def __init__(self, iface) -> None:
        pass

    def initGui(self) -> None:  # noqa N802
        self.initProcessing()

    def initProcessing(self) -> None:  # noqa: N802
        """Initialize the processing provider."""

        self.provider = ShiftProvider()
        QgsApplication.processingRegistry().addProvider(self.provider)

    def unload(self):
        QgsApplication.processingRegistry().removeProvider(self.provider)


class ShiftProvider(QgsProcessingProvider):
    """Processing provider class."""

    def loadAlgorithms(self):
        """Loads all algorithms belonging to this provider."""
        self.addAlgorithm(ShiftAlgorithm())

    def id(self) -> str:
        return "shift"

    def name(self) -> str:
        return "Shift"


class ShiftAlgorithm(QgsProcessingAlgorithm):
    INPUT = "INPUT"
    X_SHIFT = "X_SHIFT"
    Y_SHIFT = "Y_SHIFT"
    OUTPUT = "OUTPUT"

    def createInstance(self):  # noqa N802
        return ShiftAlgorithm()

    def name(self):
        return "shift"

    def displayName(self):
        return "Shift"

    def initAlgorithm(self, config=None):  # noqa N802
        self.addParameter(QgsProcessingParameterRasterLayer(self.INPUT, "Input Raster"))
        self.addParameter(
            QgsProcessingParameterNumber(self.X_SHIFT, "Shift X Coordinates by")
        )
        self.addParameter(
            QgsProcessingParameterNumber(self.Y_SHIFT, "Shift Y Coordinates byt")
        )
        self.addParameter(
            QgsProcessingParameterRasterDestination(self.OUTPUT, "Output Raster")
        )

    def processAlgorithm(  # noqa N802
        self,
        parameters: dict[str, Any],
        context: QgsProcessingContext,
        feedback: QgsProcessingFeedback | None,
    ) -> dict:
        x_shift = self.parameterAsDouble(parameters, self.X_SHIFT, context)
        y_shift = self.parameterAsDouble(parameters, self.Y_SHIFT, context)

        source_layer = self.parameterAsRasterLayer(parameters, self.INPUT, context)

        source_path = source_layer.source()

        from osgeo import gdal

        with gdal.Open(source_path) as input_raster:
            extent = input_raster.GetExtent()

        destination_path = self.parameterAsOutputLayer(parameters, self.OUTPUT, context)

        # assigned output bounds: [ulx, uly, lrx, lry]
        gdal.Translate(
            destination_path,
            source,
            outputBounds=[
                extent[0] + x_shift,
                extent[3] + y_shift,
                extent[1] + x_shift,
                extent[2] + y_shift,
            ],
        )

        return {self.OUTPUT: destination_path}
