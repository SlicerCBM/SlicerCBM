import os
import unittest
import logging
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin
import nrrd
#
# Fusion2
#

class Fusion2(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "Fusion2"  # TODO: make this more human readable by adding spaces
    self.parent.categories = ["CBM.Bioelectric.HeadModel"]  # TODO: set categories (folders where the module shows up in the module selector)
    self.parent.dependencies = []  # TODO: add here list of module names that this module requires
    self.parent.contributors = ["Saima Safdar"]  # TODO: replace with "Firstname Lastname (Organization)"
    self.parent.helpText = """
It combines all the brain segments segmented using DTI based segmentation in our DTISegmentation module.
"""  # TODO: update with short description of the module
    self.parent.helpText += self.getDefaultModuleDocumentationLink()  # TODO: verify that the default URL is correct or change it to the actual documentation
    self.parent.acknowledgementText = """

"""  # TODO: replace with organization, grant and thanks.

#
# Fusion2Widget
#

class Fusion2Widget(ScriptedLoadableModuleWidget, VTKObservationMixin):
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
    uiWidget = slicer.util.loadUI(self.resourcePath('UI/Fusion2.ui'))
    self.layout.addWidget(uiWidget)
    self.ui = slicer.util.childWidgetVariables(uiWidget)

    # Set scene in MRML widgets. Make sure that in Qt designer
    # "mrmlSceneChanged(vtkMRMLScene*)" signal in is connected to each MRML widget's.
    # "setMRMLScene(vtkMRMLScene*)" slot.
    uiWidget.setMRMLScene(slicer.mrmlScene)

    # Create a new parameterNode (it stores user's node and parameter values choices in the scene)
    self.logic = Fusion2Logic()
    self.ui.parameterNodeSelector.addAttribute("vtkMRMLScriptedModuleNode", "ModuleName", self.moduleName)
    self.setParameterNode(self.logic.getParameterNode())

    # Connections
    self.ui.parameterNodeSelector.connect('currentNodeChanged(vtkMRMLNode*)', self.setParameterNode)
    
    #self.ui.scalpSelector.connect("currentSegmentChanged(QString)", self.onContourChange)
    #self.ui.skullSelector.connect("currentSegmentChanged(QString)", self.onContourChange)

    self.ui.scalpSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
    self.ui.skullSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
    self.ui.brainSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
    self.ui.electrodeSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
    self.ui.wmSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
    self.ui.gmSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
    self.ui.csfSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
    #self.ui.segBrainNode.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
   
    
    
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
    wasBlocked = self.ui.electrodeSelector.blockSignals(True)
    self.ui.electrodeSelector.setCurrentNode(self._parameterNode.GetNodeReference("electrodeSelector"))
    self.ui.electrodeSelector.blockSignals(wasBlocked)
    
    wasBlocked = self.ui.scalpSelector.blockSignals(True)
    self.ui.scalpSelector.setCurrentNode(self._parameterNode.GetNodeReference("scalpSelector"))
    self.ui.scalpSelector.blockSignals(wasBlocked)
    
    wasBlocked = self.ui.skullSelector.blockSignals(True)
    self.ui.skullSelector.setCurrentNode(self._parameterNode.GetNodeReference("skullSelector"))
    self.ui.skullSelector.blockSignals(wasBlocked)
    
    wasBlocked = self.ui.brainSelector.blockSignals(True)
    self.ui.brainSelector.setCurrentNode(self._parameterNode.GetNodeReference("brainSelector"))
    self.ui.brainSelector.blockSignals(wasBlocked)

    wasBlocked = self.ui.wmSelector.blockSignals(True)
    self.ui.wmSelector.setCurrentNode(self._parameterNode.GetNodeReference("wmSelector"))
    self.ui.wmSelector.blockSignals(wasBlocked)

    wasBlocked = self.ui.gmSelector.blockSignals(True)
    self.ui.gmSelector.setCurrentNode(self._parameterNode.GetNodeReference("gmSelector"))
    self.ui.gmSelector.blockSignals(wasBlocked)
    
    wasBlocked = self.ui.csfSelector.blockSignals(True)
    self.ui.csfSelector.setCurrentNode(self._parameterNode.GetNodeReference("csfSelector"))
    self.ui.csfSelector.blockSignals(wasBlocked)
    
    
    # Update buttons states and tooltips
    if self._parameterNode.GetNodeReference("scalpSelector"): #and self._parameterNode.GetNodeReference("skullVolume"):
      self.ui.applyButton.toolTip = "Compute output volume"
      self.ui.applyButton.enabled = True
    else:
      self.ui.applyButton.toolTip = "Select input volume nodes"
      self.ui.applyButton.enabled = False

  def updateParameterNodeFromGUI(self, caller=None, event=None):
    """
    This method is called when the user makes changes in the GUI.
    The changes are saved into the parameter node (so that they are preserved when the scene is saved and loaded).
    """

    if self._parameterNode is None:
      return 
    self._parameterNode.SetNodeReferenceID("scalpSelector", self.ui.scalpSelector.currentNodeID())
    self._parameterNode.SetNodeReferenceID("skullSelector", self.ui.skullSelector.currentNodeID())
    self._parameterNode.SetNodeReferenceID("brainSelector", self.ui.brainSelector.currentNodeID())
    self._parameterNode.SetNodeReferenceID("electrodeSelector", self.ui.electrodeSelector.currentNodeID())
    self._parameterNode.SetNodeReferenceID("wmSelector", self.ui.wmSelector.currentNodeID())
    self._parameterNode.SetNodeReferenceID("gmSelector", self.ui.gmSelector.currentNodeID())
    self._parameterNode.SetNodeReferenceID("csfSelector", self.ui.csfSelector.currentNodeID())

  def onApplyButton(self):
    """
    Run processing when user clicks "Apply" button.
    """
    try:
      self.logic.run(self.ui.imgType.currentIndex, self.ui.scalpSelector.currentNode(), self.ui.scalpSelector.currentSegmentID(), self.ui.skullSelector.currentNode(), self.ui.skullSelector.currentSegmentID(), self.ui.brainSelector.currentNode(), self.ui.brainSelector.currentSegmentID(), self.ui.wmSelector.currentNode(), self.ui.wmSelector.currentSegmentID(), self.ui.gmSelector.currentNode(), self.ui.gmSelector.currentSegmentID(), self.ui.csfSelector.currentNode(), self.ui.csfSelector.currentSegmentID(), self.ui.electrodeSelector.currentNode(), self.ui.electrodeSelector.currentSegmentID())
    except Exception as e:
      slicer.util.errorDisplay("Failed to compute results: "+str(e))
      import traceback
      traceback.print_exc()


#
# Fusion2Logic
#

class Fusion2Logic(ScriptedLoadableModuleLogic):
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

  def run(self, imgType, seg1Node, scalpSelector,seg2Node, skullSelector, seg3Node, brainSelector, seg4Node, wmSelector, seg5Node, gmSelector, seg6Node, csfSelector, seg7Node, electrodeSelector):
    """
    Run the processing algorithm.
    Can be used without GUI widget.
    """

    if not scalpSelector: # or not skullNode:
      raise ValueError("Inputs are invalid")

    logging.info('Processing started')

    # Compute the thresholded output volume using the Threshold Scalar Volume CLI module
    #dir_path = os.path.dirname(os.path.realpath(__file__))
    #slicer.util.saveNode(skullNode, dir_path+"/skullNode.nrrd")
    #skull_mask, skull_header= nrrd.read(dir_path+"/skullNode")
    
    
    #scalp_mask = slicer.util.arrayFromVolume(scalpNode)
    #skull_mask = slicer.util.arrayFromVolume(skullNode)
    #csf_mask = slicer.util.arrayFromVolume(brainNode)
    #sheet_mask = slicer.util.arrayFromVolume(electrodeSheetNode)
    #brain_data = slicer.util.arrayFromVolume(segBrainNode)
    
    print(imgType)
    #segmentationNode = slicer.vtkMRMLSegmentationNode()
    #slicer.mrmlScene.AddNode(segmentationNode)
    #segmentationNode.CreateDefaultDisplayNodes()
    #import volume to labelmap     
    #slicer.modules.segmentations.logic().ImportLabelmapToSegmentationNode(scalpNode, segmentationNode)
    #slicer.modules.segmentations.logic().ImportLabelmapToSegmentationNode(skullNode, segmentationNode)
    print(seg1Node.GetID())
    print(seg2Node.GetID())
    print(seg3Node.GetID())
    print(seg4Node.GetID())
    print(seg5Node.GetID())
    print(seg6Node.GetID())
    print(scalpSelector)
    print(skullSelector)
    print(brainSelector)
    if(imgType==0):
        #create a anew segmentation and delete the csf, wm, gm from the brain combine the remaining brain with csf 
        segmentationNode1 = slicer.vtkMRMLSegmentationNode()
        slicer.mrmlScene.AddNode(segmentationNode1)
        segmentationNode1.CreateDefaultDisplayNodes() # only needed for display
        brainSegment = seg1Node.GetSegmentation().GetSegment(brainSelector)
        wmSegment = seg4Node.GetSegmentation().GetSegment(wmSelector)
        gmSegment = seg5Node.GetSegmentation().GetSegment(gmSelector)
        csfSegment = seg6Node.GetSegmentation().GetSegment(csfSelector)
        
        segmentationNode1.GetSegmentation().CopySegmentFromSegmentation(seg1Node.GetSegmentation(), brainSelector)
        segmentationNode1.GetSegmentation().CopySegmentFromSegmentation(seg5Node.GetSegmentation(), gmSelector)
        segmentationNode1.GetSegmentation().CopySegmentFromSegmentation(seg6Node.GetSegmentation(), csfSelector)
        segmentationNode1.GetSegmentation().CopySegmentFromSegmentation(seg4Node.GetSegmentation(), wmSelector)
    
        
        segmentEditorWidget = slicer.qMRMLSegmentEditorWidget()
        # To show segment editor widget (useful for debugging): segmentEditorWidget.show()
        segmentEditorWidget.setMRMLScene(slicer.mrmlScene)
        segmentEditorNode = slicer.vtkMRMLSegmentEditorNode()
        #segmentEditorWidget.setMasterVolumeNode(wholeBrain)
        #segmentEditorNode.SetOverwriteMode(slicer.vtkMRMLSegmentEditorNode.OverwriteNone)
        segmentEditorNode.SetOverwriteMode(2) 
        #segmentEditorNode.SetOverwriteMode(1)
        
        slicer.mrmlScene.AddNode(segmentEditorNode)
        segmentEditorWidget.setMRMLSegmentEditorNode(segmentEditorNode)
        segmentEditorWidget.setSegmentationNode(segmentationNode1)
        
        #print(wmID)
        #print(brainID)
        #print(segmentationNode.GetID())
        
        segmentEditorWidget.setActiveEffectByName("Logical operators")
        effect = segmentEditorWidget.activeEffect()
        effect.setParameter("Operation", "SUBTRACT")
        effect.setParameter("ModifierSegmentID",wmSelector) 
        segmentEditorWidget.setCurrentSegmentID(brainSelector)
        effect.self().onApply()
        effect.setParameter("ModifierSegmentID",gmSelector)
        effect.self().onApply()
        effect.setParameter("ModifierSegmentID",csfSelector)
        effect.self().onApply()
        
       
        
        #combine the remaining brain and csf segments to fill all the holes in the segmentation file
        segmentEditorWidget.setActiveEffectByName("Logical operators")
        #segmentEditorNode.SetOverwriteMode(slicer.vtkMRMLSegmentEditorNode.OverwriteNone)
        effect = segmentEditorWidget.activeEffect()
        effect.setParameter("Operation", "UNION")
        segmentEditorWidget.setCurrentSegmentID(brainSelector)
        effect.setParameter("ModifierSegmentID", csfSelector)
        effect.self().onApply()
        
        
        
        segmentationNode = slicer.vtkMRMLSegmentationNode()
        slicer.mrmlScene.AddNode(segmentationNode)
        segmentationNode.CreateDefaultDisplayNodes() # only needed for display
        #brainID= segmentationNode.GetSegmentation.GetBinaryLabelMapRepresentation(brainSegment)
        
        empSegID0 = segmentationNode.GetSegmentation().AddEmptySegment("air")
        #segmentationNode.GetSegmentation().GetSegment(empSegID0).SetColor(0,0,0) 
        segmentationNode.GetSegmentation().CopySegmentFromSegmentation(seg1Node.GetSegmentation(), scalpSelector)
        scalpSeg =  segmentationNode.GetSegmentation().GetSegment(scalpSelector)
        scalpSeg.SetColor(255/255,192/255,203/255)
        #displayNode = segmentationNode.GetDisplayNode()
        #displayNode.SetSegmentOverrideColor(scalpSelector, 255, 192, 203)
        segmentationNode.GetSegmentation().CopySegmentFromSegmentation(seg2Node.GetSegmentation(), skullSelector)
        segmentationNode.GetSegmentation().GetSegment(skullSelector).SetColor(255/255,255/255,0)
        empSegID1 = segmentationNode.GetSegmentation().AddEmptySegment("unused")
        segmentationNode.GetSegmentation().CopySegmentFromSegmentation(seg5Node.GetSegmentation(), gmSelector)
        segmentationNode.GetSegmentation().GetSegment(gmSelector).SetColor(128/255,128/255,128/255)
        segmentationNode.GetSegmentation().CopySegmentFromSegmentation(segmentationNode1.GetSegmentation(), brainSelector)
        segmentationNode.GetSegmentation().GetSegment(brainSelector).SetColor(0,0,255/255)
        segmentationNode.GetSegmentation().GetSegment(brainSelector).SetName("csf")
        empSegID2 = segmentationNode.GetSegmentation().AddEmptySegment("unused")
     
        segmentationNode.GetSegmentation().CopySegmentFromSegmentation(seg4Node.GetSegmentation(), wmSelector)
        segmentationNode.GetSegmentation().GetSegment(wmSelector).SetColor(255/255,255/255,255/255)
        
        
        #remove the brainselector segment
        #segmentationNode.GetSegmentation().RemoveSegment(wmSelector)
        
        
        empSegID3 = segmentationNode.GetSegmentation().AddEmptySegment("Maximally Conductive")
        empSegID4 = segmentationNode.GetSegmentation().AddEmptySegment("Manimally Conductive")
        #empSegID5 = segmentationNode.GetSegmentation().AddEmptySegment("electrodeSheetArray")
        #segmentationNode.GetSegmentation().GetSegment(empSegID5).SetColor(255/255,0,0)
        segmentationNode.GetSegmentation().CopySegmentFromSegmentation(seg7Node.GetSegmentation(), electrodeSelector)
        segmentationNode.GetSegmentation().GetSegment(electrodeSelector).SetColor(0,0,0)
        segmentationNode.GetSegmentation().GetSegment(electrodeSelector).SetName("electrode Sheet")
    
    elif(imgType==1):
        segmentationNode1 = slicer.vtkMRMLSegmentationNode()
        slicer.mrmlScene.AddNode(segmentationNode1)
        segmentationNode1.CreateDefaultDisplayNodes() # only needed for display
        brainSegment = seg1Node.GetSegmentation().GetSegment(brainSelector)
        wmSegment = seg4Node.GetSegmentation().GetSegment(wmSelector)
        gmSegment = seg5Node.GetSegmentation().GetSegment(gmSelector)
        csfSegment = seg6Node.GetSegmentation().GetSegment(csfSelector)
        
        segmentationNode1.GetSegmentation().CopySegmentFromSegmentation(seg1Node.GetSegmentation(), brainSelector)
        segmentationNode1.GetSegmentation().CopySegmentFromSegmentation(seg7Node.GetSegmentation(), electrodeSelector)
        segmentationNode1.GetSegmentation().CopySegmentFromSegmentation(seg5Node.GetSegmentation(), gmSelector)
        segmentationNode1.GetSegmentation().CopySegmentFromSegmentation(seg6Node.GetSegmentation(), csfSelector)
        segmentationNode1.GetSegmentation().CopySegmentFromSegmentation(seg4Node.GetSegmentation(), wmSelector)
    
        
        segmentEditorWidget = slicer.qMRMLSegmentEditorWidget()
        # To show segment editor widget (useful for debugging): segmentEditorWidget.show()
        segmentEditorWidget.setMRMLScene(slicer.mrmlScene)
        segmentEditorNode = slicer.vtkMRMLSegmentEditorNode()
        segmentEditorNode.SetOverwriteMode(2)               
        slicer.mrmlScene.AddNode(segmentEditorNode)
        segmentEditorWidget.setMRMLSegmentEditorNode(segmentEditorNode)
        segmentEditorWidget.setSegmentationNode(segmentationNode1)
              
        segmentEditorWidget.setActiveEffectByName("Logical operators")
        effect = segmentEditorWidget.activeEffect()
        effect.setParameter("Operation", "SUBTRACT")
        effect.setParameter("ModifierSegmentID",wmSelector) 
        segmentEditorWidget.setCurrentSegmentID(brainSelector)
        effect.self().onApply()
        effect.setParameter("ModifierSegmentID",gmSelector)
        effect.self().onApply()
        effect.setParameter("ModifierSegmentID",csfSelector)
        effect.self().onApply()
        effect.setParameter("ModifierSegmentID",electrodeSelector)
        effect.self().onApply()


  
        #combine the remaining brain and csf segments to fill all the holes in the segmentation file
        segmentEditorWidget.setActiveEffectByName("Logical operators")
        #segmentEditorNode.SetOverwriteMode(slicer.vtkMRMLSegmentEditorNode.OverwriteNone)
        effect = segmentEditorWidget.activeEffect()
        effect.setParameter("Operation", "UNION")
        segmentEditorWidget.setCurrentSegmentID(brainSelector)
        effect.setParameter("ModifierSegmentID", csfSelector)
        effect.self().onApply()
        
        
        
        segmentationNode = slicer.vtkMRMLSegmentationNode()
        slicer.mrmlScene.AddNode(segmentationNode)
        segmentationNode.CreateDefaultDisplayNodes() # only needed for display
        
        empSegID0 = segmentationNode.GetSegmentation().AddEmptySegment("air")
        segmentationNode.GetSegmentation().CopySegmentFromSegmentation(seg1Node.GetSegmentation(), scalpSelector)
        scalpSeg =  segmentationNode.GetSegmentation().GetSegment(scalpSelector)
        scalpSeg.SetColor(255/255,192/255,203/255)

        segmentationNode.GetSegmentation().CopySegmentFromSegmentation(seg2Node.GetSegmentation(), skullSelector)
        segmentationNode.GetSegmentation().GetSegment(skullSelector).SetColor(255/255,255/255,0)
        empSegID1 = segmentationNode.GetSegmentation().AddEmptySegment("unused")
        segmentationNode.GetSegmentation().CopySegmentFromSegmentation(seg5Node.GetSegmentation(), gmSelector)
        segmentationNode.GetSegmentation().GetSegment(gmSelector).SetColor(128/255,128/255,128/255)
        segmentationNode.GetSegmentation().CopySegmentFromSegmentation(segmentationNode1.GetSegmentation(), brainSelector)
        segmentationNode.GetSegmentation().GetSegment(brainSelector).SetColor(0,0,255/255)
        segmentationNode.GetSegmentation().GetSegment(brainSelector).SetName("csf")
        empSegID2 = segmentationNode.GetSegmentation().AddEmptySegment("unused")
     
        segmentationNode.GetSegmentation().CopySegmentFromSegmentation(seg4Node.GetSegmentation(), wmSelector)
        segmentationNode.GetSegmentation().GetSegment(wmSelector).SetColor(255/255,255/255,255/255)
        
        
        empSegID3 = segmentationNode.GetSegmentation().AddEmptySegment("Maximally Conductive")
        empSegID4 = segmentationNode.GetSegmentation().AddEmptySegment("Manimally Conductive")
  
        segmentationNode.GetSegmentation().CopySegmentFromSegmentation(seg7Node.GetSegmentation(), electrodeSelector)
        segmentationNode.GetSegmentation().GetSegment(electrodeSelector).SetColor(0,0,0)
        segmentationNode.GetSegmentation().GetSegment(electrodeSelector).SetName("electrode Sheet")
        
    
    #segmentationNode.GetSegmentation().CopySegmentFromSegmentation(seg3Node.GetSegmentation(), brainSelector)
    
    
    #brainID = segmentationNode.GetSegmentation().AddSegment(brainSegment)
    
    #wholeBrain = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLLabelMapVolumeNode")
    #slicer.modules.segmentations.logic().ExportVisibleSegmentsToLabelmapNode(segmentationNode, wholeBrain)
   
    #segmentationNode.SetReferenceImageGeometryParameterFromVolumeNode(wholeBrain)
    #segmentationNode.GetSegmentation().AddSegment(wmSegment)
    #segmentationNode.GetSegmentation().AddSegment(gmSegment)
    #segmentationNode.GetSegmentation().AddSegment(csfSegment)
    #wmID = segmentationNode.GetSegmentation().GetSegmentIdBySegmentName(wmSelector)
    #brainID = segmentationNode.GetSegmentation().GetSegmentIdBySegmentName(brainSelector)
    
    
   
    
    
    
    
    
    #segmentEditorNode = self.scriptedEffect.parameterSetNode()
    #segmentationNode = segmentEditorNode.GetSegmentationNode()
    #currentSegmentId = segmentEditorNode.GetSelectedSegmentID()
    #print(segmentEditorNode)
    #slicer.modules.segmentations.logic().ImportLabelmapToSegmentationNode(brainNode, segmentationNode) 
    #
    # FIXME: check: I replaced this now but haven't checked yet (should be int not double)
    
   
    logging.info('Processing completed')

#
# Fusion2Test
#

class Fusion2Test(ScriptedLoadableModuleTest):
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
    self.test_Fusion21()

  def test_Fusion21(self):
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

    logic = Fusion2Logic()

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
