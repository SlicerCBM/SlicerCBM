import logging
import os

import vtk

import slicer
from slicer.i18n import tr as _
from slicer.i18n import translate
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin
from slicer.parameterNodeWrapper import (
    parameterNodeWrapper,
    WithinRange,
)

from slicer import (
    vtkMRMLMarkupsFiducialNode,
    vtkMRMLModelNode
)

import numpy as np


#
# FiducialsToSurface
#


class FiducialsToSurface(ScriptedLoadableModule):
    """Uses ScriptedLoadableModule base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        self.parent.title = _("Fiducials To Surface")  # TODO: make this more human readable by adding spaces
        # TODO: set categories (folders where the module shows up in the module selector)
        self.parent.categories = ["CBM.Surface Models"]
        self.parent.dependencies = []  # TODO: add here list of module names that this module requires
        self.parent.contributors = ["Saima Safdar (UWA), Benjamin Zwick (UWA)"]  # TODO: replace with "Firstname Lastname (Organization)"
        # TODO: update with short description of the module and a link to online module documentation
        # _() function marks text as translatable to other languages
        self.parent.helpText = _("""
This module creates a surface from a cloud of fiducial points using Delaunay triangulation.
""")
        # TODO: replace with organization, grant and thanks
        self.parent.acknowledgementText = _("""
""")

        # Additional initialization step after application startup is complete
        slicer.app.connect("startupCompleted()", registerSampleData)


#
# Register sample data sets in Sample Data module
#


def registerSampleData():
    """Add data sets to Sample Data module."""
    # It is always recommended to provide sample data for users to make it easy to try the module,
    # but if no sample data is available then this method (and associated startupCompeted signal connection) can be removed.

    import SampleData

    iconsPath = os.path.join(os.path.dirname(__file__), "Resources/Icons")

    # To ensure that the source code repository remains small (can be downloaded and installed quickly)
    # it is recommended to store data sets that are larger than a few MB in a Github release.


#
# FiducialsToSurfaceParameterNode
#


@parameterNodeWrapper
class FiducialsToSurfaceParameterNode:
    """
    The parameters needed by module.

    inputFiducial - The input fiducials.
    outputModel - The output model.
    enableScreenshots - If true, save screenshots.
    """

    inputFiducial: vtkMRMLMarkupsFiducialNode
    outputModel: vtkMRMLModelNode
    enableScreenshots: bool = False


#
# FiducialsToSurfaceWidget
#


class FiducialsToSurfaceWidget(ScriptedLoadableModuleWidget, VTKObservationMixin):
    """Uses ScriptedLoadableModuleWidget base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent=None) -> None:
        """Called when the user opens the module the first time and the widget is initialized."""
        ScriptedLoadableModuleWidget.__init__(self, parent)
        VTKObservationMixin.__init__(self)  # needed for parameter node observation
        self.logic = None
        self._parameterNode = None
        self._parameterNodeGuiTag = None

    def setup(self) -> None:
        """Called when the user opens the module the first time and the widget is initialized."""
        ScriptedLoadableModuleWidget.setup(self)

        # Load widget from .ui file (created by Qt Designer).
        # Additional widgets can be instantiated manually and added to self.layout.
        uiWidget = slicer.util.loadUI(self.resourcePath("UI/FiducialsToSurface.ui"))
        self.layout.addWidget(uiWidget)
        self.ui = slicer.util.childWidgetVariables(uiWidget)

        # Set scene in MRML widgets. Make sure that in Qt designer the top-level qMRMLWidget's
        # "mrmlSceneChanged(vtkMRMLScene*)" signal in is connected to each MRML widget's.
        # "setMRMLScene(vtkMRMLScene*)" slot.
        uiWidget.setMRMLScene(slicer.mrmlScene)

        # Create logic class. Logic implements all computations that should be possible to run
        # in batch mode, without a graphical user interface.
        self.logic = FiducialsToSurfaceLogic()

        # Connections

        # These connections ensure that we update parameter node when scene is closed
        self.addObserver(slicer.mrmlScene, slicer.mrmlScene.StartCloseEvent, self.onSceneStartClose)
        self.addObserver(slicer.mrmlScene, slicer.mrmlScene.EndCloseEvent, self.onSceneEndClose)

        # Buttons
        self.ui.applyButton.connect("clicked(bool)", self.onApplyButton)

        # Make sure parameter node is initialized (needed for module reload)
        self.initializeParameterNode()

    def cleanup(self) -> None:
        """Called when the application closes and the module widget is destroyed."""
        self.removeObservers()

    def enter(self) -> None:
        """Called each time the user opens this module."""
        # Make sure parameter node exists and observed
        self.initializeParameterNode()

    def exit(self) -> None:
        """Called each time the user opens a different module."""
        # Do not react to parameter node changes (GUI will be updated when the user enters into the module)
        if self._parameterNode:
            self._parameterNode.disconnectGui(self._parameterNodeGuiTag)
            self._parameterNodeGuiTag = None
            self.removeObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self._checkCanApply)

    def onSceneStartClose(self, caller, event) -> None:
        """Called just before the scene is closed."""
        # Parameter node will be reset, do not use it anymore
        self.setParameterNode(None)

    def onSceneEndClose(self, caller, event) -> None:
        """Called just after the scene is closed."""
        # If this module is shown while the scene is closed then recreate a new parameter node immediately
        if self.parent.isEntered:
            self.initializeParameterNode()

    def initializeParameterNode(self) -> None:
        """Ensure parameter node exists and observed."""
        # Parameter node stores all user choices in parameter values, node selections, etc.
        # so that when the scene is saved and reloaded, these settings are restored.

        self.setParameterNode(self.logic.getParameterNode())

        # Select default input nodes if nothing is selected yet to save a few clicks for the user
        if not self._parameterNode.inputFiducial:
            firstFiducialNode = slicer.mrmlScene.GetFirstNodeByClass("vtkMRMLScalarFiducialNode")
            if firstFiducialNode:
                self._parameterNode.inputFiducial = firstFiducialNode

    def setParameterNode(self, inputParameterNode: FiducialsToSurfaceParameterNode | None) -> None:
        """
        Set and observe parameter node.
        Observation is needed because when the parameter node is changed then the GUI must be updated immediately.
        """

        if self._parameterNode:
            self._parameterNode.disconnectGui(self._parameterNodeGuiTag)
            self.removeObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self._checkCanApply)
        self._parameterNode = inputParameterNode
        if self._parameterNode:
            # Note: in the .ui file, a Qt dynamic property called "SlicerParameterName" is set on each
            # ui element that needs connection.
            self._parameterNodeGuiTag = self._parameterNode.connectGui(self.ui)
            self.addObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self._checkCanApply)
            self._checkCanApply()

    def _checkCanApply(self, caller=None, event=None) -> None:
        if self._parameterNode and self._parameterNode.inputFiducial and self._parameterNode.outputModel:
            self.ui.applyButton.toolTip = _("Compute output Model")
            self.ui.applyButton.enabled = True
        else:
            self.ui.applyButton.toolTip = _("Select input Fiducial and output Model nodes")
            self.ui.applyButton.enabled = False

    def onApplyButton(self) -> None:
        """Run processing when user clicks "Apply" button."""
        with slicer.util.tryWithErrorDisplay(_("Failed to compute results."), waitCursor=True):
            # Compute output
            self.logic.process(
                self.ui.inputSelector.currentNode(),
                self.ui.outputSelector.currentNode(),
                self.ui.enableScreenshotsFlagCheckBox.checked)


