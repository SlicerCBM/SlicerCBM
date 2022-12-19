import os
import unittest
import logging
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin

#
# Fusion
#

class Fusion(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "Fusion"  # TODO: make this more human readable by adding spaces
    self.parent.categories = ["CBM.Bioelectric.HeadModel"]  # TODO: set categories (folders where the module shows up in the module selector)
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
# FusionWidget
#

class FusionWidget(ScriptedLoadableModuleWidget, VTKObservationMixin):
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
    uiWidget = slicer.util.loadUI(self.resourcePath('UI/Fusion.ui'))
    self.layout.addWidget(uiWidget)
    self.ui = slicer.util.childWidgetVariables(uiWidget)

    # Set scene in MRML widgets. Make sure that in Qt designer
    # "mrmlSceneChanged(vtkMRMLScene*)" signal in is connected to each MRML widget's.
    # "setMRMLScene(vtkMRMLScene*)" slot.
    uiWidget.setMRMLScene(slicer.mrmlScene)

    # Create a new parameterNode (it stores user's node and parameter values choices in the scene)
    self.logic = FusionLogic()
    self.ui.parameterNodeSelector.addAttribute("vtkMRMLScriptedModuleNode", "ModuleName", self.moduleName)
    self.setParameterNode(self.logic.getParameterNode())

    # Connections
    self.ui.parameterNodeSelector.connect('currentNodeChanged(vtkMRMLNode*)', self.setParameterNode)

    #self.ui.inputSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
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

    #wasBlocked = self.ui.inputSelector.blockSignals(True)
    #self.ui.inputSelector.setCurrentNode(self._parameterNode.GetNodeReference("InputVolume"))
    #self.ui.inputSelector.blockSignals(wasBlocked)

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

    #self._parameterNode.SetNodeReferenceID("InputVolume", self.ui.inputSelector.currentNodeID)
    self._parameterNode.SetNodeReferenceID("OutputVolume", self.ui.outputSelector.currentNodeID)
    

  def onApplyButton(self):
    """
    Run processing when user clicks "Apply" button.
    """
    try:
      self.logic.run(self.ui.outputSelector.currentNode(), self.ui.skullGrow.value, self.ui.scalpGrow.value)
    except Exception as e:
      slicer.util.errorDisplay("Failed to compute results: "+str(e))
      import traceback
      traceback.print_exc()


#
# FusionLogic
#

class FusionLogic(ScriptedLoadableModuleLogic):
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

  def run(self,outputVolume, skullGrow, scalpGrow):
    """
    Run the processing algorithm.
    Can be used without GUI widget.
    """

    if not outputVolume:
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
    
    #outputVolume1 = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLLabelMapVolumeNode")
    #slicer.vtkSlicerVolumesLogic().CreateLabelVolumeFromVolume(slicer.mrmlScene, outputVolume1, outputVolume)
    # Create segmentation
    print(type(skullGrow))
    segmentationNode = slicer.vtkMRMLSegmentationNode()
    slicer.mrmlScene.AddNode(segmentationNode)
    segmentationNode.CreateDefaultDisplayNodes() # only needed for display
    segmentationNode.SetReferenceImageGeometryParameterFromVolumeNode(outputVolume)
    brainID = segmentationNode.GetSegmentation().AddEmptySegment("brain")
    #outputVolume1.SetName("brain")
    
    #segmentationNode.SetReferenceImageGeometryParameterFromVolumeNode(inputVolume)
    # Create segment editor to get access to effects
    segmentEditorWidget = slicer.qMRMLSegmentEditorWidget()
    # To show segment editor widget (useful for debugging): segmentEditorWidget.show()
    segmentEditorWidget.setMRMLScene(slicer.mrmlScene)
    segmentEditorNode = slicer.vtkMRMLSegmentEditorNode()
    #segmentEditorNode.SetOverwriteMode(1)

    slicer.mrmlScene.AddNode(segmentEditorNode)
    segmentEditorWidget.setMRMLSegmentEditorNode(segmentEditorNode)
    segmentEditorWidget.setSegmentationNode(segmentationNode)
    segmentEditorWidget.setMasterVolumeNode(outputVolume)
    
    
   
    
    
    #import volume to labelmap     
    #slicer.modules.segmentations.logic().ImportLabelmapToSegmentationNode(outputVolume1, segmentationNode) 
    #segmentationNode.CreateClosedSurfaceRepresentation()
    #segmentEditorWidget.setCurrentSegmentID(segmentationNode.GetSegmentation().GetNthSegmentID(0))
    
    
    
    #threshold
    segmentEditorWidget.setActiveEffectByName("Threshold")
    effect = segmentEditorWidget.activeEffect()
    effect.setParameter("MinimumThreshold","2")
    effect.setParameter("MaximumThreshold","255")
    effect.self().onApply()
    
    #masking to allow overlap modify all segments
    #segmentEditorNode.SetMaskSegmentID(
    segmentEditorNode.SetOverwriteMode(slicer.vtkMRMLSegmentEditorNode.OverwriteNone)
    #segmentEditorNode.SetMaskMode(slicer.vtkMRMLSegmentEditorNode.OverwriteNone)
    
    
    #add another segment skull
    skullID = segmentationNode.GetSegmentation().AddEmptySegment("Skull")
    
    
    
    
    #copy brain into this new segment
    segmentEditorWidget.setActiveEffectByName("Logical operators")
    effect = segmentEditorWidget.activeEffect()
    effect.setParameter("Operation", "COPY")
    
    #effect.setParameter("SelectedSegmentID", skull) 
    effect.setParameter("ModifierSegmentID", brainID) 
    segmentEditorWidget.setCurrentSegmentID(skullID)
    effect.self().onApply()
   
    #grow the skull
    
    segmentEditorWidget.setActiveEffectByName("Margin")
    effect = segmentEditorWidget.activeEffect()
    segmentEditorWidget.setSegmentationNode(segmentationNode)
    segmentEditorWidget.setCurrentSegmentID(skullID)
    segmentEditorWidget.setActiveEffectByName("Margin")
    effect = segmentEditorWidget.activeEffect()
    effect.setParameter("MarginSizeMm",str(skullGrow))
    effect.self().onApply()
    
   
    
    segmentEditorWidget.setActiveEffectByName("Logical operators")
    effect = segmentEditorWidget.activeEffect()
    effect.setParameter("Operation", "SUBTRACT")
    effect.setParameter("ModifierSegmentID",brainID) 
    segmentEditorWidget.setCurrentSegmentID(skullID)
    effect.self().onApply()
    #create new segment scalp and subtract skull and brain1
    scalpID = segmentationNode.GetSegmentation().AddEmptySegment("Scalp")
     
    #copy brain into this new segment
    segmentEditorWidget.setActiveEffectByName("Logical operators")
    effect = segmentEditorWidget.activeEffect()
    effect.setParameter("Operation", "COPY")
    effect.setParameter("ModifierSegmentID", skullID) 
    segmentEditorWidget.setCurrentSegmentID(scalpID)
    effect.self().onApply()
    
    #grow scalp
    segmentEditorWidget.setActiveEffectByName("Margin")
    effect = segmentEditorWidget.activeEffect()
    segmentEditorWidget.setSegmentationNode(segmentationNode)
    segmentEditorWidget.setCurrentSegmentID(scalpID)
    segmentEditorWidget.setActiveEffectByName("Margin")
    effect = segmentEditorWidget.activeEffect()
    effect.setParameter("MarginSizeMm",str(scalpGrow))
    effect.self().onApply()
    
    #subtract both brain and skull from scalp
   
    
    segmentEditorWidget.setActiveEffectByName("Logical operators")
    effect = segmentEditorWidget.activeEffect()
    effect.setParameter("Operation", "SUBTRACT")
    effect.setParameter("ModifierSegmentID",brainID) 
    segmentEditorWidget.setCurrentSegmentID(scalpID)
    effect.self().onApply()
    
    segmentEditorWidget.setActiveEffectByName("Logical operators")
    effect = segmentEditorWidget.activeEffect()
    effect.setParameter("Operation", "SUBTRACT")
    effect.setParameter("ModifierSegmentID",skullID) 
    segmentEditorWidget.setCurrentSegmentID(scalpID)
    effect.self().onApply()
    
    displayNode = segmentationNode.GetDisplayNode()
    #displayNode.SetSegmentVisibility(skullID, False) 
    #displayNode.SetSegmentVisibility(brainID, False)
    
    #add label maps
    #skull = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLLabelMapVolumeNode")
    wholeBrain = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLLabelMapVolumeNode")
    
    slicer.modules.segmentations.logic().ExportVisibleSegmentsToLabelmapNode(segmentationNode, wholeBrain, outputVolume)
    #displayNode.SetSegmentVisibility(skullID, True)
    #displayNode.SetSegmentVisibility(scalpID, False)
    #slicer.modules.segmentations.logic().ExportVisibleSegmentsToLabelmapNode(segmentationNode, skull, outputVolume)
    
    
    slicer.mrmlScene.RemoveNode(segmentEditorNode)
    """

    
    segmentation.AddEmptySegment("Scalp")
    #copy brain into this new segment
    segmentEditorWidget.setActiveEffectByName("Logical operators")
    effect = segmentEditorWidget.activeEffect()
    effect.setParameter("Operation", "UNION")
    skull = segmentation.GetSegmentIdBySegmentName("skull")
    scalp = segmentation.GetSegmentIdBySegmentName("scalp")
    effect.setParameter("ModifierSegmentID", skull) 
    effect.setParameter("SelectedSegmentID", scalp) 
    #segmentEditorWidget.setCurrentSegmentID(scalp)
    effect.self().onApply()
    
    #grow the scalp
    
    segmentEditorWidget.setActiveEffectByName("Margin")
    effect = segmentEditorWidget.activeEffect()
    segmentEditorWidget.setSegmentationNode(segmentationNode)
    segmentEditorWidget.setCurrentSegmentID(scalp)
    segmentEditorWidget.setActiveEffectByName("Margin")
    effect = segmentEditorWidget.activeEffect()
    effect.setParameter("MarginSizeMm","4")
    effect.self().onApply()
    
     #subtract skull from scalp
    segmentEditorWidget.setActiveEffectByName("Logical operators")
    effect = segmentEditorWidget.activeEffect()
    effect.setParameter("Operation", "SUBTRACT")
    skull = segmentation.GetSegmentIdBySegmentName("skull")
    scalp = segmentation.GetSegmentIdBySegmentName("scalp")
    effect.setParameter("ModifierSegmentID", skull) 
    effect.setParameter("SelectedSegmentID", scalp) 
    #segmentEditorWidget.setCurrentSegmentID(scalp)
    effect.self().onApply()
       
        
         segmentEditorWidget.setActiveEffectByName("Logical operators")
    effect = segmentEditorWidget.activeEffect()
     operationName = "Subtract"
     effect.setParameter("Operation", "SUBTRACT")
    brain = segmentationNode.GetSegmentIdBySegmentName("brain")
    
    
     brain = segmentation.GetSegmentIdBySegmentName("brain")
    >>> brain
    'mask_1'
    >>> skull = segmentation.GetSegmentIdBySegmentName("skull")
    >>> skull
    'mask'
    >>> effect.setParameter("ModifierSegmentID", brain) 
    >>> segmentEditorWidget.setCurrentSegmentID(skull)
    >>> effect.self().onApply()
    >>> 
    
    #export Segmentation to labelmapNode
    slicer.modules.segmentations.logic().ExportVisibleSegmentsToLabelmapNode(segmentationNode, labelmapVolumeNode, masterVolumeNode)
    
    #segment visible
    segmentationNode = slicer.util.getNode('Segmentation')
    displayNode = segmentationNode.GetDisplayNode()
    displayNode.SetAllSegmentsVisibility(False) # Hide all segments
    displayNode.SetSegmentVisibility(leftCerebralCortexSegmentID, True) # Show specific segment
    #getsegment by id
    segmentation = segmentationNode.GetSegmentation()
    leftCerebralCortexSegmentID = segmentation.GetSegmentIdBySegmentName("Left-Cerebral-Cortex")"""
    
    logging.info('Processing completed')

#
# FusionTest
#

class FusionTest(ScriptedLoadableModuleTest):
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
    self.test_Fusion1()

  def test_Fusion1(self):
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

    logic = FusionLogic()

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
