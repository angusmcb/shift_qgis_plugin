from pathlib import Path
from typing import Any, Optional

from qgis.core import (
    QgsApplication,
    QgsProcessingAlgorithm,
    QgsProcessingContext,
    QgsProcessingFeedback,
    QgsProcessingParameterNumber,
    QgsProcessingParameterRasterDestination,
    QgsProcessingParameterRasterLayer,
    QgsProcessingProvider,
)
from qgis.processing import execAlgorithmDialog
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction

ICON = QIcon(str(Path(__file__).parent / "shift_logo.svg"))


class ShiftPlugin:
    def __init__(self, iface) -> None:
        self.iface = iface
        self.provider: Optional["ShiftProvider"] = None
        self.action = None

    def initGui(self) -> None:  # noqa N802
        self.initProcessing()
        self.initRasterMenuAction()

    def initProcessing(self) -> None:  # noqa: N802
        self.provider = ShiftProvider()
        QgsApplication.processingRegistry().addProvider(self.provider)

    def initRasterMenuAction(self) -> None:  # noqa: N802
        action = QAction(ICON, "Shift raster...", self.iface.mainWindow())
        action.triggered.connect(self.openAlgorithmDialog)
        self.action = action

        self.iface.rasterMenu().addAction(action)

    def openAlgorithmDialog(self) -> None:  # noqa: N802

        execAlgorithmDialog(ShiftAlgorithm(), {})

    def unload(self):
        if self.action is not None:
            self.iface.rasterMenu().removeAction(self.action)
            self.action = None

        if self.provider is not None:
            QgsApplication.processingRegistry().removeProvider(self.provider)
            self.provider = None


class ShiftProvider(QgsProcessingProvider):
    def loadAlgorithms(self):
        self.addAlgorithm(ShiftAlgorithm())

    def id(self) -> str:
        return "shift"

    def name(self) -> str:
        return "Shift Raster"

    def icon(self) -> QIcon:
        return ICON


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
        return "Shift Raster"

    def icon(self):
        return ICON

    def shortHelpString(self):
        return """
            Shifts the coordinates of a raster by a specified amount in the X and Y directions.     
            
            The x and y values will be in the same units as the coordinate refence system of the layer. (i.e. if the layer is in a metre-based CRS, x and y will move will be in metres; if in degrees it will be in degrees)

            Compatible with batch processing if you want to move lots of rasters at the same time.

            Works on all rasters that open with gdal (that's most rasters in qgis, but not web maps for example)
            """

    def initAlgorithm(self, config=None):  # noqa N802
        self.addParameter(QgsProcessingParameterRasterLayer(self.INPUT, "Input Raster"))
        self.addParameter(
            QgsProcessingParameterNumber(self.X_SHIFT, "Shift X Coordinates by")
        )
        self.addParameter(
            QgsProcessingParameterNumber(self.Y_SHIFT, "Shift Y Coordinates by")
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
            source_path,
            outputBounds=[
                extent[0] + x_shift,
                extent[3] + y_shift,
                extent[1] + x_shift,
                extent[2] + y_shift,
            ],
        )

        return {self.OUTPUT: destination_path}