#
# FiducialsToSurfaceLogic
#


class FiducialsToSurfaceLogic(ScriptedLoadableModuleLogic):
    """This class should implement all the actual
    computation done by your module.  The interface
    should be such that other python code can import
    this class and make use of the functionality without
    requiring an instance of the Widget.
    Uses ScriptedLoadableModuleLogic base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self) -> None:
        """Called when the logic class is instantiated. Can be used for initializing member variables."""
        ScriptedLoadableModuleLogic.__init__(self)

    def getParameterNode(self):
        return FiducialsToSurfaceParameterNode(super().getParameterNode())

    def process(self,
                inputFiducial: vtkMRMLMarkupsFiducialNode,
                outputModel: vtkMRMLModelNode,
                enableScreenshots: bool = False) -> None:
        """
        Run the processing algorithm.
        Can be used without GUI widget.
        """


        if not inputFiducial:
            raise ValueError("Input fiducials is invalid")
        if not outputModel:
            raise ValueError("Output model is invalid")

        try:
            import pyvista as pv
        except ModuleNotFoundError:
            if slicer.util.confirmOkCancelDisplay("This module requires 'pyvista' Python package. Click OK to install it now."):
                slicer.util.pip_install("pyvista")
                import pyvista as pv
            else:
                slicer.util.errorDisplay("This module requires 'pyvista' Python package but it was not installed.")
                return False

        import time

        startTime = time.time()
        logging.info("Processing started")

        markupsNode = slicer.util.getNode(inputFiducial.GetID())
        markupsIndex = 0
        n = markupsNode.GetNumberOfFiducials()
        modelNode = slicer.util.getNode(outputModel.GetID())

        ar = []
        print(n)
        for j in range(n):
            point_Ras = [0, 0, 0, 1]
            markupsNode.GetNthFiducialWorldCoordinates(markupsIndex, point_Ras)
            ar.append(point_Ras[0:3])
            markupsIndex = markupsIndex + 1

        ar2 = np.array(ar)
        print(ar2)
        print(ar2.shape)

        cloud = pv.PolyData(ar2)
        surf = cloud.delaunay_2d(alpha=0.0, offset=-5.0)
        newMesh1 = surf.compute_normals()
        cpos = newMesh1.plot()

        outputModel.SetAndObservePolyData(newMesh1)

        # Capture screenshot
        if enableScreenshots:
            self.takeScreenshot("FiducialsToSurfaceTest-Start", "MyScreenshot", -1)

        stopTime = time.time()
        logging.info(f"Processing completed in {stopTime-startTime:.2f} seconds")


#
# FiducialsToSurfaceTest
#


class FiducialsToSurfaceTest(ScriptedLoadableModuleTest):
    """
    This is the test case for your scripted module.
    Uses ScriptedLoadableModuleTest base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def setUp(self):
        """Do whatever is needed to reset the state - typically a scene clear will be enough."""
        slicer.mrmlScene.Clear()

    def runTest(self):
        """Run as few or as many tests as needed here."""
        self.setUp()
        self.test_FiducialsToSurface1()

    def test_FiducialsToSurface1(self):
        """Ideally you should have several levels of tests.  At the lowest level
        tests should exercise the functionality of the logic with different inputs
        (both valid and invalid).  At higher levels your tests should emulate the
        way the user would interact with your code and confirm that it still works
        the way you intended.
        One of the most important features of the tests is that it should alert other
        developers when their changes will have an impact on the behavior of your
        module.  For example, if a developer removes a feature that you depend on,
        your test should break so they know that the feature is needed.
        """

        self.delayDisplay("Starting the test")

        # Get/create input data

        # Test the module logic

        self.delayDisplay("Test passed")
