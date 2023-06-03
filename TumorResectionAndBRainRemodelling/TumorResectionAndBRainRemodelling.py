import os
import unittest
import logging
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin
import numpy as np
#import mvloader.nrrd as mvnrrd
#import nrrd
#import meshio

#
# TumorResectionAndBRainRemodelling
#

class TumorResectionAndBRainRemodelling(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "Tumor Resection and Brain Remodeling"
    self.parent.categories = ["CBM.Biomechanical"]
    self.parent.dependencies = []  # TODO: add here list of module names that this module requires
    self.parent.contributors = ["Saima Safdar"]  # TODO: replace with "Firstname Lastname (Organization)"
    self.parent.helpText = """
This is an example of scripted loadable module bundled in an extension.
It resects the tumour based on the provided mask and generates a tetrahedral brain model without tumour.
"""  # TODO: update with short description of the module
    self.parent.helpText += self.getDefaultModuleDocumentationLink()  # TODO: verify that the default URL is correct or change it to the actual documentation
    self.parent.acknowledgementText = """

"""  # TODO: replace with organization, grant and thanks.

#
# TumorResectionAndBRainRemodellingWidget
#

class TumorResectionAndBRainRemodellingWidget(ScriptedLoadableModuleWidget, VTKObservationMixin):
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
    uiWidget = slicer.util.loadUI(self.resourcePath('UI/TumorResectionAndBRainRemodelling.ui'))
    self.layout.addWidget(uiWidget)
    self.ui = slicer.util.childWidgetVariables(uiWidget)

    # Set scene in MRML widgets. Make sure that in Qt designer
    # "mrmlSceneChanged(vtkMRMLScene*)" signal in is connected to each MRML widget's.
    # "setMRMLScene(vtkMRMLScene*)" slot.
    uiWidget.setMRMLScene(slicer.mrmlScene)

    # Create a new parameterNode (it stores user's node and parameter values choices in the scene)
    self.logic = TumorResectionAndBRainRemodellingLogic()
    self.ui.parameterNodeSelector.addAttribute("vtkMRMLScriptedModuleNode", "ModuleName", self.moduleName)
    self.setParameterNode(self.logic.getParameterNode())

    # Connections
    self.ui.parameterNodeSelector.connect('currentNodeChanged(vtkMRMLNode*)', self.setParameterNode)

    self.ui.tumorMask.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
    self.ui.brainModel.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)


    self.ui.rBrainModel.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
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
    self.ui.outputs.enabled = self._parameterNode is not None
    if self._parameterNode is None:
      return

    # Update each widget from parameter node

    wasBlocked = self.ui.tumorMask.blockSignals(True)
    self.ui.tumorMask.setCurrentNode(self._parameterNode.GetNodeReference("InputVolume"))
    self.ui.tumorMask.blockSignals(wasBlocked)

    wasBlocked = self.ui.brainModel.blockSignals(True)
    self.ui.brainModel.setCurrentNode(self._parameterNode.GetNodeReference("OutputVolume"))
    self.ui.brainModel.blockSignals(wasBlocked)

    wasBlocked = self.ui.rBrainModel.blockSignals(True)
    self.ui.rBrainModel.setCurrentNode(self._parameterNode.GetNodeReference("rOutputVolume"))
    self.ui.rBrainModel.blockSignals(wasBlocked)

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

    self._parameterNode.SetNodeReferenceID("InputVolume", self.ui.tumorMask.currentNodeID)
    self._parameterNode.SetNodeReferenceID("OutputVolume", self.ui.brainModel.currentNodeID)
    self._parameterNode.SetNodeReferenceID("rOutputVolume", self.ui.rBrainModel.currentNodeID)



  def onApplyButton(self):
    """
    Run processing when user clicks "Apply" button.
    """
    try:
        import mvloader.nrrd as mvnrrd
        import nrrd
        import numpy as np
        import meshio
    except ModuleNotFoundError as e:
        if slicer.util.confirmOkCancelDisplay("This module requires 'nrrd, mvloader, meshio' Python package. Click OK to install."):
            slicer.util.pip_install("git+https://github.com/spezold/mvloader.git")
            slicer.util.pip_install("pynrrd")
            slicer.util.pip_install("meshio")
            import nrrd
            import mvloader.nrrd as mvnrrd
            import meshio


    try:
      self.logic.run(self.ui.tumorMask.currentNode(), self.ui.brainModel.currentNode(),self.ui.rBrainModel.currentNode(), self.ui.iNodesBefore.currentPath, self.ui.iNodesAfter.currentPath)
    except Exception as e:
      slicer.util.errorDisplay("Failed to compute results: "+str(e))
      import traceback
      traceback.print_exc()


