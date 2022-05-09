import os
import unittest
import logging
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin

#
# BrainMeshSurfaceCellsSelection
#

class BrainMeshSurfaceCellsSelection(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "BrainMeshSurfaceCellsSelection"  # TODO: make this more human readable by adding spaces
    self.parent.categories = ["Examples"]  # TODO: set categories (folders where the module shows up in the module selector)
    self.parent.dependencies = []  # TODO: add here list of module names that this module requires
    self.parent.contributors = ["John Doe (AnyWare Corp.)"]  # TODO: replace with "Firstname Lastname (Organization)"
    self.parent.helpText = """
This is an example of scripted loadable module bundled in an extension.
It performs a simple thresholding on the input volume and optionally captures a screenshot.
"""  # TODO: update with short description of the module
    self.parent.helpText += self.getDefaultModuleDocumentationLink()  # TODO: verify that the default URL is correct or change it to the actual documentation
    self.parent.acknowledgementText = """
This file was originally developed by Jean-Christophe Fillion-Robin, Kitware Inc.
and Steve Pieper, Isomics, Inc. and was partially funded by NIH grant 3P41RR013218-12S1.
"""  # TODO: replace with organization, grant and thanks.

#
# BrainMeshSurfaceCellsSelectionWidget
#

class BrainMeshSurfaceCellsSelectionWidget(ScriptedLoadableModuleWidget, VTKObservationMixin):
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
    uiWidget = slicer.util.loadUI(self.resourcePath('UI/BrainMeshSurfaceCellsSelection.ui'))
    self.layout.addWidget(uiWidget)
    self.ui = slicer.util.childWidgetVariables(uiWidget)

    # Set scene in MRML widgets. Make sure that in Qt designer
    # "mrmlSceneChanged(vtkMRMLScene*)" signal in is connected to each MRML widget's.
    # "setMRMLScene(vtkMRMLScene*)" slot.
    uiWidget.setMRMLScene(slicer.mrmlScene)

    # Create a new parameterNode (it stores user's node and parameter values choices in the scene)
    self.logic = BrainMeshSurfaceCellsSelectionLogic()
    self.ui.parameterNodeSelector.addAttribute("vtkMRMLScriptedModuleNode", "ModuleName", self.moduleName)
    self.setParameterNode(self.logic.getParameterNode())

    # Connections
    self.ui.parameterNodeSelector.connect('currentNodeChanged(vtkMRMLNode*)', self.setParameterNode)

    self.ui.brainVolumeModel.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)

    self.ui.inputSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
    self.ui.outputSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
    #self.ui.imageThresholdSliderWidget.connect("valueChanged(double)", self.updateParameterNodeFromGUI)
    self.ui.invertOutputCheckBox.connect("toggled(bool)", self.updateParameterNodeFromGUI)

    #button for extracting surface model from volume model
    self.ui.saveSurfaceModelButton.connect('clicked(bool)' , self.onApplyExtractSurfaceModelButton)
    
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
    self.ui.advancedCollapsibleButton.enabled = self._parameterNode is not None
    if self._parameterNode is None:
      return

    # Update each widget from parameter node
    wasBlocked = self.ui.brainVolumeModel.blockSignals(True)
    self.ui.brainVolumeModel.setCurrentNode(self._parameterNode.GetNodeReference("brainVolume"))
    self.ui.brainVolumeModel.blockSignals(wasBlocked)



    wasBlocked = self.ui.inputSelector.blockSignals(True)
    self.ui.inputSelector.setCurrentNode(self._parameterNode.GetNodeReference("InputVolume"))
    self.ui.inputSelector.blockSignals(wasBlocked)

    wasBlocked = self.ui.outputSelector.blockSignals(True)
    self.ui.outputSelector.setCurrentNode(self._parameterNode.GetNodeReference("OutputVolume"))
    self.ui.outputSelector.blockSignals(wasBlocked)

    """wasBlocked = self.ui.imageThresholdSliderWidget.blockSignals(True)
    self.ui.imageThresholdSliderWidget.value = float(self._parameterNode.GetParameter("Threshold"))
    self.ui.imageThresholdSliderWidget.blockSignals(wasBlocked)"""

    wasBlocked = self.ui.invertOutputCheckBox.blockSignals(True)
    self.ui.invertOutputCheckBox.checked = (self._parameterNode.GetParameter("Invert") == "true")
    self.ui.invertOutputCheckBox.blockSignals(wasBlocked)

    # Update buttons states and tooltips
    if self._parameterNode.GetNodeReference("brainVolume"):
      self.ui.saveSurfaceModelButton.toolTip = "Compute surface model"
      self.ui.saveSurfaceModelButton.enabled = True
    else:
      self.ui.saveSurfaceModelButton.toolTip = "Select input brain model"
      self.ui.saveSurfaceModelButton.enabled = False
    
    
    if self._parameterNode.GetNodeReference("InputVolume") and self._parameterNode.GetNodeReference("OutputVolume"):
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

    self._parameterNode.SetNodeReferenceID("brainVolume", self.ui.brainVolumeModel.currentNodeID)
    self._parameterNode.SetNodeReferenceID("InputVolume", self.ui.inputSelector.currentNodeID)
    self._parameterNode.SetNodeReferenceID("OutputVolume", self.ui.outputSelector.currentNodeID)
    #self._parameterNode.SetParameter("Threshold", str(self.ui.imageThresholdSliderWidget.value))
    self._parameterNode.SetParameter("Invert", "true" if self.ui.invertOutputCheckBox.checked else "false")

  def onApplyExtractSurfaceModelButton(self):
    """
    Run extract surface method when user clicks "Apply" button.
    """
    try:
      self.logic.extractSurfaceModel(self.ui.brainVolumeModel.currentNode(), self.ui.saveSurfaceModel.currentPath)
    except Exception as e:
      slicer.util.errorDisplay("Failed to compute results: "+str(e))
      import traceback
      traceback.print_exc()  
      
      
      
  def onApplyButton(self):
    """
    Run processing when user clicks "Apply" button.
    """
    try:
      self.logic.run(self.ui.inputSelector.currentNode(), self.ui.outputSelector.currentNode(),self.ui.meshCellFile.currentPath, self.ui.fidFile.currentPath, self.ui.pointFile.currentPath,
        self.ui.invertOutputCheckBox.checked)
    except Exception as e:
      slicer.util.errorDisplay("Failed to compute results: "+str(e))
      import traceback
      traceback.print_exc()


