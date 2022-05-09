import os
import unittest
import logging
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin
import numpy as np
#
# NodeSelector
#

class NodeSelector(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "NodeSelector"  # TODO: make this more human readable by adding spaces
    self.parent.categories = ["Image as a Model"]  # TODO: set categories (folders where the module shows up in the module selector)
    self.parent.dependencies = []  # TODO: add here list of module names that this module requires
    self.parent.contributors = ["Saima Safdar"]  # TODO: replace with "Firstname Lastname (Organization)"
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
# NodeSelectorWidget
#

class NodeSelectorWidget(ScriptedLoadableModuleWidget, VTKObservationMixin):
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
    uiWidget = slicer.util.loadUI(self.resourcePath('UI/NodeSelector.ui'))
    self.layout.addWidget(uiWidget)
    self.ui = slicer.util.childWidgetVariables(uiWidget)

    # Set scene in MRML widgets. Make sure that in Qt designer
    # "mrmlSceneChanged(vtkMRMLScene*)" signal in is connected to each MRML widget's.
    # "setMRMLScene(vtkMRMLScene*)" slot.
    uiWidget.setMRMLScene(slicer.mrmlScene)

    # Create a new parameterNode (it stores user's node and parameter values choices in the scene)
    self.logic = NodeSelectorLogic()
    self.ui.parameterNodeSelector.addAttribute("vtkMRMLScriptedModuleNode", "ModuleName", self.moduleName)
    self.setParameterNode(self.logic.getParameterNode())

    # Connections
    self.ui.parameterNodeSelector.connect('currentNodeChanged(vtkMRMLNode*)', self.setParameterNode)

    self.ui.inputSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
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
    self.ui.advancedCollapsibleButton.enabled = self._parameterNode is not None
    if self._parameterNode is None:
      return

    # Update each widget from parameter node

    wasBlocked = self.ui.inputSelector.blockSignals(True)
    self.ui.inputSelector.setCurrentNode(self._parameterNode.GetNodeReference("InputVolume"))
    self.ui.inputSelector.blockSignals(wasBlocked)

    wasBlocked = self.ui.outputSelector.blockSignals(True)
    self.ui.outputSelector.setCurrentNode(self._parameterNode.GetNodeReference("OutputVolume"))
    self.ui.outputSelector.blockSignals(wasBlocked)

    

    

    # Update buttons states and tooltips
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

    self._parameterNode.SetNodeReferenceID("InputVolume", self.ui.inputSelector.currentNodeID)
    self._parameterNode.SetNodeReferenceID("OutputVolume", self.ui.outputSelector.currentNodeID)
    


  def onApplyButton(self):
    """
    Run processing when user clicks "Apply" button.
    """
    try:
      self.logic.run(self.ui.inputSelector.currentNode(), self.ui.outputSelector.currentNode(),
        self.ui.disNodeFile.currentPath, self.ui.skullEleFile.currentPath)
    except Exception as e:
      slicer.util.errorDisplay("Failed to compute results: "+str(e))
      import traceback
      traceback.print_exc()


#
# NodeSelectorLogic
#

class NodeSelectorLogic(ScriptedLoadableModuleLogic):
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
    #print(electrodePos)
    global electrodePosArray1
    electrodePosArray = np.array(electrodePos)
    electrodePosArray1 = np.unique(electrodePosArray)
    print("electrode array unique:", electrodePosArray1)
    print("Nuber of Cells")
    print(len(electrodePosArray1))
    print(arr)
    #cells to nodel selection on brain surface
    
    return electrodePosArray1    

  def run(self, inputVolume, outputVolume, disFile, skullEleFile):
    """
    Run the processing algorithm.
    Can be used without GUI widget.
    """

    if not inputVolume or not outputVolume:
      raise ValueError("Input or output volume is invalid")

    logging.info('Processing started')

    # Compute the thresholded output volume using the Threshold Scalar Volume CLI module
    import time
    start_time = time.time()
    markupsNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsFiducialNode")
    markupsNode.CreateDefaultDisplayNodes()
    modelNode = slicer.util.getNode(inputVolume.GetID()) # selecting all the nodes in this model
    meshModel = modelNode.GetMesh()    #getting mesh of the model
    points = meshModel.GetPoints()
    nPoints = points.GetNumberOfPoints()
    for i in range(nPoints):
        p = points.GetPoint(i)
       
        #
        markupsNode.AddFiducial(p[0],p[1],p[2])
    

    d = markupsNode.GetDisplayNode()
    d.PointLabelsVisibilityOff()
    
    #getting thre seconf mesh model and highlight the cells on the model using the created fiducials
    modelNode2 = slicer.util.getNode(outputVolume.GetID()) # select cells in this model
    
    cellScalars = modelNode2.GetMesh().GetCellData()
    selectionArray = cellScalars.GetArray('selection')
    if not selectionArray:
      selectionArray = vtk.vtkIntArray()
      selectionArray.SetName('selection')
      selectionArray.SetNumberOfValues(modelNode2.GetMesh().GetNumberOfCells())
      selectionArray.Fill(0)
      cellScalars.AddArray(selectionArray)
      
    modelNode2.GetDisplayNode().SetActiveScalar("selection", vtk.vtkAssignAttribute.CELL_DATA)
    modelNode2.GetDisplayNode().SetAndObserveColorNodeID("vtkMRMLColorTableNodeWarm1")
    modelNode2.GetDisplayNode().SetScalarVisibility(True)
    
    cell = vtk.vtkCellLocator()
    cell.SetDataSet(modelNode2.GetMesh())
    cell.BuildLocator()
   
    arr = self.onPointsModified(selectionArray, markupsNode, cell) 
    #get the brain volume so the reference displaced node ids can be collected
    #brainVol = slicer.util.getNode(brainVolume.GetID()) # select cells in this model
    #brainMesh = brainVol.GetMesh()
    
    disNodes = []
    markupsNode2 = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsFiducialNode")
    markupsNode2.CreateDefaultDisplayNodes()
    mesh = modelNode2.GetMesh()
    print("nodes within slicer")
    nodeCoordinates = open(disFile,"w+")

    for i in range(len(arr)):
        cell = mesh.GetCell(int(arr[i]))
        #cell2 = mesh.GetCell(int(arr[i]+1))
        #print(cell2)
        points = cell.GetPoints()
        pointIds = cell.GetPointIds()
        p1 = pointIds.GetId(0)
        p2 = pointIds.GetId(1)
        p3 = pointIds.GetId(2)
        
        print(p1, p2, p3)
        #disNodes.append(p1+1)
        #disNodes.append(p2+1)
        #disNodes.append(p3+1)
        #ff.write(str(p1))
        #ff.write("\n")
        #ff.write(str(p2))
        #ff.write("\n")
        #ff.write(str(p3))
        #ff.write("\n")
        #points = closestCell.GetPoints()
        pointOne = points.GetPoint(0)
        a1 = np.array(pointOne)
        pointTwo = points.GetPoint(1)
        a2 = np.array(pointTwo)
        pointThree = points.GetPoint(2)
        a3 = np.array(pointThree)
        print(p1,',',a1[0],',',a1[1],',',a1[2])
        print(p2,',',a2[0],',',a2[1],',',a2[2])
        print(p3,',',a3[0],',',a3[1],',',a3[2])
        #write the node coordinates to file directly
        disNodes.append(p1+1)
        disNodes.append(p2+1)
        disNodes.append(p3+1)
        print(pointOne,"\n")
        print(pointTwo,"\n")
        print(pointThree,"\n")
        #nodeCoordinates.write(str(a1[0])+","+str(a1[1])+","+str(a1[2])+"\n")
        #nodeCoordinates.write(str(a2[0])+","+str(a2[1])+","+str(a2[2])+"\n")
        #nodeCoordinates.write(str(a3[0])+","+str(a3[1])+","+str(a3[2])+"\n")

        markupsNode2.AddFiducial(a1[0],a1[1],a1[2],str(p1+1))
        markupsNode2.AddFiducial(a2[0],a2[1],a2[2],str(p2+1))
        markupsNode2.AddFiducial(a3[0],a3[1],a3[2],str(p3+1))
        
        #get the projected electrode locations
        
    
    nodeCoordinates.close()
    d = markupsNode2.GetDisplayNode()
    #d.PointLabelsVisibilityOff()
    #save the displaced nodes in the file
    arrNumpy = np.array(disNodes)
    np.savetxt(disFile,arrNumpy, fmt="%s", delimiter=",")
    
    #saving skull cell numbers in the file
    if skullEleFile:
        print(arr)
        arr = [i+1 for i in arr]
        print(arr)
        np.savetxt(skullEleFile,arr, fmt="%s", delimiter=",")
    
    
    logging.info('Processing completed')
#
# NodeSelectorTest
#

class NodeSelectorTest(ScriptedLoadableModuleTest):
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
    self.test_NodeSelector1()

  def test_NodeSelector1(self):
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

    logic = NodeSelectorLogic()

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
