import os
import unittest
import logging
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin

#
# Visualisation
#

class Visualisation(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "Visualisation"  # TODO: make this more human readable by adding spaces
    self.parent.categories = ["CBM.Biomechanical"]  # TODO: set categories (folders where the module shows up in the module selector)
    self.parent.dependencies = []  # TODO: add here list of module names that this module requires
    self.parent.contributors = ["saima safdar"]  # TODO: replace with "Firstname Lastname (Organization)"
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
# VisualisationWidget
#

class VisualisationWidget(ScriptedLoadableModuleWidget, VTKObservationMixin):
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
    uiWidget = slicer.util.loadUI(self.resourcePath('UI/Visualisation.ui'))
    self.layout.addWidget(uiWidget)
    self.ui = slicer.util.childWidgetVariables(uiWidget)

    # Set scene in MRML widgets. Make sure that in Qt designer
    # "mrmlSceneChanged(vtkMRMLScene*)" signal in is connected to each MRML widget's.
    # "setMRMLScene(vtkMRMLScene*)" slot.
    uiWidget.setMRMLScene(slicer.mrmlScene)

    # Create a new parameterNode (it stores user's node and parameter values choices in the scene)
    self.logic = VisualisationLogic()
    self.ui.parameterNodeSelector.addAttribute("vtkMRMLScriptedModuleNode", "ModuleName", self.moduleName)
    self.setParameterNode(self.logic.getParameterNode())

    # Connections
    self.ui.parameterNodeSelector.connect('currentNodeChanged(vtkMRMLNode*)', self.setParameterNode)

    self.ui.inputSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
    self.ui.outputSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
    self.ui.model.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
    #self.ui.imageThresholdSliderWidget.connect("valueChanged(double)", self.updateParameterNodeFromGUI)
    #self.ui.scalarBar.connect('toggled(bool)',self.updateParameterNodeFromGUI)

    self.ui.scalarBar.connect('toggled(bool)',self.onScalarCheckBox)
    self.ui.invertOutputCheckBox.connect("toggled(bool)", self.updateParameterNodeFromGUI)
    
    self.addObserver(slicer.mrmlScene, slicer.mrmlScene.StartCloseEvent, self.onSceneStartClose)
    self.addObserver(slicer.mrmlScene, slicer.mrmlScene.EndCloseEvent, self.onSceneEndClose)

    self.ui.applyButton.connect('clicked(bool)', self.onApplyButton)
    
    

    # Initial GUI update
    self.updateGUIFromParameterNode()
    

  def onScalarCheckBox(self):
    #check un check scalar bar
    self.logic.updateScalarBar(self.scalarBar.checked)
    self.updateParameterNodeFromGUI()
        
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

    wasBlocked = self.ui.model.blockSignals(True)
    self.ui.model.setCurrentNode(self._parameterNode.GetNodeReference("model"))
    self.ui.model.blockSignals(wasBlocked)
    
    wasBlocked = self.ui.scalarBar.blockSignals(True)
    self.ui.scalarBar.checked = (self._parameterNode.GetParameter("scalarBarLabel") == "true")
    self.ui.scalarBar.blockSignals(wasBlocked)


    wasBlocked = self.ui.invertOutputCheckBox.blockSignals(True)
    self.ui.invertOutputCheckBox.checked = (self._parameterNode.GetParameter("Invert") == "true")
    self.ui.invertOutputCheckBox.blockSignals(wasBlocked)
    
   

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
    self._parameterNode.SetNodeReferenceID("model", self.ui.model.currentNodeID)
    self._parameterNode.SetParameter("scalarBarLabel", "true" if self.scalarBar.checked else "false")
    #self._parameterNode.SetParameter("Threshold", str(self.ui.imageThresholdSliderWidget.value))
    self._parameterNode.SetParameter("Invert", "true" if self.ui.invertOutputCheckBox.checked else "false")

  def onApplyButton(self):
    """
    Run processing when user clicks "Apply" button.
    """
    try:
      self.logic.run(self.ui.inputSelector.currentNode(), self.ui.outputSelector.currentNode(),
        self.ui.model.currentNode(), self.ui.invertOutputCheckBox.checked)
    except Exception as e:
      slicer.util.errorDisplay("Failed to compute results: "+str(e))
      import traceback
      traceback.print_exc()


#
# VisualisationLogic
#

class VisualisationLogic(ScriptedLoadableModuleLogic):
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
      
  def onProcessingStatusUpdate(self, cliNode, event):
    print("Got a %s from a %s" % (event, cliNode.GetClassName()))
    if cliNode.IsA('vtkMRMLCommandLineModuleNode'):
      print("Status is %s" % cliNode.GetStatusString())
    if cliNode.GetStatus() & cliNode.Completed:
      if cliNode.GetStatus() & cliNode.ErrorsMask:
        # error
        errorText = cliNode.GetErrorText()
        print("CLI execution failed: " + errorText)
      else:
        # success
        print("CLI execution succeeded. Output model node ID: "+cliNode.GetParameterAsString("OutputGeometry"))
        
  def updateScalarBar(self, scalarBar=False):
      if scalarBar:
        sliceAnnotations = slicer.modules.DataProbeInstance.infoWidget.sliceAnnotations
        sliceAnnotations.scalarBarEnabled=True
        sliceAnnotations.updateSliceViewFromGUI()
        # Disable slice annotations persistently (after Slicer restarts)
        settings = qt.QSettings()
        settings.setValue("DataProbe/sliceViewAnnotations.enabled", 1)
      else:
        sliceAnnotations = slicer.modules.DataProbeInstance.infoWidget.sliceAnnotations
        sliceAnnotations.scalarBarEnabled=False
        sliceAnnotations.updateSliceViewFromGUI()
        # Disable slice annotations persistently (after Slicer restarts)
        settings = qt.QSettings()
        settings.setValue("DataProbe/sliceViewAnnotations.enabled", 0)
          
    
        
        
  def run(self, inputMRI, inputTransform, model, invert=False):
    """
    Run the processing algorithm.
    Can be used without GUI widget.
    """

    if not inputMRI or not inputTransform:
      raise ValueError("Input or output volume is invalid")

    logging.info('Processing started')

    # Compute the thresholded output volume using the Threshold Scalar Volume CLI module
    #probe model with volume
    #get transform node
    transformNode = slicer.util.getNode(inputTransform.GetID())
    #get scalar volume node
    n = slicer.util.getNode(inputMRI.GetID())
   
    m = slicer.util.getNode(model.GetID())
    #for hardening the transform on the node 
    n.SetAndObserveTransformNodeID(transformNode.GetID())
    n.HardenTransform()
    
    
    #adding new scalar volume node 
    disNode=slicer.mrmlScene.AddNewNodeByClass("vtkMRMLScalarVolumeNode")
    disNode.SetName("displacementFieldVolume")
    #get the displacement field volume node by using transform 
    slicer.modules.transforms.logic().CreateDisplacementVolumeFromTransform(transformNode, n, True, disNode)
    
    #add new model node
    nModel = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLModelNode")
    
    params = {'InputVolume': n.GetID(), 'InputModel': m.GetID(), 'OutputModel' : nModel.GetID()}
    #apply probe model with volume
    #probeLogic = slicer.modules.probevolumewithmodel.logic()
    #probeLogic.Apply(disNode, m)
    cliNode = slicer.cli.runSync(slicer.modules.probevolumewithmodel, None, params)
    #cliNode.AddObserver('ModifiedEvent', onProcessingStatusUpdate)
    
    
    #enable slice annotations
    # Disable slice annotations immediately
    d.EdgeVisibilityOn() #edge visibility of the model
    d.Visibility2DOn() #slice view visibility
    #set clippin 0 off 1 on
    d.SetClipping(0)
    #set opacity of the model 
    d.SetOpacity(0.4)
    #to turn on and off scalars
    d.ScalarVisibilityOn()
    #set scalar range mode
    
    d.SetActiveScalarName("NRRDImage")
    d.SetScalarRangeFlag(0) # manual 0 , active scalar (auto) 1, color table (LUT) 2, data type 3 direct color mapping 4
    
    #for changing the color of the model
    d.SetAndObserveColorNodeID("vtkMRMLColorTableNodeGrey")
#
# VisualisationTest
#

class VisualisationTest(ScriptedLoadableModuleTest):
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
    self.test_Visualisation1()

  def test_Visualisation1(self):
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

    logic = VisualisationLogic()

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
