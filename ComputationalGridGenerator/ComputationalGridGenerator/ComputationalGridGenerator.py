import os
import unittest
import logging
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin
#
# ComputationalGridGenerator
#

class ComputationalGridGenerator(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "ComputationalGridGenerator"  # TODO: make this more human readable by adding spaces
    self.parent.categories = ["Examples"]  # TODO: set categories (folders where the module shows up in the module selector)
    self.parent.dependencies = []  # TODO: add here list of module names that this module requires
    self.parent.contributors = ["Saima Safdar"]  # TODO: replace with "Firstname Lastname (Organization)"
    # TODO: update with short description of the module and a link to online module documentation
    self.parent.helpText = """
This is an example of scripted loadable module bundled in an extension.
See more information in <a href="https://github.com/organization/projectname#ComputationalGridGenerator">module documentation</a>.
"""
    # TODO: replace with organization, grant and thanks
    self.parent.acknowledgementText = """
This file was originally developed by Jean-Christophe Fillion-Robin, Kitware Inc., Andras Lasso, PerkLab,
and Steve Pieper, Isomics, Inc. and was partially funded by NIH grant 3P41RR013218-12S1.
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

  # ComputationalGridGenerator1
  SampleData.SampleDataLogic.registerCustomSampleDataSource(
    # Category and sample name displayed in Sample Data module
    category='ComputationalGridGenerator',
    sampleName='ComputationalGridGenerator1',
    # Thumbnail should have size of approximately 260x280 pixels and stored in Resources/Icons folder.
    # It can be created by Screen Capture module, "Capture all views" option enabled, "Number of images" set to "Single".
    thumbnailFileName=os.path.join(iconsPath, 'ComputationalGridGenerator1.png'),
    # Download URL and target file name
    uris="https://github.com/Slicer/SlicerTestingData/releases/download/SHA256/998cb522173839c78657f4bc0ea907cea09fd04e44601f17c82ea27927937b95",
    fileNames='ComputationalGridGenerator1.nrrd',
    # Checksum to ensure file integrity. Can be computed by this command:
    #  import hashlib; print(hashlib.sha256(open(filename, "rb").read()).hexdigest())
    checksums = 'SHA256:998cb522173839c78657f4bc0ea907cea09fd04e44601f17c82ea27927937b95',
    # This node name will be used when the data set is loaded
    nodeNames='ComputationalGridGenerator1'
  )

  # ComputationalGridGenerator2
  SampleData.SampleDataLogic.registerCustomSampleDataSource(
    # Category and sample name displayed in Sample Data module
    category='ComputationalGridGenerator',
    sampleName='ComputationalGridGenerator2',
    thumbnailFileName=os.path.join(iconsPath, 'ComputationalGridGenerator2.png'),
    # Download URL and target file name
    uris="https://github.com/Slicer/SlicerTestingData/releases/download/SHA256/1a64f3f422eb3d1c9b093d1a18da354b13bcf307907c66317e2463ee530b7a97",
    fileNames='ComputationalGridGenerator2.nrrd',
    checksums = 'SHA256:1a64f3f422eb3d1c9b093d1a18da354b13bcf307907c66317e2463ee530b7a97',
    # This node name will be used when the data set is loaded
    nodeNames='ComputationalGridGenerator2'
  )

#
# ComputationalGridGeneratorWidget
#

class ComputationalGridGeneratorWidget(ScriptedLoadableModuleWidget, VTKObservationMixin):
  """Uses ScriptedLoadableModuleWidget base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
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
    uiWidget = slicer.util.loadUI(self.resourcePath('UI/ComputationalGridGenerator.ui'))
    self.layout.addWidget(uiWidget)
    self.ui = slicer.util.childWidgetVariables(uiWidget)

    # Set scene in MRML widgets. Make sure that in Qt designer the top-level qMRMLWidget's
    # "mrmlSceneChanged(vtkMRMLScene*)" signal in is connected to each MRML widget's.
    # "setMRMLScene(vtkMRMLScene*)" slot.
    uiWidget.setMRMLScene(slicer.mrmlScene)

    # Create logic class. Logic implements all computations that should be possible to run
    # in batch mode, without a graphical user interface.
    self.logic = ComputationalGridGeneratorLogic()

    # Connections

    # These connections ensure that we update parameter node when scene is closed
    self.addObserver(slicer.mrmlScene, slicer.mrmlScene.StartCloseEvent, self.onSceneStartClose)
    self.addObserver(slicer.mrmlScene, slicer.mrmlScene.EndCloseEvent, self.onSceneEndClose)

    # These connections ensure that whenever user changes some settings on the GUI, that is saved in the MRML scene
    # (in the selected parameter node).
    self.ui.inputSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
    #self.ui.outputSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
    #self.ui.imageThresholdSliderWidget.connect("valueChanged(double)", self.updateParameterNodeFromGUI)
    self.ui.invertOutputCheckBox.connect("toggled(bool)", self.updateParameterNodeFromGUI)
    #self.ui.invertedOutputSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)

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
    if self._parameterNode is not None:
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
    #self.ui.outputSelector.setCurrentNode(self._parameterNode.GetNodeReference("OutputVolume"))
    #self.ui.invertedOutputSelector.setCurrentNode(self._parameterNode.GetNodeReference("OutputVolumeInverse"))
    #self.ui.imageThresholdSliderWidget.value = float(self._parameterNode.GetParameter("Threshold"))
    self.ui.invertOutputCheckBox.checked = (self._parameterNode.GetParameter("Invert") == "true")

    # Update buttons states and tooltips
    if self._parameterNode.GetNodeReference("InputVolume"):
      self.ui.applyButton.toolTip = "Compute output volume"
      self.ui.applyButton.enabled = True
    else:
      self.ui.applyButton.toolTip = "Select input and output volume nodes"
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
    #self._parameterNode.SetNodeReferenceID("OutputVolume", self.ui.outputSelector.currentNodeID)
    #self._parameterNode.SetParameter("Threshold", str(self.ui.imageThresholdSliderWidget.value))
    #self._parameterNode.SetParameter("Invert", "true" if self.ui.invertOutputCheckBox.checked else "false")
    #self._parameterNode.SetNodeReferenceID("OutputVolumeInverse", self.ui.invertedOutputSelector.currentNodeID)

    self._parameterNode.EndModify(wasModified)

  def onApplyButton(self):
    """
    Run processing when user clicks "Apply" button.
    """
    try:
        import gmsh
        import meshio
        import pyacvd
        import pyvista as pv
    except ModuleNotFoundError as e:
        if slicer.util.confirmOkCancelDisplay("This module requires gmsh, meshio, pyacvd and pyvista Python packages. Click OK to install (it may take several minutes)."):
            slicer.util.pip_install("gmsh")
            slicer.util.pip_install("meshio")
            slicer.util.pip_install("pyacvd")
            slicer.util.pip_install("pyvista")


      # Compute output
    try:
          self.logic.process(self.ui.inputSelector.currentNode(), self.ui.fold_save.currentPath)#self.ui.invertOutputCheckBox.checked)
    except Exception as e:
          slicer.util.errorDisplay("Failed to compute results: "+str(e))
          import traceback
          traceback.print_exc()
      # Compute inverted output (if needed)
      #if self.ui.invertedOutputSelector.currentNode():
        # If additional output volume is selected then result with inverted threshold is written there
       # self.logic.process(self.ui.inputSelector.currentNode(), self.ui.fold_save.currentPath,
        #  not self.ui.invertOutputCheckBox.checked, showResult=False)




#
# ComputationalGridGeneratorLogic
#

class ComputationalGridGeneratorLogic(ScriptedLoadableModuleLogic):
  """This class should implement all the actual
  computation done by your module.  The interface
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget.
  Uses ScriptedLoadableModuleLogic base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
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
    if not parameterNode.GetParameter("Threshold"):
      parameterNode.SetParameter("Threshold", "100.0")
    if not parameterNode.GetParameter("Invert"):
      parameterNode.SetParameter("Invert", "false")

  def process(self, inputVolume, fold_path,  showResult=True):
    """
    Run the processing algorithm.
    Can be used without GUI widget.
    :param inputVolume: volume to be thresholded
    :param outputVolume: thresholding result
    :param imageThreshold: values above/below this threshold will be set to 0
    :param invert: if True then values above the threshold will be set to 0, otherwise values below are set to 0
    :param showResult: show output volume in slice viewers
    """

    if not inputVolume:
      raise ValueError("Input is invalid")

    import time
    startTime = time.time()
    logging.info('Processing started')

    # Compute the thresholded output volume using the "Threshold Scalar Volume" CLI module
    """cliParams = {
      'InputVolume': inputVolume.GetID(),
      'OutputVolume': outputVolume.GetID(),
      'ThresholdValue' : imageThreshold,
      'ThresholdType' : 'Above' if invert else 'Below'
      }
    cliNode = slicer.cli.run(slicer.modules.thresholdscalarvolume, None, cliParams, wait_for_completion=True, update_display=showResult)
    # We don't need the CLI module node anymore, remove it to not clutter the scene with it
    slicer.mrmlScene.RemoveNode(cliNode)"""


    #thresholding auto OSTU
    # Create segmentation
    segmentationNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSegmentationNode")
    segmentationNode.CreateDefaultDisplayNodes() # only needed for display
    segmentationNode.SetReferenceImageGeometryParameterFromVolumeNode(inputVolume)

    # Create temporary segment editor to get access to effects
    segmentEditorWidget = slicer.qMRMLSegmentEditorWidget()
    segmentEditorWidget.setMRMLScene(slicer.mrmlScene)
    segmentEditorNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSegmentEditorNode")
    segmentEditorWidget.setMRMLSegmentEditorNode(segmentEditorNode)
    segmentEditorWidget.setSegmentationNode(segmentationNode)
    segmentEditorWidget.setMasterVolumeNode(inputVolume)

    # Create a new segment in segemnt editor effects
    addedSegmentID = segmentationNode.GetSegmentation().AddEmptySegment("cran")
    segmentEditorNode.SetSelectedSegmentID(addedSegmentID)

    # thresholding
    #getting bone threshold value min and maximum
    import vtkITK
    thresholdCalculator = vtkITK.vtkITKImageThresholdCalculator()
    thresholdCalculator.SetInputData(inputVolume.GetImageData())
    thresholdCalculator.SetMethodToOtsu()
    thresholdCalculator.Update()
    boneThresholdValue = thresholdCalculator.GetThreshold()
    volumeScalarRange = inputVolume.GetImageData().GetScalarRange()
    logging.info("Volume minimum = {0}, maximum = {1}, bone threshold = {2}".format(volumeScalarRange[0], volumeScalarRange[1], boneThresholdValue))


    #applying threshold effect
    segmentEditorWidget.setActiveEffectByName("Threshold")
    effect = segmentEditorWidget.activeEffect()
    effect.setParameter("MinimumThreshold",str(boneThresholdValue))
    effect.setParameter("MaximumThreshold",str(volumeScalarRange[1]))
    #effect.setParameter("MinimumThreshold",0.0)#11130.40)#9386.40)
    #effect.setParameter("MaximumThreshold",0)#31049.00)#21807.00)
    #effect.setParameter("AutoThresholdMethod", "OTSU")
    #effect.setParameter("AutoThresholdMode","SET_UPPER")
    effect.self().onApply()


    #use shrink wrapping to wrap the bone and get the full surface
    segmentEditorWidget.setActiveEffectByName("Wrap Solidify")
    effect = segmentEditorWidget.activeEffect()
    segmentEditorWidget.setCurrentSegmentID(segmentationNode.GetSegmentation().GetSegmentIdBySegmentName("cran"))
    effect.setParameter("region", "outerSurface")
    effect.setParameter("regionSegmentID", "segment")
    #effect.setParameter("REGION_OUTER_SURFACE", "outerSurface")
    #effect.setParameter("REGION_LARGEST_CAVITY", "largestCavity")
    effect.setParameter("carveHolesInOuterSurface", True)
    effect.setParameter("carveHolesInOuterSurfaceDiameter", 10)
    effect.setParameter("smoothingFactor", 0.5)
    effect.setParameter("shrinkwrapIterations", 9)
    effect.setParameter("outputType", "segment")
    #effect.setParameter("outputModelNode", segmentName)
    effect.self().onApply()


    #model maker module
    """labelmapVolumeNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLLabelMapVolumeNode")
    slicer.modules.segmentations.logic().ExportVisibleSegmentsToLabelmapNode(segmentationNode, labelmapVolumeNode, inputVolume)
    parameters = {}
    parameters['Name'] = "model"
    parameters["InputVolume"] = labelmapVolumeNode.GetID()
    parameters['FilterType'] = "Laplacian"

    # build only the currently selected model.
    parameters['Labels'] = ""
    parameters["StartLabel"] = -1
    parameters["EndLabel"] = -1

    parameters['GenerateAll'] = True
    parameters["JointSmoothing"] = False
    parameters["SplitNormals"] = False
    parameters["PointNormals"] = False
    parameters["SkipUnNamed"] = True


    parameters["Decimate"] = 0.00
    parameters["Smooth"] = 10


    outHierarchy = slicer.vtkMRMLModelHierarchyNode()
    outHierarchy.SetScene( slicer.mrmlScene )
    outHierarchy.SetName( "Editor Models" )
    slicer.mrmlScene.AddNode( outHierarchy )

    parameters["ModelSceneFile"] = outHierarchy

    modelMaker = slicer.modules.modelmaker

    #self.CLINode = slicer.cli.run(modelMaker, self.CLINode, parameters)
    slicer.cli.run(modelMaker, None, parameters)


    #segmentationNode = slicer.util.loadSegmentation(labelmapVolumeNode)"""
    slicer.modules.segmentations.logic().ExportSegmentsClosedSurfaceRepresentationToFiles(fold_path, segmentationNode)


    #triangulation
    import gmsh
    import pyvista as pv
    import pyacvd
    import math
    import meshio
    surfacemesh = pv.read(fold_path+"/"+segmentationNode.GetName()+"_cran.stl")
    print(surfacemesh)
    clus = pyacvd.Clustering(surfacemesh)
    #clus.subdivide(3)
    clus.cluster(4000)
    nmesh = clus.create_mesh()
    #print(nClusters)

    filePath =fold_path+"/surfaceMeshModel.stl"
    nmesh.save(filePath)

    sMeshModel = slicer.util.loadModel(filePath)

    n = slicer.util.getNode(sMeshModel.GetID())
    nn = n.GetModelDisplayNode()
    #nn.EdgeVisibilityOff()
    nn.VisibilityOff()


    gmsh.initialize()

    gmsh.merge(filePath)
    print(fold_path+"/"+segmentationNode.GetName()+"_cran.stl")
    angle = 40
    forceParametrizablePatches = True
    includeBoundary = False
    curveAngle = 120

    gmsh.model.mesh.classifySurfaces(angle * math.pi / 180., includeBoundary,forceParametrizablePatches, curveAngle * math.pi / 180.)

    gmsh.model.mesh.createGeometry()

    n = gmsh.model.getDimension()
    s = gmsh.model.getEntities(n)
    l = gmsh.model.geo.addSurfaceLoop([s[i][1] for i in range(len(s))])
    gmsh.model.geo.addVolume([l])
    #print("Volume added")
    gmsh.model.geo.synchronize()
    funny = False
    f = gmsh.model.mesh.field.add("MathEval")
    if funny:
        gmsh.model.mesh.field.setString(f, "F", "2*Sin((x+y)/5) + 3")
    else:
        gmsh.model.mesh.field.setString(f, "F", "4")
    gmsh.model.mesh.field.setAsBackgroundMesh(f)


    gmsh.model.mesh.generate(2)
    gmsh.write(fold_path+"/brainmask_auto.msh")


    gmsh.finalize()


    # mesh = meshio.read(fold_path+"/brainmask_auto.msh")
    # nodes = mesh.points
    # cells = mesh.cells_dict["triangle"]
    # meshio.write_points_cells(fold_path+"/vMesh.vtk", nodes,[("triangle", cells)])

    # outputModel = slicer.util.loadModel(fold_path+"/vMesh.vtk")


    # n = slicer.util.getNode(outputModel.GetID())
    # nn = n.GetModelDisplayNode()
    # nn.EdgeVisibilityOn()
    # nn.SliceIntersectionVisibilityOn()
    # nn.SetSliceIntersectionThickness(3)
    # nn.SetColor(1,1,0)

    # """gmsh.model.mesh.generate(3)
    # gmsh.write(fold_path+"/brainmask_auto2.msh")


    # gmsh.finalize()

    # mesh2 = meshio.read(fold_path+"/brainmask_auto2.msh")
    # nodes2 = mesh2.points
    # cells2 = mesh2.cells_dict["tetra"]
    # meshio.write_points_cells(fold_path+"/vMesh2.vtk", nodes2,[("tretra", cells2)])

    # outputModel2 = slicer.util.loadModel(fold_path+"/vMesh2.vtk")

    # n = slicer.util.getNode(outputModel2.GetID())
    # nn = n.GetModelDisplayNode()
    # nn.EdgeVisibilityOn()"""
    # gmsh.initialize()

    # gmsh.merge(filePath)
    # print(fold_path+"/"+segmentationNode.GetName()+"_cran.stl")
    # angle = 40
    # forceParametrizablePatches = True
    # includeBoundary = False
    # curveAngle = 120

    # gmsh.model.mesh.classifySurfaces(angle * math.pi / 180., includeBoundary,forceParametrizablePatches, curveAngle * math.pi / 180.)

    # gmsh.model.mesh.createGeometry()

    # n = gmsh.model.getDimension()
    # s = gmsh.model.getEntities(n)
    # l = gmsh.model.geo.addSurfaceLoop([s[i][1] for i in range(len(s))])
    # gmsh.model.geo.addVolume([l])
    # #print("Volume added")
    # gmsh.model.geo.synchronize()
    # funny = False
    # f = gmsh.model.mesh.field.add("MathEval")
    # if funny:
    #     gmsh.model.mesh.field.setString(f, "F", "2*Sin((x+y)/5) + 3")
    # else:
    #     gmsh.model.mesh.field.setString(f, "F", "4")
    # gmsh.model.mesh.field.setAsBackgroundMesh(f)


    # gmsh.model.mesh.generate(3)
    # gmsh.write(fold_path+"/brainmask_auto2.msh")


    # gmsh.finalize()
    # mesh2 = meshio.read(fold_path+"/brainmask_auto2.msh")
    # nodes2 = mesh2.points
    # cells2 = mesh2.cells_dict["tetra"]
    # meshio.write_points_cells(fold_path+"/vMesh2.vtk", nodes2,[("tetra", cells2)])

    # outputModel2 = slicer.util.loadModel(fold_path+"/vMesh2.vtk")

    # n = slicer.util.getNode(outputModel2.GetID())
    # nn = n.GetModelDisplayNode()
    # nn.EdgeVisibilityOn()
    # nn.SliceIntersectionVisibilityOn()
    # nn.SetSliceIntersectionOpacity(0.3)
    # nn.SetColor(128/225,174/225,128/225) #green color

    stopTime = time.time()
    logging.info('Processing completed in {0:.2f} seconds'.format(stopTime-startTime))

#
# ComputationalGridGeneratorTest
#

class ComputationalGridGeneratorTest(ScriptedLoadableModuleTest):
  """
  This is the test case for your scripted module.
  Uses ScriptedLoadableModuleTest base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setUp(self):
    """ Do whatever is needed to reset the state - typically a scene clear will be enough.
    """
    slicer.mrmlScene.Clear()

  def runTest(self):
    """Run as few or as many tests as needed here.
    """
    self.setUp()
    self.test_ComputationalGridGenerator1()

  def test_ComputationalGridGenerator1(self):
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
    inputVolume = SampleData.downloadSample('ComputationalGridGenerator1')
    self.delayDisplay('Loaded test data set')

    inputScalarRange = inputVolume.GetImageData().GetScalarRange()
    self.assertEqual(inputScalarRange[0], 0)
    self.assertEqual(inputScalarRange[1], 695)

    outputVolume = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLScalarVolumeNode")
    threshold = 100

    # Test the module logic

    logic = ComputationalGridGeneratorLogic()

    # Test algorithm with non-inverted threshold
    logic.process(inputVolume, outputVolume, threshold, True)
    outputScalarRange = outputVolume.GetImageData().GetScalarRange()
    self.assertEqual(outputScalarRange[0], inputScalarRange[0])
    self.assertEqual(outputScalarRange[1], threshold)

    # Test algorithm with inverted threshold
    logic.process(inputVolume, outputVolume, threshold, False)
    outputScalarRange = outputVolume.GetImageData().GetScalarRange()
    self.assertEqual(outputScalarRange[0], inputScalarRange[0])
    self.assertEqual(outputScalarRange[1], inputScalarRange[1])

    self.delayDisplay('Test passed')