#
# BrainMeshSurfaceCellsSelectionLogic
#

class BrainMeshSurfaceCellsSelectionLogic(ScriptedLoadableModuleLogic):
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
      
  def onPointsModified(self,selectionArray,markupsNode, cell,observer=None, eventid=None):
    #global markupsNode, selectionArray
    selectionArray.Fill(0) # set all cells to non-selected by default
    markupPoints = slicer.util.arrayFromMarkupsControlPoints(markupsNode)
    import numpy as np
    n=0
    arr= np.array([])
    closestPoint = [0.0, 0.0, 0.0]
    cellObj = vtk.vtkGenericCell()
    cellId = vtk.mutable(0)
    subId = vtk.mutable(0)
    dist2 = vtk.mutable(0.0)
    electrodePos=[]
    for markupPoint in markupPoints:
        cell.FindClosestPoint(markupPoint, closestPoint, cellObj, cellId, subId, dist2)
        closestCell = cellId.get()
        arr=np.append(arr,closestCell)
        
        print("markup point",markupPoint)
        print("closest Cell",closestCell)
        if closestCell >=0:
            print("inside")
            n=n+1
            print(n)
            electrodePos.append(closestCell)
            selectionArray.SetValue(closestCell, 100)
        # set selected cell's scalar value to non-zero
    selectionArray.Modified()
    print("The mesh cells Ids under electrodes")
    print(electrodePos)
    print("Nuber of Cells")
    print(len(electrodePos))
    print(arr)
    return arr

  def extractSurfaceModel(self, inputModel, sFile):
    """Run the method to extract and save the surface model from a volume brain model"""
    if not inputModel:
      raise ValueError("Input Model is invalid")
    
    logging.info('Processing started')
    modelNode = slicer.util.getNode(inputModel.GetID()) # extract surface in this model
    #mesh = modelNode.GetMesh()
    dir_path = os.path.dirname(os.path.realpath(__file__))
    file_path ="/home/saima/volumeMesh.vtk" 
    slicer.util.saveNode(modelNode, dir_path+"/volumeMesh.vtk")    
    #reading vtk file and converting it inp and then reading inp file and and saving the inp file only with s3 elements
    #again readin inp file and converting to stl and reading stl file using the slicer util.load node
    import meshio
    volume_mesh = meshio.read(dir_path+"/volumeMesh.vtk")
    meshio.write(dir_path+"/volumeMesh.inp", volume_mesh)
    #reading inp file and saving only s3 elements
    f = open(dir_path+"/volumeMesh.inp","r")
    o = open(dir_path+"/surfaceFromVolumeMesh.inp","w+")
    lines = f.readlines();
    copy = False
    for l in lines:
        if("C3D4" in l):
            copy = True
            break;
        print(l)
        o.write(l)  
    #saving inp surface mesh file reading it again through meshio and converting it into stl
    o.close()
    f.close()
    surface_mesh = meshio.read(dir_path+"/surfaceFromVolumeMesh.inp")
    meshio.write(dir_path+"/surfaceFromVolumeMesh.stl", surface_mesh)
    #import meshio
    #mesh = meshio.read("/home/saima/slicer/Case Results New/braincran_deformed.vtk")
    meshio.write(sFile, surface_mesh)
      
      
  def run(self, inputVolume, outputVolume, meshFile, fidFile, pointFile,invert=False):
    """
    Run the processing algorithm.
    Can be used without GUI widget.
    """

    if not inputVolume or not outputVolume:
      raise ValueError("Input or output volume is invalid")

    logging.info('Processing started')

    # Compute the thresholded output volume using the Threshold Scalar Volume CLI module
    """cliParams = {
      'InputVolume': inputVolume.GetID(),
      'OutputVolume': outputVolume.GetID(),
      'ThresholdValue' : imageThreshold,
      'ThresholdType' : 'Below' if invert else 'Above'
      }
    cliNode = slicer.cli.run(slicer.modules.thresholdscalarvolume, None, cliParams, wait_for_completion=True)"""
    
    modelNode = slicer.util.getNode(inputVolume.GetID()) # select cells in this model
    markupsNode = slicer.util.getNode(outputVolume.GetID()) # points will be selected at positions specified by this markups fiducial node
    
    cellScalars = modelNode.GetMesh().GetCellData()
    selectionArray = cellScalars.GetArray('selection')
    if not selectionArray:
      selectionArray = vtk.vtkIntArray()
      selectionArray.SetName('selection')
      selectionArray.SetNumberOfValues(modelNode.GetMesh().GetNumberOfCells())
      selectionArray.Fill(0)
      cellScalars.AddArray(selectionArray)
      
    
    modelNode.GetDisplayNode().SetActiveScalar("selection", vtk.vtkAssignAttribute.CELL_DATA)
    modelNode.GetDisplayNode().SetAndObserveColorNodeID("vtkMRMLColorTableNodeWarm1")
    modelNode.GetDisplayNode().SetScalarVisibility(True)
    
    cell = vtk.vtkCellLocator()
    cell.SetDataSet(modelNode.GetMesh())
    cell.BuildLocator()  
    
    arr = self.onPointsModified(selectionArray, markupsNode, cell)
    print(arr)
    import numpy as np
    arr_new = np.array(arr)
    arr_new1 = np.unique(arr_new)
    arr_new1.sort()
    
    print(arr_new1)
    print(len(arr_new1))
    
    fff=open(meshFile,"w+")
    i=0
    for x in range(len(arr_new1)):
        fff.write(str(int(arr_new1[i])))
        fff.write(',')
        print(arr_new1[i])
        i=i+1
    
    fff.close()
    f = open(fidFile,"w+")
    import numpy
    mesh = modelNode.GetMesh()
    j = 1;
    f.write("# Markups fiducial file version = 4.4\n")
    f.write("# CoordinateSystem = 0\n")
    f.write("# columns = id,x,y,z,ow,ox,oy,oz,vis,sel,lock,label,desc,associatedNodeID)\n")        
    
    ff = open(pointFile,"w+")


    for i in range(len(arr_new1)):
        
        cell = mesh.GetCell(int(arr_new1[i]))
        #cell2 = mesh.GetCell(int(arr[i]+1))
        #print(cell2)
        points = cell.GetPoints()
        pointIds = cell.GetPointIds()
        p1 = pointIds.GetId(0)
        p2 = pointIds.GetId(1)
        p3 = pointIds.GetId(2)
        #print(p1, p2, p3)
        ff.write(str(p1))
        ff.write("\n")
        ff.write(str(p2))
        ff.write("\n")
        ff.write(str(p3))
        ff.write("\n")
        #points = closestCell.GetPoints()
        pointOne = points.GetPoint(0)
        a1 = numpy.array(pointOne)
        print(a1)
        pointTwo = points.GetPoint(1)
        a2 = numpy.array(pointTwo)
        print(a2)
        pointThree = points.GetPoint(2)
        a3 = numpy.array(pointThree)
        print(a3)
        
        print("get point/node ids:"+str(p1)+" "+str(p2)+" "+str(p3)+"\n")
        print("cell Id"+str(cell))
        print(int(arr_new1[i]))
        
        ax_avg = (a1[0]+a2[0]+a3[0])/3
        ay_avg = (a1[1]+a2[1]+a3[1])/3
        az_avg = (a1[2]+a2[2]+a3[2])/3
        
        #print(points, pointOne, pointTwo, pointThree)
        #f.write("vtkMRMLMarkupsFiducialNode_%d,%.8f,%.8f,%.8f,0,0,0,1,1,1,0,F-%d,vtkMRMLScalarVolumeNode2\n" %(p1,a1[0], a1[1], a1[2], j))
        #f.write("vtkMRMLMarkupsFiducialNode_%d,%.8f,%.8f,%.8f,0,0,0,1,1,1,0,F-%d,vtkMRMLScalarVolumeNode2\n" %(p2,a2[0], a2[1], a2[2], j+1))
        #f.write("vtkMRMLMarkupsFiducialNode_%d,%.8f,%.8f,%.8f,0,0,0,1,1,1,0,F-%d,vtkMRMLScalarVolumeNode2\n" %(p3,a3[0], a3[1], a3[2], j+2))
        
        f.write("vtkMRMLMarkupsFiducialNode_%d,%.8f,%.8f,%.8f,0,0,0,1,1,1,0,F-%d,vtkMRMLScalarVolumeNode2\n" %(j,ax_avg, ay_avg, az_avg, j))
        j = j+3

    f.close()
    ff.close()

    logging.info('Processing completed')

#
# BrainMeshSurfaceCellsSelectionTest
#

class BrainMeshSurfaceCellsSelectionTest(ScriptedLoadableModuleTest):
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
    self.test_BrainMeshSurfaceCellsSelection1()

  def test_BrainMeshSurfaceCellsSelection1(self):
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

    logic = BrainMeshSurfaceCellsSelectionLogic()

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
