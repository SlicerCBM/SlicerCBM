import os
import unittest
import logging
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin

import numpy as np
#
# SkullGenerator
#

class SkullGenerator(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "SkullGenerator"  # TODO: make this more human readable by adding spaces
    self.parent.categories = ["CBM.Biomechanical"]  # TODO: set categories (folders where the module shows up in the module selector)
    self.parent.dependencies = []  # TODO: add here list of module names that this module requires
    self.parent.contributors = ["Saima Safdar"]  # TODO: replace with "Firstname Lastname (Organization)"
    self.parent.helpText = """
It performs skull generation"""  # TODO: update with short description of the module
    self.parent.helpText += self.getDefaultModuleDocumentationLink()  # TODO: verify that the default URL is correct or change it to the actual documentation
    self.parent.acknowledgementText = """
"""  # TODO: replace with organization, grant and thanks.

#
# SkullGeneratorWidget
#

class SkullGeneratorWidget(ScriptedLoadableModuleWidget, VTKObservationMixin):
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
    uiWidget = slicer.util.loadUI(self.resourcePath('UI/SkullGenerator.ui'))
    self.layout.addWidget(uiWidget)
    self.ui = slicer.util.childWidgetVariables(uiWidget)

    # Set scene in MRML widgets. Make sure that in Qt designer
    # "mrmlSceneChanged(vtkMRMLScene*)" signal in is connected to each MRML widget's.
    # "setMRMLScene(vtkMRMLScene*)" slot.
    uiWidget.setMRMLScene(slicer.mrmlScene)

    # Create a new parameterNode (it stores user's node and parameter values choices in the scene)
    self.logic = SkullGeneratorLogic()
    self.ui.parameterNodeSelector.addAttribute("vtkMRMLScriptedModuleNode", "ModuleName", self.moduleName)
    self.setParameterNode(self.logic.getParameterNode())

    # Connections
    self.ui.parameterNodeSelector.connect('currentNodeChanged(vtkMRMLNode*)', self.setParameterNode)
    self.ui.skullModel.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
    self.ui.brainModel.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
    #button to combine skull and brain files and contact file    
    self.ui.comSkullBrainBtn.connect('clicked(bool)', self.onApplycomSkullBrainBtn)

    #self.ui.inputSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
    #self.ui.outputSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
    #self.ui.imageThresholdSliderWidget.connect("valueChanged(double)", self.updateParameterNodeFromGUI)
    #self.ui.invertOutputCheckBox.connect("toggled(bool)", self.updateParameterNodeFromGUI)

    self.ui.applyButton.connect('clicked(bool)', self.onApplyButton)
    #for deleting the skull elements
    self.ui.delSkullCells.connect('clicked(bool)', self.onPressDelSkullCells)
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

    wasBlocked = self.ui.skullModel.blockSignals(True)
    self.ui.skullModel.setCurrentNode(self._parameterNode.GetNodeReference("skullModel"))
    self.ui.skullModel.blockSignals(wasBlocked)
    
    wasBlocked = self.ui.brainModel.blockSignals(True)
    self.ui.brainModel.setCurrentNode(self._parameterNode.GetNodeReference("brainModel"))
    self.ui.brainModel.blockSignals(wasBlocked)
    """
    wasBlocked = self.ui.imageThresholdSliderWidget.blockSignals(True)
    self.ui.imageThresholdSliderWidget.value = float(self._parameterNode.GetParameter("Threshold"))
    self.ui.imageThresholdSliderWidget.blockSignals(wasBlocked)"""

    #wasBlocked = self.ui.invertOutputCheckBox.blockSignals(True)
    #self.ui.invertOutputCheckBox.checked = (self._parameterNode.GetParameter("Invert") == "true")
    #self.ui.invertOutputCheckBox.blockSignals(wasBlocked)
    
    wasBlocked = self.ui.tumorCheck.blockSignals(True)
    self.ui.tumorCheck.checked = (self._parameterNode.GetParameter("tumorCheck") == "true")
    self.ui.tumorCheck.blockSignals(wasBlocked)

    # Update buttons states and tooltips
    """if self._parameterNode.GetNodeReference("InputVolume") and self._parameterNode.GetNodeReference("OutputVolume"):
      self.ui.applyButton.toolTip = "Compute output volume"
      self.ui.applyButton.enabled = True
    else:
      self.ui.applyButton.toolTip = "Select input and output volume nodes"
      self.ui.applyButton.enabled = False"""

  def updateParameterNodeFromGUI(self, caller=None, event=None):
    """
    This method is called when the user makes changes in the GUI.
    The changes are saved into the parameter node (so that they are preserved when the scene is saved and loaded).
    """

    if self._parameterNode is None:
      return

    self._parameterNode.SetNodeReferenceID("skullModel", self.ui.skullModel.currentNodeID)
    self._parameterNode.SetNodeReferenceID("brainModel", self.ui.brainModel.currentNodeID)
    #self._parameterNode.SetParameter("Threshold", str(self.ui.imageThresholdSliderWidget.value))
    #self._parameterNode.SetParameter("Invert", "true" if self.ui.invertOutputCheckBox.checked else "false")
    self._parameterNode.SetParameter("tumorCheck", "true" if self.ui.tumorCheck.checked else "false")

  def onApplycomSkullBrainBtn(self):
    try:
      self.logic.comSkullBrainContact(self.ui.inputSkullFile.currentPath, self.ui.skullModel.currentNode(), self.ui.brainModel.currentNode(), self.ui.inputContactFile.currentPath, self.ui.fullModelFile.currentPath)
    except Exception as e:
      slicer.util.errorDisplay("Failed to compute results: "+str(e))
      import traceback
      traceback.print_exc()  
      
      
  def onApplyButton(self):
    """
    Run processing when user clicks "Apply" button.
    """
    try:
        import slicer.util
        import meshio
    except Exception as e1:
        slicer.util.pip_install('meshio')
        import meshio
        
    try:
      self.logic.run(self.ui.skullModel.currentNode(), self.ui.brainModel.currentNode(), self.ui.contactsFile.currentPath, self.ui.newSkullFile.currentPath, self.ui.tumorCheck.checked)
    except Exception as e:
      slicer.util.errorDisplay("Failed to compute results: "+str(e))
      import traceback
      traceback.print_exc()
      
  def onPressDelSkullCells(self):
    """Run this to delete the skull elements"""
    try:
      self.logic.deleteSkullCells(self.ui.cellFile.currentPath, self.ui.delSkullFile.currentPath, self.ui.skullModel.currentNode(), self.ui.brainModel.currentNode())
    except Exception as e:
      slicer.util.errorDisplay("Failed to compute results: "+str(e))
      import traceback
      traceback.print_exc()
      
       

#
# SkullGeneratorLogic
#

class SkullGeneratorLogic(ScriptedLoadableModuleLogic):
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
      
  def comSkullBrainContact(self, skullFile,skullNode, brainNode,contactFile, fullModelFile):
    logging.info('Processing started')
    print(skullFile)
    print(brainNode)
    dir_path = os.path.dirname(os.path.realpath(__file__))
    
    #reading the model from slicer and saving the model temporarily and reading it through meshio againa s inp file
    skullModel= slicer.util.getNode(skullNode.GetID())
    properties = {'useCompression': 0};
    slicer.util.saveNode(skullModel,dir_path+"/skullModel.vtk",properties)
    skullModel_file = meshio.read(dir_path+"/skullModel.vtk")
    
    
    #reading the brain model and then doing the ame as for the skull model
    brainModel= slicer.util.getNode(brainNode.GetID())
    properties = {'useCompression': 0};
    slicer.util.saveNode(brainModel,dir_path+"/brainModel.vtk",properties)
    brain_volume = meshio.read(dir_path+"/brainModel.vtk")
    
    brain_nodes = brain_volume.points
    brain_tetra = brain_volume.cells_dict["tetra"] 
    
    skull_nodes = skullModel_file.points
    #initialise_new_nodes for the new file of brain biomechanics the inp complete file
    final_nodes = np.vstack((brain_nodes,skull_nodes))
    final_nodes2 =  np.ndarray((final_nodes.shape[0],3), dtype=object)
    for idx, points in enumerate(final_nodes):
        a = np.array([points[0], points[1], points[2]])
        final_nodes2[idx,0] = a[0]/1000
        final_nodes2[idx,1] = a[1]/1000
        final_nodes2[idx,2] = a[2]/1000
        
    meshio.write_points_cells(fullModelFile, final_nodes2, [("tetra",brain_tetra)])
    
    #read the skull file that is generated
    skull_connectivity = open(skullFile,"r")
    content = skull_connectivity.read()
    
    contacts = open(contactFile,"r")
    contact = contacts.read()
    
    print(content)
    print(contact)
    # write in inp file the remaining things append witht eh skull and the contacts
    
    with open (fullModelFile,"a+") as braininp:
        braininp.write("*Element, type=S3, ELSET=skull")
        braininp.write("\n"+ content)
        braininp.write("*Nset, nset=contact")    
        braininp.write("\n" + contact)

      
      
      
  def deleteSkullCells(self,cellFile, newSkullFile , skullNode, brainNode):
    #run this to delete the cells on skull surface 
    print("ok")
    dir_path = os.path.dirname(os.path.realpath(__file__))
    #reading the model from slicer and saving the model temporarily and reading it through meshio againa s inp file
    skullModel= slicer.util.getNode(skullNode.GetID())
    properties = {'useCompression': 0};
    slicer.util.saveNode(skullModel,dir_path+"/skullModel.vtk",properties)
    skullModel_file = meshio.read(dir_path+"/skullModel.vtk")
    meshio.write(dir_path+"/skullModel.inp", skullModel_file)
    
    skull = meshio.read(dir_path+"/skullModel.inp")
    skull_nodes = skull.points
    skull_tris = skull.cells_dict["triangle"]
    
    print(skull_tris)
    #reading the cells to be deleted
    cell_File = np.loadtxt(cellFile, dtype=int)
    print(len(cell_File))
    #Deleting the skull cells
    for i in range (0,len(cell_File)):
        np.delete(skull_tris, cell_File[i], 0)
            
    meshio.write_points_cells(dir_path+"/skullModel.vtu",skull_nodes, [("triangle" ,skull_tris)])
    print(skull_tris)
      
  def run(self, skullNode, brainNode, contactsFile, newSkullFile, tumorCheck=False):
    """
    Run the processing algorithm.
    Can be used without GUI widget.
    """

    """if not inputVolume or not outputVolume:
      raise ValueError("Input or output volume is invalid")"""

    logging.info('Processing started')
    dir_path = os.path.dirname(os.path.realpath(__file__))
    
    
    print(tumorCheck)
    #reading the model from slicer and saving the model temporarily and reading it through meshio againa s inp file
    skullModel= slicer.util.getNode(skullNode.GetID())
    properties = {'useCompression': 0};
    slicer.util.saveNode(skullModel,dir_path+"/skullModel.vtk",properties)
    skullModel_file = meshio.read(dir_path+"/skullModel.vtk")
    meshio.write(dir_path+"/skullModel.inp", skullModel_file)
    
    #reading the brain model and then doing the ame as for the skull model
    brainModel= slicer.util.getNode(brainNode.GetID())
    properties = {'useCompression': 0};
    slicer.util.saveNode(brainModel,dir_path+"/brainModel.vtk",properties)
    brainModel_file = meshio.read(dir_path+"/brainModel.vtk")
    
    #nodes=brainModel_file.points
    #tetras=brainModel_file.cells_dict["tetra"]
    #meshio.write_points_cells("brainModel.inp",nodes,[("tetra",tetras)])
    meshio.write(dir_path+"/brainModel.inp", brainModel_file)
    
    # Compute the thresholded output volume using the Threshold Scalar Volume CLI module
    skull = meshio.read(dir_path+"/skullModel.inp")
    skull_nodes = skull.points
    skull_tris = skull.cells_dict["triangle"]
    
    brain_volume = meshio.read(dir_path+"/brainModel.inp")
    brain_nodes = brain_volume.points
    brain_tetra = brain_volume.cells_dict["tetra"] 
    
    #change normals from outwards to inwards
    skull_tris_reorder = np.zeros([skull_tris.shape[0],3], dtype = object)
    for i in range (0,skull_tris.shape[0]):
        skull_tris_reorder[i,0] = skull_tris[i,0]
        skull_tris_reorder[i,1] = skull_tris[i,2]
        skull_tris_reorder[i,2] = skull_tris[i,1]
    skull_tris = skull_tris_reorder
    
    #changing all nodes of skull and brain to mm dividing by thousand and combining all the skull and brain nodes as well final_nodes2 contain all nodes of skull +brain
    final_nodes = np.vstack((brain_nodes,skull_nodes))
    final_nodes2 =  np.ndarray((final_nodes.shape[0],3), dtype=object)
    for idx, points in enumerate(final_nodes):
        a = np.array([points[0], points[1], points[2]])
        final_nodes2[idx,0] = a[0]/1000
        final_nodes2[idx,1] = a[1]/1000
        final_nodes2[idx,2] = a[2]/1000     
    
    contacts=[]
    if tumorCheck=='False':        
        #get connectivity nget contacts
        for i in range (0,skull_tris.shape[0]):
            print(skull_tris[i,0])
            print(skull_tris[i,1])
            print(skull_tris[i,2])
            contacts.append(skull_tris[i,0])
            contacts.append(skull_tris[i,1])
            contacts.append(skull_tris[i,2])
    else:
        #there can be another method to it as well extract brain surface nad then choose those that exist in the normal whole skull which means taking an intersection
        for i in range (skull_nodes.shape[0]):
            a1 = skull_nodes[i,0]/1000
            a2 = skull_nodes[i,1]/1000
            a3 = skull_nodes[i,2]/1000
            for j in range (final_nodes2.shape[0]):
                b1 = final_nodes2[j,0]
                b2 = final_nodes2[j,1]
                b3 = final_nodes2[j,2]
                if a1 == b1 and a2 == b2 and a3 == b3:
                    contacts.append(j+1)
                    break
    contacts.sort() 
    
    
        
    print(contacts)
    np.savetxt(contactsFile+".txt",contacts,fmt = '%d', newline = '\n')
    #writing to file 8 in each line
    f = open(contactsFile,'w+')
    for i in range(len(contacts)):
     f.write(str(contacts[i]))
     f.write(",")
     if (i+1) % 8 == 0 and i < len(contacts):
         f.write("\n")
    
    f.close()  
     
    #changing skull triangle cell ids and make it start after the tetrahedrals for this adding the brain total element number +1 to each skull id number
    brain_volume_nodes_length = brain_nodes.shape[0]
    skull_tris2 = skull_tris + brain_volume_nodes_length + 1
    skull_tris_file = np.zeros([skull_tris2.shape[0],4],dtype = 'int')

    for i in range (0,skull_tris2.shape[0]):
        skull_tris_file[i,0] = i+1+brain_tetra.shape[0]
        skull_tris_file[i,1:] = skull_tris2[i]
    np.savetxt(newSkullFile,skull_tris_file,fmt = '%d, %d, %d, %d', newline = '\n')      
   


    
    
    logging.info('Processing completed')

#
# SkullGeneratorTest
#

class SkullGeneratorTest(ScriptedLoadableModuleTest):
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
    self.test_SkullGenerator1()

  def test_SkullGenerator1(self):
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

    logic = SkullGeneratorLogic()

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
