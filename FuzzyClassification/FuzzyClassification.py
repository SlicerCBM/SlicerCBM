import os
import unittest
import logging
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin
import numpy as np
#
# FuzzyClassification
#

class FuzzyClassification(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "FuzzyClassification"  # TODO: make this more human readable by adding spaces
    self.parent.categories = ["CBM.Biomechanical.Property"]  # TODO: set categories (folders where the module shows up in the module selector)
    self.parent.dependencies = []  # TODO: add here list of module names that this module requires
    self.parent.contributors = ["Saima Safdar"]  # TODO: replace with "Firstname Lastname (Organization)"
    self.parent.helpText = """
This is an example of scripted loadable module bundled in an extension.
It module performs fuzzy classification and produces fuzzy classified ventricle, tumour (if present) and parenchyma binary images.
"""  # TODO: update with short description of the module
    self.parent.helpText += self.getDefaultModuleDocumentationLink()  # TODO: verify that the default URL is correct or change it to the actual documentation
    self.parent.acknowledgementText = """
This file was originally developed by Jean-Christophe Fillion-Robin, Kitware Inc.
and Steve Pieper, Isomics, Inc. and was partially funded by NIH grant 3P41RR013218-12S1.
"""  # TODO: replace with organization, grant and thanks.


#
# FuzzyClassificationWidget
#

class FuzzyClassificationWidget(ScriptedLoadableModuleWidget, VTKObservationMixin):
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
    uiWidget = slicer.util.loadUI(self.resourcePath('UI/FuzzyClassification.ui'))
    self.layout.addWidget(uiWidget)
    self.ui = slicer.util.childWidgetVariables(uiWidget)

    # Set scene in MRML widgets. Make sure that in Qt designer
    # "mrmlSceneChanged(vtkMRMLScene*)" signal in is connected to each MRML widget's.
    # "setMRMLScene(vtkMRMLScene*)" slot.
    uiWidget.setMRMLScene(slicer.mrmlScene)

    # Create a new parameterNode (it stores user's node and parameter values choices in the scene)
    self.logic = FuzzyClassificationLogic()
    self.ui.parameterNodeSelector.addAttribute("vtkMRMLScriptedModuleNode", "ModuleName", self.moduleName)
    self.setParameterNode(self.logic.getParameterNode())

    # Connections
    self.ui.parameterNodeSelector.connect('currentNodeChanged(vtkMRMLNode*)', self.setParameterNode)

    self.ui.inputSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
    self.ui.outputSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
    self.ui.tumourSeg.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)

    #self.ui.imageThresholdSliderWidget.connect("valueChanged(double)", self.updateParameterNodeFromGUI)
    #self.ui.invertOutputCheckBox.connect("toggled(bool)", self.updateParameterNodeFromGUI)

    self.ui.nClass.connect("valueChanged(int)", self.updateParameterNodeFromGUI)
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
    #self.ui.advancedCollapsibleButton.enabled = self._parameterNode is not None
    if self._parameterNode is None:
      return

    # Update each widget from parameter node

    wasBlocked = self.ui.inputSelector.blockSignals(True)
    self.ui.inputSelector.setCurrentNode(self._parameterNode.GetNodeReference("InputVolume"))
    self.ui.inputSelector.blockSignals(wasBlocked)

    wasBlocked = self.ui.outputSelector.blockSignals(True)
    self.ui.outputSelector.setCurrentNode(self._parameterNode.GetNodeReference("OutputVolume"))
    self.ui.outputSelector.blockSignals(wasBlocked)

    wasBlocked = self.ui.tumourSeg.blockSignals(True)
    self.ui.tumourSeg.setCurrentNode(self._parameterNode.GetNodeReference("tumourSeg"))
    self.ui.tumourSeg.blockSignals(wasBlocked)

    #wasBlocked = self.ui.imageThresholdSliderWidget.blockSignals(True)
    #self.ui.imageThresholdSliderWidget.value = float(self._parameterNode.GetParameter("Threshold"))
    #self.ui.imageThresholdSliderWidget.blockSignals(wasBlocked)

    wasBlocked = self.ui.nClass.blockSignals(True)
    self.ui.nClass.value = int(self._parameterNode.GetParameter("nnClass"))
    self.ui.nClass.blockSignals(wasBlocked)

    """if(self.ui.nClass.value == 2):
        self.ui.ventricle_file.enabled = True
        self.ui.paren_file.enabled = True


    if(self.ui.nClass.value == 3):
        self.ui.ventricle_file.enabled = True
        self.ui.paren_file.enabled = True
        self.ui.tumor_file.enabled = True"""

    #wasBlocked = self.ui.invertOutputCheckBox.blockSignals(True)
    #self.ui.invertOutputCheckBox.checked = (self._parameterNode.GetParameter("Invert") == "true")
    #self.ui.invertOutputCheckBox.blockSignals(wasBlocked)

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
    self._parameterNode.SetNodeReferenceID("tumourSeg", self.ui.tumourSeg.currentNodeID)

    #self._parameterNode.SetParameter("Threshold", str(self.ui.imageThresholdSliderWidget.value))
    self._parameterNode.SetParameter("nnClass", str(self.ui.nClass.value))
    #self._parameterNode.SetParameter("Invert", "true" if self.ui.invertOutputCheckBox.checked else "false")

  def onApplyButton(self):
    """
    Run processing when user clicks "Apply" button.
    """
    try:
        import skfuzzy as fuzz
    except ModuleNotFoundError as e:
        if slicer.util.confirmOkCancelDisplay("This module requires 'skfuzzy' Python package. Click OK to install (it takes several minutes)."):
            slicer.util.pip_install("scikit-fuzzy")
            import skfuzzy as fuzz

    try:
      self.logic.run(self.ui.inputSelector.currentNode(), self.ui.outputSelector.currentNode(), self.ui.tumourSeg.currentNode(), self.ui.nClass.value)
    except Exception as e:
      slicer.util.errorDisplay("Failed to compute results: "+str(e))
      import traceback
      traceback.print_exc()


