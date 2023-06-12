import logging
import os

import vtk

import slicer
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin


#
# CreateHeadTetrahedralGrid
#

class CreateHeadTetrahedralGrid(ScriptedLoadableModule):
    """Uses ScriptedLoadableModule base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        self.parent.title = "Create Head Tetrahedral Grid"
        self.parent.categories = ["CBM.Mesh/Grid"]
        self.parent.dependencies = []
        self.parent.contributors = ["Benjamin Zwick"]
        self.parent.helpText = """
Create brain volume and skull surface mesh from brain surface model, and save as a '.inp' mesh file.
See more information in <a href="https://slicercbm.org/en/latest/modules/mesh-grid/CreateHeadTetrahedralGrid.html">module documentation</a>.
"""
        self.parent.acknowledgementText = """
This file was originally developed by Benjamin Zwick.
"""

        # Additional initialization step after application startup is complete
        slicer.app.connect("startupCompleted()", registerSampleData)


#
# Register sample data sets in Sample Data module
#

def registerSampleData():
    """
    Add data sets to Sample Data module.
    """
    # It is always recommended to provide sample data for users to make it easy to try the module,
    # but if no sample data is available then this method (and associated startupCompeted signal connection) can be removed.

    import SampleData
    iconsPath = os.path.join(os.path.dirname(__file__), 'Resources/Icons')

    # To ensure that the source code repository remains small (can be downloaded and installed quickly)
    # it is recommended to store data sets that are larger than a few MB in a Github release.

    # TODO: Add sample data...


#
# CreateHeadTetrahedralGridWidget
#

class CreateHeadTetrahedralGridWidget(ScriptedLoadableModuleWidget, VTKObservationMixin):
    """Uses ScriptedLoadableModuleWidget base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent=None):
        """
        Called when the user opens the module the first time and the widget is initialized.
        """
        ScriptedLoadableModuleWidget.__init__(self, parent)
        VTKObservationMixin.__init__(self)  # needed for parameter node observation
        self.logic = None
        self._parameterNode = None
        self._updatingGUIFromParameterNode = False

    def setup(self):
        """
        Called when the user opens the module the first time and the widget is initialized.
        """
        ScriptedLoadableModuleWidget.setup(self)

        # Load widget from .ui file (created by Qt Designer).
        # Additional widgets can be instantiated manually and added to self.layout.
        uiWidget = slicer.util.loadUI(self.resourcePath('UI/CreateHeadTetrahedralGrid.ui'))
        self.layout.addWidget(uiWidget)
        self.ui = slicer.util.childWidgetVariables(uiWidget)

        # Set scene in MRML widgets. Make sure that in Qt designer the top-level qMRMLWidget's
        # "mrmlSceneChanged(vtkMRMLScene*)" signal in is connected to each MRML widget's.
        # "setMRMLScene(vtkMRMLScene*)" slot.
        uiWidget.setMRMLScene(slicer.mrmlScene)

        # Create logic class. Logic implements all computations that should be possible to run
        # in batch mode, without a graphical user interface.
        self.logic = CreateHeadTetrahedralGridLogic()

        # Connections

        # These connections ensure that we update parameter node when scene is closed
        self.addObserver(slicer.mrmlScene, slicer.mrmlScene.StartCloseEvent, self.onSceneStartClose)
        self.addObserver(slicer.mrmlScene, slicer.mrmlScene.EndCloseEvent, self.onSceneEndClose)

        # These connections ensure that whenever user changes some settings on the GUI, that is saved in the MRML scene
        # (in the selected parameter node).
        self.ui.inputSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
        self.ui.outputSelector.connect("currentPathChanged(QString)", self.updateParameterNodeFromGUI)

        # Buttons
        self.ui.applyButton.connect('clicked(bool)', self.onApplyButton)

        # Make sure parameter node is initialized (needed for module reload)
        self.initializeParameterNode()

    def cleanup(self):
        """
        Called when the application closes and the module widget is destroyed.
        """
        self.removeObservers()

    def enter(self):
        """
        Called each time the user opens this module.
        """
        # Make sure parameter node exists and observed
        self.initializeParameterNode()

    def exit(self):
        """
        Called each time the user opens a different module.
        """
        # Do not react to parameter node changes (GUI wlil be updated when the user enters into the module)
        self.removeObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)

    def onSceneStartClose(self, caller, event):
        """
        Called just before the scene is closed.
        """
        # Parameter node will be reset, do not use it anymore
        self.setParameterNode(None)

    def onSceneEndClose(self, caller, event):
        """
        Called just after the scene is closed.
        """
        # If this module is shown while the scene is closed then recreate a new parameter node immediately
        if self.parent.isEntered:
            self.initializeParameterNode()

    def initializeParameterNode(self):
        """
        Ensure parameter node exists and observed.
        """
        # Parameter node stores all user choices in parameter values, node selections, etc.
        # so that when the scene is saved and reloaded, these settings are restored.

        self.setParameterNode(self.logic.getParameterNode())

        # Select default input nodes if nothing is selected yet to save a few clicks for the user
        if not self._parameterNode.GetNodeReference("InputVolume"):
            firstVolumeNode = slicer.mrmlScene.GetFirstNodeByClass("vtkMRMLScalarVolumeNode")
            if firstVolumeNode:
                self._parameterNode.SetNodeReferenceID("InputVolume", firstVolumeNode.GetID())

    def setParameterNode(self, inputParameterNode):
        """
        Set and observe parameter node.
        Observation is needed because when the parameter node is changed then the GUI must be updated immediately.
        """

        if inputParameterNode:
            self.logic.setDefaultParameters(inputParameterNode)

        # Unobserve previously selected parameter node and add an observer to the newly selected.
        # Changes of parameter node are observed so that whenever parameters are changed by a script or any other module
        # those are reflected immediately in the GUI.
        if self._parameterNode is not None and self.hasObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode):
            self.removeObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)
        self._parameterNode = inputParameterNode
        if self._parameterNode is not None:
            self.addObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)

        # Initial GUI update
        self.updateGUIFromParameterNode()

    def updateGUIFromParameterNode(self, caller=None, event=None):
        """
        This method is called whenever parameter node is changed.
        The module GUI is updated to show the current state of the parameter node.
        """

        if self._parameterNode is None or self._updatingGUIFromParameterNode:
            return

        # Make sure GUI changes do not call updateParameterNodeFromGUI (it could cause infinite loop)
        self._updatingGUIFromParameterNode = True

        # Update node selectors and sliders
        self.ui.inputSelector.setCurrentNode(self._parameterNode.GetNodeReference("InputVolume"))
        self.ui.outputSelector.setCurrentPath(self._parameterNode.GetParameter("OutputVolume"))

        # Update buttons states and tooltips
        # FIXME: Why can't we set empty path here? Maybe this is the cause:
        # https://github.com/commontk/CTK/blob/2acba97da908cb94255b079a73fea28294637167/Libs/Widgets/ctkPathLineEdit.cpp#L678-L681
        # print(len(self._parameterNode.GetParameter("OutputVolume")))
        # FIXME: This below should be >0 not >1 (see comment above)
        if self._parameterNode.GetNodeReference("InputVolume") and len(self.ui.outputSelector.currentPath) > 1: # and self._parameterNode.GetNodeReference("OutputVolume"):
            self.ui.applyButton.toolTip = "Create grid."
            self.ui.applyButton.enabled = True
        else:
            self.ui.applyButton.toolTip = "Select input surface model and output grid file name."
            self.ui.applyButton.enabled = False

        # All the GUI updates are done
        self._updatingGUIFromParameterNode = False

    def updateParameterNodeFromGUI(self, caller=None, event=None):
        """
        This method is called when the user makes any change in the GUI.
        The changes are saved into the parameter node (so that they are restored when the scene is saved and loaded).
        """

        if self._parameterNode is None or self._updatingGUIFromParameterNode:
            return

        wasModified = self._parameterNode.StartModify()  # Modify all properties in a single batch

        self._parameterNode.SetNodeReferenceID("InputVolume", self.ui.inputSelector.currentNodeID)
        self._parameterNode.SetParameter("OutputVolume", self.ui.outputSelector.currentPath)

        self._parameterNode.EndModify(wasModified)

    def onApplyButton(self):
        """
        Run processing when user clicks "Apply" button.
        """
        with slicer.util.tryWithErrorDisplay("Failed to compute results.", waitCursor=True):

            # Compute output
            self.logic.process(self.ui.inputSelector.currentNode().GetStorageNode().GetFullNameFromFileName(),
                               self.ui.outputSelector.currentPath)