#
# TumorResectionAndBRainRemodellingLogic
#

class TumorResectionAndBRainRemodellingLogic(ScriptedLoadableModuleLogic):
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

  def run(self, tumorMask, brainModel, rBrainModel, iNodesBeforeFile, iNodesAfterFile):
    """
    Run the processing algorithm.
    Can be used without GUI widget.
    """

    if not tumorMask or not brainModel:
      raise ValueError("tumormask or brain model is invalid")

    logging.info('Processing started')

    # Compute the thresholded output volume using the Threshold Scalar Volume CLI module
    dir_path = os.path.dirname(os.path.realpath(__file__))
    print(dir_path)
    node = slicer.util.getNode(tumorMask.GetID())
    slicer.util.saveNode(node,dir_path+"/tumour.seg.nrrd")

    tumour_mask = mvnrrd.open_image(dir_path+"/tumour.seg.nrrd")
    tumour_voxel, header = nrrd.read(dir_path+"/tumour.seg.nrrd")
    voxels2world = tumour_mask.src_transformation
    world2voxels = np.linalg.inv(voxels2world)

    homogeneous = lambda c3d: np.r_[c3d, 1]

    #read brain node
    brainModel = slicer.util.getNode(brainModel.GetID())
    slicer.util.saveNode(brainModel,dir_path+"/brainModel.vtk")
    brainModel_1 = meshio.read(dir_path+"/brainModel.vtk")
    brain_nodes = brainModel_1.points
    brain_tetra = brainModel_1.cells_dict["tetra"]
    brain_nodes = brainModel_1.points
    tetras = tris = brainModel_1.cells_dict["tetra"]

    print("-------------------------read brain mesh done!--------------------------------")

    brain_nodes_new  = np.zeros([brain_nodes.shape[0],4])
    brain_tetras_new = np.zeros([tetras.shape[0],5])

    #create brain_nodes with id

    for i in range (0,brain_nodes.shape[0]):
        brain_nodes_new[i,0] = int(i+1)
        brain_nodes_new[i,1:] = brain_nodes[i]

    #create brain_tetras with id

    for ii in range (0,tetras.shape[0]):
        brain_tetras_new[ii,0] = int(ii+1)
        brain_tetras_new[ii,1:] = tetras[ii]+1

    #initialise tumour nodes

    print("---------------------Initialise tumour nodes!----------------------------------")
    tumour_nodes = []
    #tumour nodes collection

    for idx, pts in enumerate (brain_nodes_new):
        x  = np.array([pts[1], pts[2], pts[3]])
        voxel_idxs = world2voxels[:3] @homogeneous(x)
        iv, jv, kv = voxel_idxs.astype(np.int)
        if tumour_voxel[iv, jv, kv] != 0:
            tumour_nodes.append(pts)


    tumour_nodes = np.array(tumour_nodes)

    print("---------------------------tumour nodes collection done--------------------------")

    #generate tumour_nodes_id-----can be used in abaqus inp file

    tumour_idx = tumour_nodes[:,0]

    with open(dir_path+"/tumour_idx.txt","w") as f:
        for t_idx in range (0,tumour_idx.shape[0]):
            if (t_idx+1)%16 == 0:
                s = int(tumour_idx[t_idx])
                f.write("%d\n" %s)
            else:
                s = int(tumour_idx[t_idx])
                f.write("%d," %s)

    print("tumour_idx.txt saved, there are",tumour_idx.shape[0],"tumour nodes")
    print("--------------------------start tumour element id--------------------------------------")
    #generate tumour_ele_id-----can be used in abaqus inp file
    #Initialise tumour_element id
    tumour_ele_idx = []
    non_tumour_element_idx = brain_tetras_new[:,0]
    new_non_tumour_element_idx = []

    #for item in non_tumour_element_idx:
        #new_non_tumour_element_idx.append(int(item))

    #new_non_tumour_element_idx = np.array(new_non_tumour_element_idx)
    #non_tumour_element_idx = new_non_tumour_element_idx
    for idx, pts in enumerate (tumour_idx):
        if idx%50 == 0:
            print("tumour_idx comes to",idx,"/",tumour_idx.shape[0],".")
        t_idx = int(pts)
        for i in range (0,brain_tetras_new.shape[0]):
            tetra_id = int(brain_tetras_new[i,0])
            tetra_1 = int(brain_tetras_new[i,1])
            tetra_2 = int(brain_tetras_new[i,2])
            tetra_3 = int(brain_tetras_new[i,3])
            tetra_4 = int(brain_tetras_new[i,4])
            if t_idx == tetra_1 or t_idx == tetra_2 or t_idx == tetra_3 or t_idx == tetra_4:
                tumour_ele_idx.append(tetra_id)

    tumour_ele_idx = list(dict.fromkeys(tumour_ele_idx))


    for item in non_tumour_element_idx:
        if item not in tumour_ele_idx:
            new_non_tumour_element_idx.append(item)

    tumour_ele_idx=np.array(tumour_ele_idx)
    new_non_tumour_element_idx= np.array(new_non_tumour_element_idx)

    print("----------------------------tumour_ele_idx obtained--------------------------------")

    with open(dir_path+"/tumour_ele_idx.txt","w") as f:
        for t_idx in range (0,tumour_ele_idx.shape[0]):
            if (t_idx+1)%16 == 0:
                s = int(tumour_ele_idx[t_idx])
                f.write("%d\n" %s)
            else:
                s = int(tumour_ele_idx[t_idx])
                f.write("%d," %s)

    print("------------------------------tumour_ele_idx.txt saved-----------------------------------")
    print("there are",tumour_ele_idx.shape[0],"tumour elements")
    ####check sharing nodes
    print("-------------------------------sharing_nodes_id start------------------------------------")
    sharing_nodes_id=[]

    for i in range (0,tumour_ele_idx.shape[0]):
        if i%50 == 0:
            print("tumour_ele_idx comes to",i,"/",tumour_ele_idx.shape[0],".")
        tum_ele_id = tumour_ele_idx[i]
        tum_tetra_nodes_id = brain_tetras_new[tum_ele_id-1]
        tri_1 = int(tum_tetra_nodes_id[1])
        tri_2 = int(tum_tetra_nodes_id[2])
        tri_3 = int(tum_tetra_nodes_id[3])
        tri_4 = int(tum_tetra_nodes_id[4])
        for ii in range (0,new_non_tumour_element_idx.shape[0]):
            #if ii%1000 == 0:
                #print("new_non_tumour_element_idx comes to",ii,"/",new_non_tumour_element_idx.shape[0],".")
            non_tum_ele_id = new_non_tumour_element_idx[ii]
            non_tum_tetra_nodes_id = brain_tetras_new[int(non_tum_ele_id-1)]
            non_tri_1 = int(non_tum_tetra_nodes_id[1])
            non_tri_2 = int(non_tum_tetra_nodes_id[2])
            non_tri_3 = int(non_tum_tetra_nodes_id[3])
            non_tri_4 = int(non_tum_tetra_nodes_id[4])
            if tri_1 == non_tri_1 or tri_1 == non_tri_2 or tri_1 == non_tri_3 or tri_1 == non_tri_4:
                sharing_nodes_id.append(tri_1)
            elif tri_2 == non_tri_1 or tri_2 == non_tri_2 or tri_2 == non_tri_3 or tri_2 == non_tri_4:
                sharing_nodes_id.append(tri_2)
            elif tri_3 == non_tri_1 or tri_3 == non_tri_2 or tri_3 == non_tri_3 or tri_3 == non_tri_4:
                sharing_nodes_id.append(tri_3)
            elif tri_4 == non_tri_1 or tri_4 == non_tri_2 or tri_4 == non_tri_3 or tri_4 == non_tri_4:
                sharing_nodes_id.append(tri_4)

    print("sharing nodes collection done")
    sharing_nodes_id = list(dict.fromkeys(sharing_nodes_id))
    sharing_nodes_id = np.array(sharing_nodes_id)
    with open(iNodesBeforeFile,"w") as f:
        for t_idx in range (0,sharing_nodes_id.shape[0]):
            if (t_idx+1)%16 == 0:
                s = int(sharing_nodes_id[t_idx])
                f.write("%d\n" %s)
            else:
                s = int(sharing_nodes_id[t_idx])
                f.write("%d," %s)

    #get sharing nodes coordinate

    sharing_nodes_coordinate = np.zeros([sharing_nodes_id.shape[0],4])

    for i in range (0,sharing_nodes_id.shape[0]):
        sharing_nodes_coordinate[i,0] = sharing_nodes_id[i]
        sharing_nodes_coordinate[i,1:] = brain_nodes[int(sharing_nodes_coordinate[i,0]-1)]

    np.savetxt(dir_path+'/***sharing_nodes_coordinate***.txt',sharing_nodes_coordinate, fmt = "%d, %.8f, %.8f, %.8f",
               newline = '\n')
    print("sharing nodes txt saved")

    #reconstructing brain model file
    #brainmesh = meshio.read("brain_model/brainmask_auto.inp")
    brainmesh = meshio.read(dir_path+"/brainModel.vtk")
    brain_nodes = brainmesh.points
    tetras = brainmesh.cells_dict["tetra"]


    brain_nodes_new1  = np.zeros([brain_nodes.shape[0],4])
    brain_tetras_new1 = np.zeros([tetras.shape[0],5])

    #create brain_nodes with id

    for i in range (0,brain_nodes.shape[0]):
        brain_nodes_new1[i,0] = int(i+1)
        brain_nodes_new1[i,1:] = brain_nodes[i]

    #create brain_tetras with id

    for ii in range (0,tetras.shape[0]):
        brain_tetras_new1[ii,0] = int(ii+1)
        brain_tetras_new1[ii,1:] = tetras[ii]+1


    #extract tumour_id

    tumour_idx_file = open(dir_path+"/tumour_idx.txt","r")
    data = tumour_idx_file.read().replace("\n", ",")
    data = list(data.split(","))
    data.remove('')
    tumour_idx_file.close()
    tumour_id = np.array(data)

    #extract tumour element id

    tumour_ele_idx_file = open(dir_path+"/tumour_ele_idx.txt","r")
    data2 = tumour_ele_idx_file.read().replace("\n",",")
    data2 = list(data2.split(","))
    data2.remove('')
    tumour_ele_idx_file.close()
    tumour_ele_idx = np.array(data2)


    #get tumour ele nodes info
    tumour_ele_nodes = np.zeros([tumour_ele_idx.shape[0],5])
    for i in range (0,tumour_ele_idx.shape[0]):
        tumour_ele_nodes[i,0] = tumour_ele_idx[i]
        tumour_ele_nodes[i] = brain_tetras_new1[int(tumour_ele_nodes[i,0]-1)]
    tumour_ele_nodes2  = []
    tumour_ele_nodes_number = tumour_ele_nodes[:,1:]
    for i in range (0,tumour_ele_nodes_number.shape[0]):
        tumour_ele_nodes2.append(tumour_ele_nodes_number[i,0])
        tumour_ele_nodes2.append(tumour_ele_nodes_number[i,1])
        tumour_ele_nodes2.append(tumour_ele_nodes_number[i,2])
        tumour_ele_nodes2.append(tumour_ele_nodes_number[i,3])

    tumour_ele_nodes2 = list(dict.fromkeys(tumour_ele_nodes2))

    #extract sharing nodes coordinate
    #node id   x   y   z
    sharing_nodes_coordinate = np.genfromtxt(dir_path+"/***sharing_nodes_coordinate***.txt",delimiter = ',')
    sharing_nodes_id = []
    for i in range (0,sharing_nodes_coordinate.shape[0]):
        sharing_nodes_id.append(sharing_nodes_coordinate[i,0])
    t = []
    for item in tumour_ele_nodes2:
        if item not in sharing_nodes_id:
            t.append(item)

    final_tumour_nodes_id = np.array(t)
    # tumour nodes coordinate
    tumour_nodes_coordinate = np.zeros([final_tumour_nodes_id.shape[0],4])
    for i in range (0,final_tumour_nodes_id.shape[0]):
        tumour_nodes_coordinate[i,0] = int(final_tumour_nodes_id[i])
        tumour_nodes_coordinate[i,1:] = brain_nodes[int(tumour_nodes_coordinate[i,0] -1)]

    # tumour element info
    tumour_element = np.zeros([tumour_ele_idx.shape[0],5])
    for i in range (0,tumour_ele_idx.shape[0]):
        tumour_element[i,0] = int(tumour_ele_idx[i])
        tumour_element[i] = brain_tetras_new1[int(tumour_element[i,0]-1)]





    #create new nodes id

    brain_nodes_reconstructed = np.zeros([brain_nodes_new1.shape[0]-tumour_nodes_coordinate.shape[0],4])
    brain_tetras_reconstructed = np.zeros([brain_tetras_new1.shape[0]-tumour_element.shape[0],5], dtype = int)
    bnr_i = 0
    for i in range (0,brain_nodes.shape[0]):
        brain_nodes_id = brain_nodes_new1[i,0]
        if brain_nodes_id not in tumour_nodes_coordinate[:,0]:
            brain_nodes_reconstructed[bnr_i] = brain_nodes_new1[i]
            bnr_i = bnr_i+1

    btr_i = 0
    for i in range (0,brain_tetras_new1.shape[0]):
        brain_tetra_id = brain_tetras_new1[i,0]
        if brain_tetra_id not in tumour_element[:,0]:
            brain_tetras_reconstructed[btr_i] = brain_tetras_new1[i]
            btr_i = btr_i+1

    #create stl/inp file
    re_brain_nodes = brain_nodes_reconstructed[:,1:]
    #re_tetras = brain_tetras_reconstructed[:,1:]-1



    brain_nodes_no_tumour = np.zeros([re_brain_nodes.shape[0],4])
    brain_tetra_no_tumour = np.zeros([brain_tetras_reconstructed.shape[0],5], dtype = int)

    for i in range (0,re_brain_nodes.shape[0]):
        brain_nodes_no_tumour[i,0] = int(i+1)
        brain_nodes_no_tumour[i,1:] = re_brain_nodes[i]


    brain_nodes_pair = np.zeros([brain_nodes_new1.shape[0],2])
    for i in range (0,brain_nodes_new1.shape[0]):
        brain_nodes_pair[i,0] = i+1
        nodes_new = brain_nodes_new1[i,1:]
        if nodes_new in re_brain_nodes:
            nodes_new_id = np.where(re_brain_nodes == nodes_new)
            brain_nodes_pair[i,1] = nodes_new_id[0][0] +1
        else:
            brain_nodes_pair[i,1] = 0


    brain_tetras_reconstructed_no_idx  = brain_tetras_reconstructed[:,1:]
    for i in range (0,brain_tetras_reconstructed.shape[0]):
        brain_tetra_no_tumour[i,0] = i+1
        t1 = int(brain_nodes_pair[brain_tetras_reconstructed_no_idx[i,0]-1,1])
        t2 = int(brain_nodes_pair[brain_tetras_reconstructed_no_idx[i,1]-1,1])
        t3 = int(brain_nodes_pair[brain_tetras_reconstructed_no_idx[i,2]-1,1])
        t4 = int(brain_nodes_pair[brain_tetras_reconstructed_no_idx[i,3]-1,1])
        brain_tetra_no_tumour[i,1:] = [t1,t2,t3,t4]



    np.savetxt(dir_path+'/brain_tetra_new_re1.txt',brain_tetra_no_tumour, fmt="%d, %d, %d, %d, %d",
               newline = '\n')

    np.savetxt(dir_path+"/brain_nodes_new1_re1.txt",brain_nodes_no_tumour,fmt = "%d, %.8f, %.8f, %.8f",
               newline = '\n')

    re_brain_nodes = re_brain_nodes
    re_tetras2 = brain_tetra_no_tumour[:,1:]-1

    meshio.write_points_cells(dir_path+"/re_brain1.vtu", re_brain_nodes, [("tetra",re_tetras2)])
    rBrainModel = slicer.util.loadModel(dir_path+"/re_brain1.vtu")

    sharing_nodes_coordinate
    sharing_nodes_coordinate_re = np.zeros([sharing_nodes_coordinate.shape[0],5])
    #node id, x, y, z, cooresponding_node_id in previous model
    for i in range (0,sharing_nodes_coordinate.shape[0]):
        sharing_nodes_coordinate_re[i,4]=int(sharing_nodes_coordinate[i,0])
        coord = sharing_nodes_coordinate[i,1:4]
        sharing_nodes_coordinate_re[i,1:4] = coord
        for j in range (0,brain_nodes_reconstructed.shape[0]):
            coord2 = brain_nodes_reconstructed[j,1:]
            if all(np.round(coord,8) == np.round(coord2,8)):
                sharing_nodes_coordinate_re[i,0]=int(j+1)
                break
    np.savetxt(iNodesAfterFile,sharing_nodes_coordinate_re,fmt = "%d, %.8f, %.8f, %.8f, %d",
               newline = '\n')


    logging.info('Processing completed')

#
# TumorResectionAndBRainRemodellingTest
#

class TumorResectionAndBRainRemodellingTest(ScriptedLoadableModuleTest):
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
    self.test_TumorResectionAndBRainRemodelling1()

  def test_TumorResectionAndBRainRemodelling1(self):
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

    logic = TumorResectionAndBRainRemodellingLogic()

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
