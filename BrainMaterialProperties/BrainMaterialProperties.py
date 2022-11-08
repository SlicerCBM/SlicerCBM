import os
import unittest
import logging
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin

#
# BrainMaterialProperties
#

class BrainMaterialProperties(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "BrainMaterialProperties"  # TODO: make this more human readable by adding spaces
    self.parent.categories = ["CBM.Biomechanical.Property"]  # TODO: set categories (folders where the module shows up in the module selector)
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
# BrainMaterialPropertiesWidget
#

class BrainMaterialPropertiesWidget(ScriptedLoadableModuleWidget, VTKObservationMixin):
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
    uiWidget = slicer.util.loadUI(self.resourcePath('UI/BrainMaterialProperties.ui'))
    self.layout.addWidget(uiWidget)
    self.ui = slicer.util.childWidgetVariables(uiWidget)

    # Set scene in MRML widgets. Make sure that in Qt designer
    # "mrmlSceneChanged(vtkMRMLScene*)" signal in is connected to each MRML widget's.
    # "setMRMLScene(vtkMRMLScene*)" slot.
    uiWidget.setMRMLScene(slicer.mrmlScene)

    # Create a new parameterNode (it stores user's node and parameter values choices in the scene)
    self.logic = BrainMaterialPropertiesLogic()
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
        import mvloader.nrrd as mvnrrd
        import nrrd
        import numpy as np     
    except ModuleNotFoundError as e:
        if slicer.util.confirmOkCancelDisplay("This module requires 'nrrd, skfuzzy' Python package. Click OK to install (it takes several minutes)."):
            slicer.util.pip_install("git+https://github.com/spezold/mvloader.git")
            slicer.util.pip_install("pynrrd")
            import nrrd
            import mvloader.nrrd as mvnrrd
    try:
      self.logic.run(self.ui.inputSelector.currentNode(), self.ui.outputSelector.currentNode(), self.ui.cNumber.value, self.ui.mat.currentText, self.ui.intFile.currentPath, self.ui.matFile.currentPath)
    except Exception as e:
      slicer.util.errorDisplay("Failed to compute results: "+str(e))
      import traceback
      traceback.print_exc()


#
# BrainMaterialPropertiesLogic
#

class BrainMaterialPropertiesLogic(ScriptedLoadableModuleLogic):
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

  def run(self, inputVolume, outputVolume, cNumber, mat, intFile, matFile):
    """
    Run the processing algorithm.
    Can be used without GUI widget.
    """

    if not inputVolume or not outputVolume:
      raise ValueError("Input or output volume is invalid")

    logging.info('Processing started')
    import mvloader.nrrd as mvnrrd
    import nrrd
    import numpy as np   
    print(mat)
    print(matFile)
    print(intFile)
    # Compute the thresholded output volume using the Threshold Scalar Volume CLI module
    """cliParams = {
      'InputVolume': inputVolume.GetID(),
      'OutputVolume': outputVolume.GetID(),
      'ThresholdValue' : imageThreshold,
      'ThresholdType' : 'Below' if invert else 'Above'
      }
    cliNode = slicer.cli.run(slicer.modules.thresholdscalarvolume, None, cliParams, wait_for_completion=True)"""
    dir_path = os.path.dirname(os.path.realpath(__file__))
    node = slicer.util.getNode(inputVolume.GetID())
    slicer.util.saveNode(node, dir_path+"/mem1.nrrd")
    
    node = slicer.util.getNode(outputVolume.GetID())
    slicer.util.saveNode(node, dir_path+"/tumour.nrrd")
    
    cNumber = int(cNumber)
    if mat=="Neo-Hookean" and cNumber==2:
        print("neo")
        
        #brain_ventricle_membership, header = nrrd.read(dir_path+"/mem1.nrrd")
    
        brain_ventricle_membership_volume = mvnrrd.open_image(dir_path+"/mem1.nrrd")
    
        brain_ventricle_membership = brain_ventricle_membership_volume.src_data
        # Create transform from world coordinates to voxel indeces
        voxels2world = brain_ventricle_membership_volume.src_transformation
        world2voxels = np.linalg.inv(voxels2world)
    
        homogeneous = lambda c3d: np.r_[c3d, 1]  # append 1 to 3D coordinate
    
        # Define material properties for each tissue
        YM_parenchima = 3000
        YM_ventricles = 100 
    
        PR_V = 0.10
        PR_B = 0.49
        density = 1000 
        
        
        import pandas as pd
        # Read integration points
        ips = np.genfromtxt(intFile, delimiter=',')
        num_ips = ips.shape[0]
        # Create material properties for each ip
        material_props = np.zeros([num_ips, 3])
        material_props[:,0] = density
       
        for idx, ip in enumerate(ips):
            x = np.array([-1000*ip[0], -1000*ip[1], 1000*ip[2]])
            voxel_idxs = world2voxels[:3] @ homogeneous(x)
            iv, jv, kv = voxel_idxs.astype(np.int)
            for i in range(iv-1, iv+1):
                for j in range(jv-1, jv+1):
                    for k in range(kv-1, kv+1):
                        material_props[idx, 1] += YM_parenchima *(1-brain_ventricle_membership[i, j, k])+YM_ventricles * brain_ventricle_membership[i, j, k]             
                        material_props[idx, 2] += PR_B * (1-brain_ventricle_membership[i, j, k])+PR_V * brain_ventricle_membership[i, j, k]
             
            
            material_props[idx, 1]/= 8
            material_props[idx, 2]/= 8
            if material_props[idx, 1] == 0:
                print("YM is 0 for ip %d" % idx)
             
        np.savetxt(matFile, material_props, fmt = "%.8f, %.8f, %.8f", newline='\n')
    elif mat=="Neo-Hookean" and cNumber==3:
        print("neo 3")
        #brain_ventricle_membership, header = nrrd.read(dir_path+"/mem1.nrrd")
        tumour_membership, header = nrrd.read(dir_path+"/tumour.nrrd")

        brain_ventricle_membership_volume = mvnrrd.open_image(dir_path+"/mem1.nrrd")
    
        brain_ventricle_membership = brain_ventricle_membership_volume.src_data
        # Create transform from world coordinates to voxel indeces
        voxels2world = brain_ventricle_membership_volume.src_transformation
        world2voxels = np.linalg.inv(voxels2world)
    
        homogeneous = lambda c3d: np.r_[c3d, 1]  # append 1 to 3D coordinate
    
        # Define material properties for each tissue
        YM_parenchima = 3000
        YM_ventricles = 100 
        YM_tumour = 9000
    
        PR_V = 0.10
        PR_B = 0.49
        PR_T = 0.49
        density = 1000 
        
        
        import pandas as pd
        # Read integration points
        ips = np.genfromtxt(intFile, delimiter=',')
        num_ips = ips.shape[0]
        # Create material properties for each ip
        material_props = np.zeros([num_ips, 3])
        material_props[:,0] = density
       
        for idx, ip in enumerate(ips):
            x = np.array([-1000*ip[0], -1000*ip[1], 1000*ip[2]])
            voxel_idxs = world2voxels[:3] @ homogeneous(x)
            iv, jv, kv = voxel_idxs.astype(np.int)
            for i in range(iv-1, iv+1):
                for j in range(jv-1, jv+1):
                    for k in range(kv-1, kv+1):
                        material_props[idx, 1] += YM_parenchima *(1-brain_ventricle_membership[i, j, k]-tumour_membership[i,j,k]) + YM_tumour * tumour_membership[i,j,k] + YM_ventricles * brain_ventricle_membership[i, j, k]             
                        material_props[idx, 2] += PR_B * (1-brain_ventricle_membership[i, j, k]-tumour_membership[i,j,k])+ PR_T * tumour_membership[i,j,k] + PR_V * brain_ventricle_membership[i, j, k]
             
            
            material_props[idx, 1]/= 8
            material_props[idx, 2]/= 8
            if material_props[idx, 1] == 0:
                print("YM is 0 for ip %d" % idx)
             
        np.savetxt(matFile, material_props, fmt = "%.8f, %.8f, %.8f", newline='\n')
    else:
        print("ogden")
        ventricle_membership_volume = mvnrrd.open_image(dir_path+"/mem1.nrrd")
        ventricle_membership = ventricle_membership_volume.src_data
        tumour_membership, header = nrrd.read(dir_path+"/tumour.nrrd")
        
        voxels2world = ventricle_membership_volume.src_transformation
        world2voxels = np.linalg.inv(voxels2world)
        
        homogeneous = lambda c3d: np.r_[c3d, 1]
        
        parenchyma_SM = 842
        tumour_SM = 842*3
        CSF_SM = 4.54
        
        D_parenchima = 4.78e-05
        D_tumour = 1.59e-5
        #D_ventricle = 0.48058
        #D_ventricle = 0.008869704047541623
        D_ventricle = 0.008
        
        
        parenchyma_alpha = -4.7
        tumour_alpha = -4.7
        CSF_alpha = 2
        
        density = 1000
        
        #read integration points
        ips = np.genfromtxt(intFile, delimiter = ',')
        num_ips = ips.shape[0]
        
        material_props = np.zeros([num_ips, 4])
        material_props[:,0] = density
        
        for idx, ip in enumerate(ips):
            x = np.array([-1000*ip[0], -1000*ip[1], 1000*ip[2]])
            voxel_idxs = world2voxels[:3] @ homogeneous(x)
            iv, jv, kv = voxel_idxs.astype(np.int)
            for i in range(iv-1, iv+1):
                for j in range(jv-1, jv+1):
                    for k in range(kv-1, kv+1):
                        #for shear modulus 
                        if ventricle_membership[i,j,k] < 0.1:
                            ventricle_membership[i,j,k] = 0
                            
                        if  tumour_membership[i,j,k] != 0 or ventricle_membership[i,j,k] != 0:
                            
                            material_props[idx, 1] += parenchyma_SM * (1-tumour_membership[i,j,k]-ventricle_membership[i,j,k] ) + tumour_SM * tumour_membership[i,j,k] + CSF_SM * ventricle_membership[i,j,k] 
                            material_props[idx, 2] += parenchyma_alpha * (1-tumour_membership[i,j,k]-ventricle_membership[i,j,k] ) + tumour_alpha * tumour_membership[i,j,k] + CSF_alpha * ventricle_membership[i,j,k]
                            material_props[idx, 3] += D_parenchima * (1-tumour_membership[i,j,k]-ventricle_membership[i,j,k] ) + D_tumour * tumour_membership[i,j,k] + D_ventricle * ventricle_membership[i,j,k]
                        
                        if tumour_membership[i,j,k] == 0 and ventricle_membership[i,j,k] == 0:
                            
                            material_props[idx, 1] += parenchyma_SM * 1                             
                            material_props[idx, 2] += parenchyma_alpha * 1
                            material_props[idx, 3] += D_parenchima * 1
                            
                            
                            
            material_props[idx, 1] /= 8                
            material_props[idx, 2] /= 8                   
            material_props[idx, 3] /= 8   
            
            if material_props[idx, 1] == 0:
                print("SM is 0 for ip %d" % idx)
            if material_props[idx, 2] == 0:
                print("A is 0 for ip %d" % idx)
            if material_props[idx, 3] == 0:
                print("D is 0 for ip %d" % idx)
        
        
                         
                        
        # Save material properties
        np.savetxt(matFile, material_props, fmt = "%.1f, %.8f, %.8f, %.8f", newline='\n')               
                

    logging.info('Processing completed')

#
# BrainMaterialPropertiesTest
#

class BrainMaterialPropertiesTest(ScriptedLoadableModuleTest):
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
    self.test_BrainMaterialProperties1()

  def test_BrainMaterialProperties1(self):
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

    logic = BrainMaterialPropertiesLogic()

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
