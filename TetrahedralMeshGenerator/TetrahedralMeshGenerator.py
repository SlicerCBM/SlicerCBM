import os
import unittest
import logging
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin
#
# TetrahedralMeshGenerator
#

class TetrahedralMeshGenerator(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "Tetrahedral Mesh Generator"
    self.parent.categories = ["CBM.Mesh/Grid"]
    self.parent.dependencies = []  # TODO: add here list of module names that this module requires
    self.parent.contributors = ["Saima Safdar, Benjamin Zwick, Yue Yu"]
    self.parent.helpText = """
An extension to create tetrahedral meshes (2D, 3D) from surface models
"""
    self.parent.helpText += self.getDefaultModuleDocumentationLink()  # TODO: verify that the default URL is correct or change it to the actual documentation
    self.parent.acknowledgementText = """
"""  # TODO: replace with organization, grant and thanks.

#
# TetrahedralMeshGeneratorWidget
#

class TetrahedralMeshGeneratorWidget(ScriptedLoadableModuleWidget, VTKObservationMixin):
  """Uses ScriptedLoadableModuleWidget base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent=None):
    ScriptedLoadableModuleWidget.__init__(self, parent)
    VTKObservationMixin.__init__(self)  # needed for parameter node observation
    self.logic = None
    self._parameterNode = None

  def setup(self):
    """
    Called when the user opens the module the first time and the widget is initialized.
    """
    ScriptedLoadableModuleWidget.setup(self)

    # Load widget from .ui file (created by Qt Designer)
    uiWidget = slicer.util.loadUI(self.resourcePath('UI/TetrahedralMeshGenerator.ui'))
    self.layout.addWidget(uiWidget)
    self.ui = slicer.util.childWidgetVariables(uiWidget)

    # Set scene in MRML widgets. Make sure that in Qt designer
    # "mrmlSceneChanged(vtkMRMLScene*)" signal in is connected to each MRML widget's.
    # "setMRMLScene(vtkMRMLScene*)" slot.
    uiWidget.setMRMLScene(slicer.mrmlScene)

    # Create a new parameterNode (it stores user's node and parameter values choices in the scene)
    self.logic = TetrahedralMeshGeneratorLogic()
    self.ui.parameterNodeSelector.addAttribute("vtkMRMLScriptedModuleNode", "ModuleName", self.moduleName)
    self.setParameterNode(self.logic.getParameterNode())

    # Connections
    self.ui.parameterNodeSelector.connect('currentNodeChanged(vtkMRMLNode*)', self.setParameterNode)


    self.ui.outputSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)


    self.ui.applyButton.connect('clicked(bool)', self.onApplyButton)

    # Initial GUI update
    self.updateGUIFromParameterNode()

  def cleanup(self):
    """
    Called when the application closes and the module widget is destroyed.
    """
    self.removeObservers()

  def setParameterNode(self, inputParameterNode):
    """
    Adds observers to the selected parameter node. Observation is needed because when the
    parameter node is changed then the GUI must be updated immediately.
    """

    if inputParameterNode:
      self.logic.setDefaultParameters(inputParameterNode)
    wasBlocked = self.ui.parameterNodeSelector.blockSignals(True)
    self.ui.parameterNodeSelector.setCurrentNode(inputParameterNode)
    self.ui.parameterNodeSelector.blockSignals(wasBlocked)
    if inputParameterNode == self._parameterNode:
      return
    if self._parameterNode is not None:
      self.removeObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)
    if inputParameterNode is not None:
      self.addObserver(inputParameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)
    self._parameterNode = inputParameterNode
    self.updateGUIFromParameterNode()

  def updateGUIFromParameterNode(self, caller=None, event=None):
    """
    This method is called whenever parameter node is changed.
    The module GUI is updated to show the current state of the parameter node.
    """

    # Disable all sections if no parameter node is selected
    self.ui.basicCollapsibleButton.enabled = self._parameterNode is not None

    if self._parameterNode is None:
      return

    # Update each widget from parameter node


    wasBlocked = self.ui.outputSelector.blockSignals(True)
    self.ui.outputSelector.setCurrentNode(self._parameterNode.GetNodeReference("OutputVolume"))
    self.ui.outputSelector.blockSignals(wasBlocked)


    # Update buttons states and tooltips
    if self._parameterNode.GetNodeReference("OutputVolume"):
      self.ui.applyButton.toolTip = "Compute output volume"
      self.ui.applyButton.enabled = True
    else:
      self.ui.applyButton.toolTip = "Select input and output volume nodes"
      self.ui.applyButton.enabled = False

  def updateParameterNodeFromGUI(self, caller=None, event=None):
    """
    This method is called when the user makes changes in the GUI.
    The changes are saved into the parameter node (so that they are preserved when the scene is saved and loaded).
    """

    if self._parameterNode is None:
      return


    self._parameterNode.SetNodeReferenceID("OutputVolume", self.ui.outputSelector.currentNodeID)


  def onApplyButton(self):
    """
    Run processing when user clicks "Apply" button.

    """
    try:
        import gmsh
        import meshio
    except:
        slicer.util.pip_install("gmsh")
        slicer.util.pip_install("meshio")
        import gmsh
        import meshio

    try:
      self.logic.run(self.ui.inputFile.currentPath, self.ui.outputSelector.currentNode(),self.ui.outputFile.currentPath, self.ui.meshType.value)
    except Exception as e:
      slicer.util.errorDisplay("Failed to compute results: "+str(e))
      import traceback
      traceback.print_exc()


#
# TetrahedralMeshGeneratorLogic
#

class TetrahedralMeshGeneratorLogic(ScriptedLoadableModuleLogic):
  """This class should implement all the actual
  computation done by your module.  The interface
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget.
  Uses ScriptedLoadableModuleLogic base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setDefaultParameters(self, parameterNode):
    if not parameterNode.GetParameter("Threshold"):
      parameterNode.SetParameter("Threshold", "50.0")
    if not parameterNode.GetParameter("Invert"):
      parameterNode.SetParameter("Invert", "false")

  def run(self, inputFile, outputModel, outputModelFile, meshType):
    """
    Run the processing algorithm.
    Can be used without GUI widget.
    """

    if not inputFile or not outputModel:
      raise ValueError("Input File or output Model is invalid")

    import gmsh
    import math
    import time

    logging.info('Processing started')
    start_time = time.time()
    #temporary path for mid files to be saved
    dir_path = os.path.dirname(os.path.realpath(__file__))
    # Compute the thresholded output volume using the Threshold Scalar Volume CLI module
    gmsh.initialize()
    #gmsh.option.setNumber("General.Terminal", 1)
    #gmsh.option.setNumber("Mesh.Algorithm", 8);
    #gmsh.option.setNumber("Mesh.CharacteristicLengthMin", 2);
    #gmsh.option.setNumber("Mesh.CharacteristicLengthMax", 2);
    #gmsh.option.setNumber("Mesh.Optimize",1)
    #gmsh.option.setNumber("Mesh.QualityType",2);
    #gmsh.option.setNumber("Mesh.CharacteristicLengthFactor",3)#

    # Let's merge an STL mesh that we would like to remesh (from the parent
    # directory):
    #path = '/home/yue/git/automation/step/1_1_Mesh_creation/STL'
    #dirname = os.path.dirname(path)
    #gmsh.merge(os.path.join(dirname, 'brain.stl'))
    gmsh.merge(inputFile)
    # We first classify ("color") the surfaces by splitting the original surface
    # along sharp geometrical features. This will create new discrete surfaces,
    # curves and points.
    # Angle between two triangles above which an edge is considered as sharp:
    angle = 40

    # For complex geometries, patches can be too complex, too elongated or too large
    # to be parametrized; setting the following option will force the creation of
    # patches that are amenable to reparametrization:
    forceParametrizablePatches = True

    # For open surfaces include the boundary edges in the classification process:
    includeBoundary = False

    # Force curves to be split on given angle:
    curveAngle = 120

    gmsh.model.mesh.classifySurfaces(angle * math.pi / 180., includeBoundary,forceParametrizablePatches, curveAngle * math.pi / 180.)

    gmsh.model.mesh.createGeometry()


    n = gmsh.model.getDimension()
    s = gmsh.model.getEntities(n)
    l = gmsh.model.geo.addSurfaceLoop([s[i][1] for i in range(len(s))])
    gmsh.model.geo.addVolume([l])
    #print("Volume added")
    gmsh.model.geo.synchronize()


    # We specify element sizes imposed by a size field, just because we can :-)
    funny = False
    f = gmsh.model.mesh.field.add("MathEval")
    if funny:
        gmsh.model.mesh.field.setString(f, "F", "2*Sin((x+y)/5) + 3")
    else:
        gmsh.model.mesh.field.setString(f, "F", "4")
    gmsh.model.mesh.field.setAsBackgroundMesh(f)




    gmsh.model.mesh.generate(meshType)
    gmsh.write(dir_path+"/brainmask_auto.msh")

    print(meshType)
    #gmsh.model.mesh.generate(2)
    gmsh.finalize()
    #select the type of cells to be extracted and writitg into inp file based on the mesh type 2 triangels and 3 for tetras
    if meshType==2:
        cellType = "triangle"
    else:
        cellType = "tetra"

    #convert .msh to .vtk and load it in  slicer
    mesh = meshio.read(dir_path+"/brainmask_auto.msh")
    nodes = mesh.points
    cells = mesh.cells_dict[cellType]
    meshio.write_points_cells(dir_path+"/vMesh.vtk", nodes,[(cellType, cells)])

    outputModel = slicer.util.loadModel(dir_path+"/vMesh.vtk")

    n = slicer.util.getNode(outputModel.GetID())
    nn = n.GetModelDisplayNode()
    nn.EdgeVisibilityOn()

    #msh=meshio.read("./MSH/brainmask_auto.msh")
    #nodes=msh.points
    #tetras=msh.cells_dict["tetra"]
    #meshio.write_points_cells("brainmask_auto.vtk",nodes,[("tetra",tetras)])

    mesh = meshio.read(dir_path+"/vMesh.vtk")
    meshio.write(outputModelFile,mesh)

    print("----%s seconds ----"%(time.time()-start_time))
    logging.info('Processing completed')

#
# TetrahedralMeshGeneratorTest
#

class TetrahedralMeshGeneratorTest(ScriptedLoadableModuleTest):
  """
  This is the test case for your scripted module.
  Uses ScriptedLoadableModuleTest base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setUp(self):
    """ Do whatever is needed to reset the state - typically a scene clear will be enough.
    """
    slicer.mrmlScene.Clear(0)

  def runTest(self):
    """Run as few or as many tests as needed here.
    """
    self.setUp()
    self.test_TetrahedralMeshGenerator1()

  def test_TetrahedralMeshGenerator1(self):
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
    inputVolume = SampleData.downloadFromURL(
      nodeNames='MRHead',
      fileNames='MR-Head.nrrd',
      uris='https://github.com/Slicer/SlicerTestingData/releases/download/MD5/39b01631b7b38232a220007230624c8e',
      checksums='MD5:39b01631b7b38232a220007230624c8e')[0]
    self.delayDisplay('Finished with download and loading')

    inputScalarRange = inputVolume.GetImageData().GetScalarRange()
    self.assertEqual(inputScalarRange[0], 0)
    self.assertEqual(inputScalarRange[1], 279)

    outputVolume = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLScalarVolumeNode")
    threshold = 50

    # Test the module logic

    logic = TetrahedralMeshGeneratorLogic()

    # Test algorithm with non-inverted threshold
    logic.run(inputVolume, outputVolume, threshold, False)
    outputScalarRange = outputVolume.GetImageData().GetScalarRange()
    self.assertEqual(outputScalarRange[0], inputScalarRange[0])
    self.assertEqual(outputScalarRange[1], threshold)

    # Test algorithm with inverted threshold
    logic.run(inputVolume, outputVolume, threshold, True)
    outputScalarRange = outputVolume.GetImageData().GetScalarRange()
    self.assertEqual(outputScalarRange[0], inputScalarRange[0])
    self.assertEqual(outputScalarRange[1], inputScalarRange[1])

    self.delayDisplay('Test passed')