#
# CreateHeadTetrahedralGridLogic
#

class CreateHeadTetrahedralGridLogic(ScriptedLoadableModuleLogic):
    """This class should implement all the actual
    computation done by your module.  The interface
    should be such that other python code can import
    this class and make use of the functionality without
    requiring an instance of the Widget.
    Uses ScriptedLoadableModuleLogic base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self):
        """
        Called when the logic class is instantiated. Can be used for initializing member variables.
        """
        ScriptedLoadableModuleLogic.__init__(self)

    def setDefaultParameters(self, parameterNode):
        """
        Initialize parameter node with default settings.
        """
        pass

    def process(self, inputVolume, outputVolume):
        """
        Run the processing algorithm.
        Can be used without GUI widget.
        :param inputVolume: Brain surface
        :param outputModel:  Brain model
        """




        print(outputVolume)

        if not inputVolume or not outputVolume:
            raise ValueError("Input or output volume is invalid")

        import time
        startTime = time.time()
        logging.info('Processing started')

        import gmsh
        import numpy as np

        gmsh.initialize()

        gmsh.merge(inputVolume)

        gmsh.model.geo.addSurfaceLoop([1])
        gmsh.model.geo.addVolume([1])

        gmsh.model.geo.synchronize()

        gmsh.model.mesh.generate(3)

        nodes = gmsh.model.mesh.get_nodes()
        node_ids = nodes[0]
        coords = nodes[1].reshape((-1, 3))

        tri_elems = gmsh.model.mesh.get_elements_by_type(2)
        tet_elems = gmsh.model.mesh.get_elements_by_type(4)

        tri_ids = tri_elems[0]
        tet_ids = tet_elems[0] - len(tri_ids)
        tri_conn = tri_elems[1].reshape((-1,3))
        tet_conn = tet_elems[1].reshape((-1,4))

        contact_node_ids = np.unique(tri_elems[1])

        skull_node_ids = contact_node_ids + len(node_ids)
        skull_node_coords = coords[contact_node_ids - 1]
        skull_elem_ids = tri_ids + len(tet_ids)
        skull_conn = tri_conn + len(node_ids)

        # Reverse normals of skull surface
        skull_conn[:, [0, 1, 2]] = skull_conn[:, [0, 2, 1]]

        # Write tetrahedral brain mesh with skull surface in Abaqus .inp format
        with open(outputVolume, 'w') as f:
            # node ids and coordinates
            f.write("*NODE\n")
            # brain tet nodes
            for i, node_id in enumerate(node_ids):
                f.write(f"{node_id}, {coords[i,0]}, {coords[i,1]}, {coords[i,2]}\n")
            # skull tri nodes
            for i, node_id in enumerate(skull_node_ids):
                f.write(f"{node_id}, {skull_node_coords[i,0]}, {skull_node_coords[i,1]}, {skull_node_coords[i,2]}\n")

            # brain tetrahedral elements
            f.write("*ELEMENT, TYPE=C3D4, ELSET=brain\n")
            for i, elem_id in enumerate(tet_ids):
                f.write(f"{elem_id}, {tet_conn[i,0]}, {tet_conn[i,1]}, {tet_conn[i,2]}, {tet_conn[i,3]}\n")

            # skull triangle elements
            f.write("*ELEMENT, TYPE=S3, ELSET=skull\n")
            for i, elem_id in enumerate(skull_elem_ids):
                f.write(f"{elem_id}, {skull_conn[i,0]}, {skull_conn[i,1]}, {skull_conn[i,2]}\n")

            # brain surface nodes (in contact with skull)
            f.write("*NSET, NSET=contact\n")
            for i, node_id in enumerate(contact_node_ids):
                f.write(str(node_id))
                f.write(",")
                if (i+1) % 8 == 0:
                    f.write("\n")
                else:
                    f.write(" ")

        gmsh.finalize()

        stopTime = time.time()
        logging.info(f'Processing completed in {stopTime-startTime:.2f} seconds')


#
# CreateHeadTetrahedralGridTest
#

class CreateHeadTetrahedralGridTest(ScriptedLoadableModuleTest):
    """
    This is the test case for your scripted module.
    Uses ScriptedLoadableModuleTest base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def setUp(self):
        """ Do whatever is needed to reset the state - typically a scene clear will be enough.
        """
        slicer.mrmlScene.Clear()

    def runTest(self):
        """Run as few or as many tests as needed here.
        """
        self.setUp()
        self.test_CreateHeadTetrahedralGrid1()

    def test_CreateHeadTetrahedralGrid1(self):
        """ Ideally you should have several levels of tests.  At the lowest level
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

        import SampleData
        registerSampleData()
        inputVolume = SampleData.downloadSample('CreateHeadTetrahedralGrid1')
        self.delayDisplay('Loaded test data set')

        inputScalarRange = inputVolume.GetImageData().GetScalarRange()
        self.assertEqual(inputScalarRange[0], 0)
        self.assertEqual(inputScalarRange[1], 695)

        outputVolume = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLScalarVolumeNode")

        # Test the module logic

        logic = CreateHeadTetrahedralGridLogic()

        # TODO: Write tests...

        self.delayDisplay('Test passed')