#
# FuzzyClassificationLogic
#

class FuzzyClassificationLogic(ScriptedLoadableModuleLogic):
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
    if not parameterNode.GetParameter("nnClass"):
      parameterNode.SetParameter("nnClass", "2")

  def createEmptyVolume(self, imageSize, imageSpacing, nodeName):
    voxelType=vtk.VTK_SHORT
    # Create an empty image volume
    imageData=vtk.vtkImageData()
    imageData.SetDimensions(imageSize)
    imageData.AllocateScalars(voxelType, 1)
    thresholder=vtk.vtkImageThreshold()
    thresholder.SetInputData(imageData)
    thresholder.SetInValue(0)
    thresholder.SetOutValue(0)
    thresholder.Update()
    # Create volume node
    volumeNode=slicer.mrmlScene.AddNewNodeByClass("vtkMRMLScalarVolumeNode", nodeName)
    volumeNode.SetSpacing(imageSpacing)
    volumeNode.SetAndObserveImageData(thresholder.GetOutput())
    volumeNode.CreateDefaultDisplayNodes()
    volumeNode.CreateDefaultStorageNode()
    return volumeNode

  def performVesselness(self, inputNode, brain_ventricle, cutSpacing, createTempVolumes):
    import math
    inputImageArray = brain_ventricle
    dim = inputNode.GetImageData().GetDimensions()
    spacing = inputNode.GetSpacing()
    numOfSlices = [0,0,0]
    for i in range(3):
      numOfSlices[i] = int(math.ceil(dim[i] / cutSpacing[i]))
    print(numOfSlices)
    outputNode = self.createEmptyVolume(dim, spacing, 'VesselnessFiltered')
    outputImageArray = slicer.util.arrayFromVolume(outputNode).copy()
    for ii in range(numOfSlices[0]):
      xMin = ii * cutSpacing[0]
      xMax = min((ii + 1) * cutSpacing[0], dim[0])
      for jj in range(numOfSlices[1]):
        yMin = jj * cutSpacing[1]
        yMax = min((jj + 1) * cutSpacing[1], dim[1])
        for kk in range(numOfSlices[2]):
          zMin = kk * cutSpacing[2]
          zMax = min((kk + 1) * cutSpacing[2], dim[2])
          tileDim = [xMax-xMin, yMax-yMin, zMax-zMin]
          if createTempVolumes:
            tempVolume = self.createEmptyVolume(tileDim, spacing, 'tempV')
            tempVolumeArray = slicer.util.arrayFromVolume(tempVolume)
            tempVolumeArray[:] = inputImageArray[zMin:zMax, yMin:yMax, xMin:xMax]
            outputImageArray[zMin:zMax, yMin:yMax, xMin:xMax] = tempVolumeArray
            slicer.mrmlScene.RemoveNode(tempVolume)
          else:
            outputImageArray[zMin:zMax, yMin:yMax, xMin:xMax] = inputImageArray[zMin:zMax, yMin:yMax, xMin:xMax]
    slicer.util.updateVolumeFromArray(outputNode, outputImageArray)
    # Copy origin, spacing, axis directions
    ijkToRAS = vtk.vtkMatrix4x4()
    inputNode.GetIJKToRASMatrix(ijkToRAS)
    outputNode.SetIJKToRASMatrix(ijkToRAS)
    return outputNode

  def run(self, inputVolume, outputVolume, tumourSeg,  nClass):
    """
    Run the processing algorithm.
    Can be used without GUI widget.
    """

    # FIXME: update this...
    if not inputVolume or not outputVolume:
      raise ValueError("Input or output volume is invalid")

    logging.info('Processing started')
    import skfuzzy as fuzz

    # FIXME: why is this needed?
    #add a check for the image size and the mask size using resample brain volume module

    brainImageNode = slicer.util.getNode(inputVolume.GetID())
    brain_img = slicer.util.arrayFromVolume(brainImageNode)

    volumesLogic = slicer.modules.volumes.logic()
    mem0VolumeNode = volumesLogic.CloneVolume(slicer.mrmlScene, brainImageNode, "Membership 0")
    mem1VolumeNode = volumesLogic.CloneVolume(slicer.mrmlScene, brainImageNode, "Membership 1")

    brainMaskNode = slicer.util.getNode(outputVolume.GetID())
    brain_mask = slicer.util.arrayFromVolume(brainMaskNode)

    voxel_intensities = brain_img[brain_mask > 0]
    print(voxel_intensities)

    if nClass == 2:
        ncenters = 2
        cntr, u, u0, d, jm, p, fpc = fuzz.cluster.cmeans(voxel_intensities.reshape(1, voxel_intensities.size), ncenters, 2, error=0.005, maxiter=1000, init=None)

        membership0 = np.zeros(brain_img.shape)
        membership1 = np.zeros(brain_img.shape)

        membership0[brain_mask > 0] = u[0]
        membership1[brain_mask > 0] = u[1]

        slicer.util.updateVolumeFromArray(mem0VolumeNode, membership0)
        slicer.util.updateVolumeFromArray(mem1VolumeNode, membership1)

        # FIXME: update the levels automatically
        mem0VolumeNode.GetDisplayNode().SetWindowLevelMinMax(0, 1)
        mem1VolumeNode.GetDisplayNode().SetWindowLevelMinMax(0, 1)

    else:
        raise NotImplementedError("3 classes (parenchyma, ventricles and tumor) not implemented yet.")
        # FIXME: Do not write temporary files in source directory. Create nodes instead (see above).
        print("inside")
        node = slicer.util.getNode(tumourSeg.GetID())
        slicer.util.saveNode(node, dir_path+"/tumour.nrrd")
        back_mask, header1 = nrrd.read(dir_path+"/tumour.nrrd")

        #initialise tumour membership function
        back_membership = np.zeros(back_mask.shape)

        av,bv,cv = back_mask.shape

        for i in range (0, av):
            for j in range (0, bv):
                for k in range (0, cv):
                    if back_mask[i,j,k] > 0:
                        back_membership[i,j,k] = 1

        nrrd.write(dir_path+"/tumour_membership.nrrd", back_membership, header)
        #nrrd.write(tFile, back_membership, header)


        brain_img, header = nrrd.read(dir_path+"/brainVol.nrrd")
        brain_mask, header = nrrd.read(dir_path+"/brainMask.nrrd")
        print("inside2")
        ncenters = 5
        cntr, u, u0, d, jm, p, fpc = fuzz.cluster.cmeans(voxel_intensities.reshape(1, voxel_intensities.size), ncenters, 2, error = 0.005, maxiter = 1000, init = None)
        print("inside3")

        membership_1 = np.zeros(brain_img.shape)
        membership_1[brain_mask > 0] = u[0]

        membership_2 = np.zeros(brain_img.shape)
        membership_2[brain_mask > 0] = u[1]

        membership_3 = np.zeros(brain_img.shape)
        membership_3[brain_mask > 0] = u[2]

        membership_4 = np.zeros(brain_img.shape)
        membership_4[brain_mask > 0] = u[3]

        membership_5 = np.zeros(brain_img.shape)
        membership_5[brain_mask > 0] = u[4]

        nrrd.write(dir_path+"/membership_1.nrrd", membership_1, header)
        nrrd.write(dir_path+"/membership_2.nrrd", membership_2, header)
        nrrd.write(dir_path+"/membership_3.nrrd", membership_3, header)
        nrrd.write(dir_path+"/membership_4.nrrd", membership_4, header)
        nrrd.write(dir_path+"/membership_5.nrrd", membership_5, header)

        tumour_membership, header = nrrd.read(dir_path+"/tumour_membership.nrrd")

        membership_1, header = nrrd.read(dir_path+"/membership_1.nrrd")
        membership_2, header = nrrd.read(dir_path+"/membership_2.nrrd")
        membership_3, header = nrrd.read(dir_path+"/membership_3.nrrd")
        membership_4, header = nrrd.read(dir_path+"/membership_4.nrrd")
        membership_5, header = nrrd.read(dir_path+"/membership_5.nrrd")

        av,bv,cv = membership_1.shape
        for i in range (0, av):
            for j in range (0, bv):
                for k in range (0, cv):
                    if tumour_membership[i,j,k] >0:
                        membership_1[i,j,k] = 0
                        membership_2[i,j,k] = 0
                        membership_3[i,j,k] = 0
                        membership_4[i,j,k] = 0
                        membership_5[i,j,k] = 0

        nrrd.write(dir_path+"/membership_1.nrrd", membership_1, header)
        nrrd.write(dir_path+"/membership_2.nrrd", membership_2, header)
        nrrd.write(dir_path+"/membership_3.nrrd", membership_3, header)
        nrrd.write(dir_path+"/membership_4.nrrd", membership_4, header)
        nrrd.write(dir_path+"/membership_5.nrrd", membership_5, header)
        slicer.util.loadVolume(dir_path+"/tumour_membership.nrrd")
        slicer.util.loadVolume(dir_path+"/membership_1.nrrd")
        slicer.util.loadVolume(dir_path+"/membership_2.nrrd")
        slicer.util.loadVolume(dir_path+"/membership_3.nrrd")
        slicer.util.loadVolume(dir_path+"/membership_4.nrrd")
        slicer.util.loadVolume(dir_path+"/membership_5.nrrd")




    #slicer.util.loadVolume(vFile)
    #slicer.util.loadVolume(pFile)
    #dim = inputVolume.GetImageData().GetDimensions()
    #spacing = inputVolume.GetSpacing()
    #numOfSlices = [0,0,0]
    #for i in range(3):
    #  numOfSlices[i] = int(math.ceil(dim[i] / cutSpacing[i]))
    #print(numOfSlices)
    #outputNode = self.createEmptyVolume(dim, spacing, 'newVolume')
    #outputImageArray = slicer.util.arrayFromVolume(outputNode).copy()
    #volumeNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLScalarVolumeNode')
    #volumeNode = slicer.modules.volumes.logic().CloneVolume(mriImage, "Difference")
    #volumeNode.CreateDefaultDisplayNodes()
    #slicer.util.updateVolumeFromArray(outputNode, brain_ventricle_membership)
    #ijkToRAS = vtk.vtkMatrix4x4()
    #inputVolume.GetIJKToRASMatrix(ijkToRAS)
    #outputNode.SetIJKToRASMatrix(ijkToRAS)
    #outputVolume = self.performVesselness(inputVolume, brain_ventricle_membership,  [20,20,20], False)
    #slicer.util.updateVolumeFromArray(outputVolume, brain_ventricle_membership)
    #v = outputVolume
    #v.GetImageData().GetPointData().GetScalars().Modified()
    #v.Modified()

    #setSliceViewerLayers(background=volumeNode)
    logging.info('Processing completed')

#
# FuzzyClassificationTest
#

class FuzzyClassificationTest(ScriptedLoadableModuleTest):
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
    self.test_FuzzyClassification1()

  def test_FuzzyClassification1(self):
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

    logic = FuzzyClassificationLogic()

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
