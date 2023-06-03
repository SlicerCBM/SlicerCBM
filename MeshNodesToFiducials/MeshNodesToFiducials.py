import os
import unittest
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging
#
# MeshNodesToFiducials
#

class MeshNodesToFiducials(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "MeshNodesToFiducials" # TODO make this more human readable by adding spaces
    self.parent.categories = ["CBM.Biomechanical.BrainNodeSelector"]
    self.parent.dependencies = []
    self.parent.contributors = ["Saima Safdar"] # replace with "Firstname Lastname (Organization)"
    self.parent.helpText = """
It has multiple parts each performing a seperate task.
"""
    self.parent.helpText += self.getDefaultModuleDocumentationLink()
    self.parent.acknowledgementText = """
""" # replace with organization, grant and thanks.

#
# MeshNodesToFiducialsWidget
#

class MeshNodesToFiducialsWidget(ScriptedLoadableModuleWidget):
  """Uses ScriptedLoadableModuleWidget base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setup(self):
    ScriptedLoadableModuleWidget.setup(self)



    # Load widget from .ui file (created by Qt Designer)
    uiWidget = slicer.util.loadUI(self.resourcePath('UI/MeshNodesToFiducials.ui'))
    self.layout.addWidget(uiWidget)
    self.ui = slicer.util.childWidgetVariables(uiWidget)


    self.ui.sMeshButton.connect('clicked(bool)', self.onSMeshButton)
    self.ui.vMeshButton.connect('clicked(bool)',self.onVMeshButton)
    self.ui.surfaceMesh.setMRMLScene(slicer.mrmlScene)


    self.ui.inputSelector.setMRMLScene(slicer.mrmlScene)
    self.ui.outputSelector.setMRMLScene(slicer.mrmlScene)
    self.ui.modelNode.setMRMLScene(slicer.mrmlScene)

    self.ui.fVolume.setMRMLScene(slicer.mrmlScene)
    self.ui.mVolume.setMRMLScene(slicer.mrmlScene)
    self.ui.transformNode.setMRMLScene(slicer.mrmlScene)
    self.ui.oVolume.setMRMLScene(slicer.mrmlScene)

    self.ui.fiducialToTrans.setMRMLScene(slicer.mrmlScene)
    self.ui.transformNode_2.setMRMLScene(slicer.mrmlScene)

    #for extract deformation field and apply on model
    self.ui.dModel.setMRMLScene(slicer.mrmlScene)
    self.ui.dModel.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelectDeformationModel)
    self.ui.warpModelButton.connect('clicked(bool)', self.onApplyWarpModelButton)

    # connections
    self.ui.applyButton.connect('clicked(bool)', self.onApplyButton)
    self.ui.pushButton.connect('clicked(bool)', self.onCelltoFiducialButton)
    self.ui.loadCreation.connect('clicked(bool)', self.onloadCreationButton)
    self.ui.transformFid.connect('clicked(bool)', self.ontransformFidButton)

    self.ui.fNode.setMRMLScene(slicer.mrmlScene)
    self.ui.tfNode.setMRMLScene(slicer.mrmlScene)

    self.ui.inputSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)
    self.ui.outputSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)
    #Create deformed and uundeformed model input points files for scattered transform
    self.ui.uModel.setMRMLScene(slicer.mrmlScene)
    self.ui.deformModel.setMRMLScene(slicer.mrmlScene)
    self.ui.uModel.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelectModels)
    self.ui.deformModel.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelectModels)
    self.ui.createPoints.connect('clicked(bool)', self.onApplyCreatePoints)

    self.ui.modelNode.connect("currentNodeChanged(vtkMRMLNode*)", self.onCell)

    self.ui.brainModel.setMRMLScene(slicer.mrmlScene)
    self.ui.brainModel.connect("currentNodeChanged(vtkMRMLNode*)", self.onContactButton)

    self.ui.createContactButton.connect('clicked(bool)', self.onCreateContactsButtonSelection)

    self.ui.fVolume.connect("currentNodeChanged(vtkMRMLNode*)", self.onRegistrationParamSelection)
    self.ui.mVolume.connect("currentNodeChanged(vtkMRMLNode*)", self.onRegistrationParamSelection)
    self.ui.oVolume.connect("currentNodeChanged(vtkMRMLNode*)", self.onRegistrationParamSelection)
    self.ui.transformNode.connect("currentNodeChanged(vtkMRMLNode*)", self.onRegistrationParamSelection)
    #self.ui.registrationPresetSelector.connect('valueChanged(int)', self.onRegistrationParamSelection)
    self.ui.register_2.connect('clicked(bool)', self.onRegistrationButton)

    self.ui.fiducialToTrans.connect("currentNodeChanged(vtkMRMLNode*)", self.onfidTotransformParamSelection)
    self.ui.transformNode_2.connect("currentNodeChanged(vtkMRMLNode*)", self.onfidTotransformParamSelection)

    self.ui.inputImageMri.setMRMLScene(slicer.mrmlScene)
    self.ui.inputMaskMri.setMRMLScene(slicer.mrmlScene)

    self.ui.inputImageMri.connect("currentNodeChanged(vtkMRMLNode*)", self.onFuzzyButton)
    self.ui.inputMaskMri.connect("currentNodeChanged(vtkMRMLNode*)", self.onFuzzyButton)

    self.ui.fuzzyButton.connect('clicked(bool)', self.onFuzzyApply)

    self.ui.removeSkullEle.connect('clicked(bool)', self.onApplyRemoveSkullEle)
    """# Parameters Area
    #
    parametersCollapsibleButton = ctk.ctkCollapsibleButton()
    parametersCollapsibleButton.text = "Parameters"
    self.layout.addWidget(parametersCollapsibleButton)

    # Layout within the dummy collapsible button
    parametersFormLayout = qt.QFormLayout(parametersCollapsibleButton)

    # input volume selector
    #
    self.inputSelector = slicer.qMRMLNodeComboBox()
    self.inputSelector.nodeTypes = ["vtkMRMLSequenceNode"]
    self.inputSelector.selectNodeUponCreation = True
    self.inputSelector.addEnabled = False
    self.inputSelector.removeEnabled = False
    self.inputSelector.noneEnabled = False
    self.inputSelector.showHidden = False
    self.inputSelector.showChildNodeTypes = False
    self.inputSelector.setMRMLScene( slicer.mrmlScene )
    self.inputSelector.setToolTip("Pick input volume sequence. Each time point will be registered to the fixed frame.")
    parametersFormLayout.addRow("Input volume sequence:", self.inputSelector)

    #
    # output volume selector
    #
    self.outputVolumesSelector = slicer.qMRMLNodeComboBox()
    self.outputVolumesSelector.nodeTypes = ["vtkMRMLSequenceNode"]
    self.outputVolumesSelector.baseName = "OutputVolumes"
    self.outputVolumesSelector.selectNodeUponCreation = True
    self.outputVolumesSelector.addEnabled = True
    self.outputVolumesSelector.removeEnabled = True
    self.outputVolumesSelector.renameEnabled = True
    self.outputVolumesSelector.noneEnabled = True
    self.outputVolumesSelector.showHidden = False
    self.outputVolumesSelector.showChildNodeTypes = False
    self.outputVolumesSelector.setMRMLScene(slicer.mrmlScene)
    self.outputVolumesSelector.setToolTip("Select a node for storing computed motion-compensated volume sequence.")
    parametersFormLayout.addRow("Output volume sequence:", self.outputVolumesSelector)

    #
    # output transform selector
    #
    self.outputTransformSelector = slicer.qMRMLNodeComboBox()
    self.outputTransformSelector.nodeTypes = ["vtkMRMLSequenceNode"]
    self.outputTransformSelector.baseName = "OutputTransforms"
    self.outputTransformSelector.selectNodeUponCreation = True
    self.outputTransformSelector.addEnabled = True
    self.outputTransformSelector.removeEnabled = True
    self.outputTransformSelector.renameEnabled = True
    self.outputTransformSelector.noneEnabled = True
    self.outputTransformSelector.showHidden = False
    self.outputTransformSelector.showChildNodeTypes = False
    self.outputTransformSelector.setMRMLScene(slicer.mrmlScene)
    self.outputTransformSelector.setToolTip("Computed displacement field that transform nodes from moving volume space to fixed volume space. NOTE: You must set at least one output sequence (transform and/or volume).")
    parametersFormLayout.addRow("Output transform sequence:", self.outputTransformSelector)



    import Elastix
    self.registrationPresetSelector = qt.QComboBox()
    self.registrationPresetSelector.setToolTip("Pick preset to register with.")
    for preset in self.logic.elastixLogic.getRegistrationPresets():
      self.registrationPresetSelector.addItem("{0} ({1})".format(preset[Elastix.RegistrationPresets_Modality], preset[Elastix.RegistrationPresets_Content]))
    self.registrationPresetSelector.addItem("*NEW*")
    self.newPresetIndex = self.registrationPresetSelector.count - 1
    parametersFormLayout.addRow("Preset:", self.registrationPresetSelector)"""
    #filling the combo box preset
    self.logic = MeshNodesToFiducialsLogic()
    """import Elastix
    for preset in self.logic.elastixLogic.getRegistrationPresets():
      self.ui.registrationPresetSelector.addItem("{0} ({1})".format(preset[Elastix.RegistrationPresets_Modality], preset[Elastix.RegistrationPresets_Content]))
    self.ui.registrationPresetSelector.addItem("*NEW*")"""



    # Add vertical spacer
    self.layout.addStretch(1)

    # Refresh Apply button state
    self.onSelect()
  def onApplyRemoveSkullEle(self):
    logic = MeshNodesToFiducialsLogic()
    logic.removeSkullElements(self.ui.meshInpFile.currentPath, self.ui.skullElement.currentPath, self.ui.outMeshInpFile.currentPath)

  def onContactButton(self):
    self.ui.createContactButton.enabled= self.ui.brainModel.currentNode()

  def onCreateContactsButtonSelection(self):
    logic = MeshNodesToFiducialsLogic()
    logic.createContacts(self.ui.brainModel.currentNode(), self.ui.skullElement.currentPath, self.ui.saveFileInp.currentPath, self.ui.nodeFile.currentPath)


  def onSMeshButton(self):
    logic = MeshNodesToFiducialsLogic()
    inputFile = self.ui.inputModelFile.currentPath
    nClusters = self.ui.nClusters.value
    logic.createSurfaceMesh(inputFile, int(nClusters))

  def onVMeshButton(self):
    logic = MeshNodesToFiducialsLogic()
    sMesh = self.ui.surfaceMesh.currentNode()
    meshAlgo = self.ui.meshAlgo.currentText
    cMin = self.ui.cMin.value
    cMax = self.ui.cMax.value
    optimize = self.ui.optimize.value
    meshQuality = self.ui.meshQuality.value
    lFactor = self.ui.lFactor.value

    logic.createVolumeMesh(sMesh, meshAlgo, int(cMin), int(cMax), int(optimize), int(meshQuality), int(lFactor))

  def onFuzzyButton(self):
    self.ui.fuzzyButton.enabled= self.ui.inputImageMri.currentNode() and self.ui.inputMaskMri.currentNode()

  def onFuzzyApply(self):
    logic= MeshNodesToFiducialsLogic()
    inputImage = self.ui.inputImageMri.currentNode()
    inputMask = self.ui.inputMaskMri.currentNode()
    intFile = self.ui.integrationFile.currentPath
    mFile = self.ui.mFile.currentPath
    logic.createFuzzyClassification(inputImage,inputMask, intFile, mFile)

  def cleanup(self):
    pass

  def onfidTotransformParamSelection(self):
    self.ui.transformFid.enabled = self.ui.fiducialToTrans.currentNode() and self.ui.transformNode_2.currentNode()

  def onRegistrationParamSelection(self):
    self.ui.register_2.enabled = self.ui.fVolume.currentNode() and self.ui.mVolume.currentNode() and self.ui.transformNode.currentNode() and self.ui.oVolume.currentNode()

  def onSelectDeformationModel(self):
    self.ui.warpModelButton.enabled = self.ui.dModel.currentNode()

  def onSelectModels(self):
    #select models and enable the apply button to create the point model files
    self.ui.createPoints.enabled = self.ui.uModel.currentNode() and self.ui.deformModel.currentNode()

  def onSelect(self):
    self.ui.applyButton.enabled = self.ui.inputSelector.currentNode() and self.ui.outputSelector.currentNode()

  def onCell(self):
    self.ui.pushButton.enabled = self.ui.modelNode.currentNode()

  def onCelltoFiducialButton(self):
    logic = MeshNodesToFiducialsLogic()
    logic.cellToFiducial(self.ui.modelNode.currentNode(), self.ui.displacedNodesFile.currentPath)

  def onRegistrationButton(self):
    logic = MeshNodesToFiducialsLogic()
    logic.registerVolumes(self.ui.fVolume.currentNode(), self.ui.mVolume.currentNode(), self.ui.oVolume.currentNode() , self.ui.transformNode.currentNode(),self.ui.registrationPresetSelector.currentIndex)

  def ontransformFidButton(self):
    logic = MeshNodesToFiducialsLogic()
    logic.createTransform(self.ui.fiducialToTrans.currentNode(), self.ui.transformNode_2.currentNode())

  def onApplyCreatePoints(self):
    #after clicking this button the method inside the logic is called
    logic = MeshNodesToFiducialsLogic()
    logic.runCreateModelPoints(self.ui.uModel.currentNode(), self.ui.deformModel.currentNode(), self.ui.uModelPointsFile.currentPath, self.ui.deformModelPointsFile.currentPath)

  def onApplyButton(self):
    logic = MeshNodesToFiducialsLogic()
    #enableScreenshotsFlag = self.ui.enableScreenshotsFlagCheckBox.checked
    #imageThreshold = self.ui.imageThresholdSliderWidget.value
    logic.run(self.ui.inputSelector.currentNode(), self.ui.outputSelector.currentNode(), self.ui.eleFile.currentPath, self.ui.brainNodeFile.currentPath)

  def onloadCreationButton(self):
    logic = MeshNodesToFiducialsLogic()
    logic.loadCreationMethod(self.ui.fNode.currentNode(), self.ui.tfNode.currentNode(), self.ui.loadFile.currentPath)

  def onApplyWarpModelButton(self):
    logic = MeshNodesToFiducialsLogic()
    logic.runDeformModelMethod(self.ui.dModel.currentNode())

#
# MeshNodesToFiducialsLogic
#

class MeshNodesToFiducialsLogic(ScriptedLoadableModuleLogic):
  """This class should implement all the actual
  computation done by your module.  The interface
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget.
  Uses ScriptedLoadableModuleLogic base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """
  def __init__(self):
    ScriptedLoadableModuleLogic.__init__(self)
    self.logStandardOutput = False
    self.logCallback = None

    #import Elastix
    #self.elastixLogic = Elastix.ElastixLogic()

  def hasImageData(self,volumeNode):
    """This is an example logic method that
    returns true if the passed in volume
    node has valid image data
    """
    if not volumeNode:
      logging.debug('hasImageData failed: no volume node')
      return False
    if volumeNode.GetImageData() is None:
      logging.debug('hasImageData failed: no image data in volume node')
      return False
    return True

  def isValidInputOutputData(self, inputVolumeNode, outputVolumeNode):
    """Validates if the output is not the same as input
    """
    if not inputVolumeNode:
      logging.debug('isValidInputOutputData failed: no input volume node defined')
      return False
    if not outputVolumeNode:
      logging.debug('isValidInputOutputData failed: no output volume node defined')
      return False
    if inputVolumeNode.GetID()==outputVolumeNode.GetID():
      logging.debug('isValidInputOutputData failed: input and output volume is the same. Create a new volume for output to avoid this error.')
      return False
    return True


  def runCreateModelPoints(self, uModel, dModel, uFile, dFile):
      #run thid method to save the modelpoints extracted fromt he models in the files

      mesh = slicer.util.getNode(uModel.GetID()).GetMesh()
      points_data = mesh.GetPoints().GetData()
      numpy_pointdata = vtk.util.numpy_support.vtk_to_numpy(points_data)
      print(numpy_pointdata)

      mesh2 = slicer.util.getNode(dModel.GetID()).GetMesh()
      points_data2 = mesh2.GetPoints().GetData()
      numpy_pointdata2 = vtk.util.numpy_support.vtk_to_numpy(points_data2)
      print(numpy_pointdata2)

      import numpy as np
      np.savetxt(uFile, numpy_pointdata , fmt = "%.8f, %.8f, %.8f", newline='\n')
      np.savetxt(dFile, numpy_pointdata2 , fmt = "%.8f, %.8f, %.8f", newline='\n')





      """import numpy as np
      import meshio

      mesh = meshio.read("/home/saima/explicitsim/build-bucketsearch/epilepsy/case114_mtled/brain0.vtu")

      points_preop = mesh.points

      print(points_preop)

      mesh1 = meshio.read("/home/saima/explicitsim/build-bucketsearch/epilepsy/case114_mtled/brain7.vtu")

      displacements = mesh1.point_data['Displacements']

      points_intraop = points_preop + displacements

      np.savetxt('/home/saima/explicitsim/build-bucketsearch/epilepsy/case114_mtled/prebrain.txt', points_preop, fmt = "%.8f, %.8f, %.8f", newline='\n')
      np.savetxt('/home/saima/explicitsim/build-bucketsearch/epilepsy/case114_mtled/postbrain.txt', points_intraop, fmt = "%.8f, %.8f, %.8f", newline='\n')"""



  def runDeformModelMethod(self, inputModel):
      #run the mehtod and deform the model by warping the deformation field from within the model got from MTLED runiing
      logging.info('Processing started')



      model = slicer.util.getNode(inputModel.GetID())
      mesh =  model.GetMesh()
      mesh.GetPointData().SetActiveVectors("Displacements")
      warpvector = vtk.vtkWarpVector()
      warpvector.SetInputData(mesh)
      #warpvector.SetInputConnection(mesh.GetProducerPort())
      #warpvector.SetInputArraysToProcess(0,0,0,"vtkDataObject::FIELD_ASSOCIATION_POINTS", "Total_displacement")
      #warpvector.SetInputArrayToProcess(0,0,0,"vtkDataObject::FIELD_ASSOCIATION_POINTS", "Distance")
      #warpvector.Vectors =['POINTS', 'Total_displacement']
      #warpvector.SetScaleFactor(1.0)
      warpvector.Update()
      output = warpvector.GetUnstructuredGridOutput()
      #output = warpvector.GetOutput()

      mesh2 = vtk.vtkUnstructuredGrid()
      mesh2.SetPoints(output.GetPoints())
      mesh2.SetCells(output.GetCellTypesArray(),output.GetCellLocationsArray(), output.GetCells())
      mesh2.UpdateCellGhostArrayCache()
      mesh2.UpdatePointGhostArrayCache()

      modelNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLModelNode')
      modelNode.SetAndObserveMesh(mesh2)
      logging.info('Processing end')


  def createSurfaceMesh(self, inputModelFile, nClusters ):
      print(inputModelFile, nClusters)
      import time
      start_time = time.time()
      import pyvista as pv
      import pyacvd
      surfacemesh = pv.read(inputModelFile)
      print(surfacemesh)
      clus = pyacvd.Clustering(surfacemesh)
      clus.subdivide(3)
      clus.cluster(nClusters)
      nmesh = clus.create_mesh()
      print(nClusters)

      dir_path = os.path.dirname(os.path.realpath(__file__))
      #print(dir_path)
      filePath =dir_path+"/surfaceMeshModel.stl"
      nmesh.save(filePath)

      sMeshModel = slicer.util.loadModel(filePath)

      n = slicer.util.getNode(sMeshModel.GetID())
      nn = n.GetModelDisplayNode()
      nn.EdgeVisibilityOn()
      print("----%s seconds ----"%(time.time()-start_time))

      return True
  def createVolumeMesh(self, sMesh, meshAlgo, cMin, cMax, optimize, meshQuality, lFactor):
      logging.info('Processing started')

      print(sMesh, meshAlgo, cMin, cMax, optimize, meshQuality, lFactor)
      print(type(cMin),type(cMax),type(optimize), type(meshQuality), type(lFactor))
      import time
      start_time = time.time()

      import gmsh

      gmsh.initialize()
      gmsh.option.setNumber("General.Terminal", 1)
      gmsh.option.setNumber("Mesh.Algorithm", 8);
      gmsh.option.setNumber("Mesh.CharacteristicLengthMin", 2);
      gmsh.option.setNumber("Mesh.CharacteristicLengthMax", 2);
      gmsh.option.setNumber("Mesh.Optimize",1)
      gmsh.option.setNumber("Mesh.QualityType",2);

      gmsh.option.setNumber("Mesh.CharacteristicLengthFactor",5)#

      node = slicer.util.getNode(sMesh.GetID())
      dir_path = os.path.dirname(os.path.realpath(__file__))
      filePath = dir_path+"/sMesh.stl"
      properties = {'useCompression': 0}; #do not compress
      slicer.util.saveNode(node, filePath, properties)

      sMeshModel = slicer.util.loadModel(filePath)

      gmsh.merge(filePath)
      n = gmsh.model.getDimension()
      s = gmsh.model.getEntities(n)
      l = gmsh.model.geo.addSurfaceLoop([s[i][1] for i in range(len(s))])
      gmsh.model.geo.addVolume([l])
      #print("Volume added")
      gmsh.model.geo.synchronize()
      gmsh.model.mesh.generate(3)

      #print("mesh generated")
      gmsh.write(dir_path+"/vMesh.msh")
      gmsh.finalize()
      #print("finalize")

      import meshio

      mesh = meshio.read(dir_path+"/vMesh.msh")
      meshio.write(dir_path+"/vMesh.vtk", mesh)
      vMeshModel = slicer.util.loadModel(dir_path+"/vMesh.vtk")

      n = slicer.util.getNode(vMeshModel.GetID())
      nn = n.GetModelDisplayNode()
      nn.EdgeVisibilityOn()
      print("----%s seconds ----"%(time.time()-start_time))

      logging.info('Processing completed')
      return True

  def loadCreationMethod(self,fNode, tNode, loadFile):
    #creating loads from pre and transformed fiducial points
    """import numpy as np
    import meshio
    from stl import mesh
    mesh1 = meshio.read("/home/saima/explicitsim/build/brainshift/VolumeMesh_skull.inp")
    displaced_idxs = np.array(mesh1.node_sets['contact'][0])
    Preop_positions = np.genfromtxt('/home/saima/slicer/brainshift/fiducials_29.fcsv', delimiter=',')[:,1:4]

    Intraop_positions = np.genfromtxt('/home/saima/slicer/brainshift/MarkupsFiducial_transformed.fcsv', delimiter=',')[:,1:4]

    loads = np.zeros([Preop_positions.shape[0], 7])
    loads[:,1:4] = 1
    loads[:, 4:7] = Preop_positions-Intraop_positions
    loads[:, 0] = displaced_idxs

    # Save material properties
    np.savetxt('/home/saima/slicer/brainshift/loads_auto.txt', loads, newline='\n', fmt = "%d, %d, %d, %d, %.8f, %.8f, %.8f")"""
    import time
    start_time = time.time()
    fidLabel=[]
    fidRas = []
    fidNode = slicer.util.getNode(fNode.GetID())
    #print(fidNode)
    numFid= fidNode.GetNumberOfFiducials()
    for i in range(numFid):
        ras=[0,0,0]
        fidNode.GetNthFiducialPosition(i,ras)
        l = fidNode.GetNthFiducialLabel(i)
        fidLabel.append(l)
        fidRas.append(ras)
    #print(fidLabel)
    #print(fidRas)
    #print(tNode, loadFile)
    import numpy as np
    fidRasN = np.array(fidRas)
    tLabel =[]
    tRas=[]
    tNode = slicer.util.getNode(tNode.GetID())
    tNum= tNode.GetNumberOfFiducials()
    for j in range(tNum):
        tras=[0,0,0]
        tNode.GetNthFiducialPosition(j,tras)
        l = tNode.GetNthFiducialLabel(j)
        #print(l)
        tLabel.append(l)
        tRas.append(tras)

    #print(tLabel)
    #print(tRas)
    #convert to numpy
    tRasN = np.array(tRas)
    tRasN[:,0]/=1000
    tRasN[:,1]/=1000
    tRasN[:,2]/=1000
    tRasN[:,0]*=-1
    tRasN[:,1]*=-1
    print(tRasN)
    fidRasN[:,0]/=1000
    fidRasN[:,1]/=1000
    fidRasN[:,2]/=1000
    fidRasN[:,0]*=-1
    fidRasN[:,1]*=-1
    print(fidRasN)
    sub = tRasN.__sub__(fidRasN)
    print(sub[0][1])
    #print(sub[0][2])
    #print(type(sub))
    #loadFile = os.path.dirname(os.path.realpath(__file__))
    #file = open(loadFile+"/loadCreation.txt",'w+')
    file = open(loadFile,'w+')
    for i in range(numFid):
        fidLabel[i] = int(fidLabel[i])
        #file.writelines([str(fidLabel[i]),",",str(1),",",str(1),",",str(1),",",str(sub[i][0]),",",str(sub[i][1]),",",str(sub[i][2]),"\n"])
        file.writelines([str(fidLabel[i]),",",str(1),",",str(1),",",str(1),",",str(sub[i][0]),",",str(sub[i][1]),",",str(sub[i][2]),"\n"])
    file.close()
    print("--- %s seconds ---" % (time.time() - start_time))
    return True
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
    #print(electrodePos)
    import numpy as np
    global electrodePosArray1
    electrodePosArray = np.array(electrodePos)
    electrodePosArray1 = np.unique(electrodePosArray)
    print("electrode array unique:", electrodePosArray1)
    print("Nuber of Cells")
    print(len(electrodePosArray1))
    print(arr)
    #cells to nodel selection on brain surface

    return electrodePosArray1




  def cellToFiducial(self, modelNode, displacedNodesFile):
    global electrodePosArray1
    #read the node and save the node to file in inp
    #electrodePosArray1 = [27 ,29 ,30 ,31 ,33 ,34 ,37 ,38 ,39 ,41 ,42 ,43 ,44 ,87 ,90 ,92 ,105 ,106 ,107 ,108 ,110 ,112 ,113 ,119 ,142 ,143 ,150 ,151 ,152 ,167 ,168 ,169 ,170 ,171 ,172 ,173 ,174 ,175 ,176 ,177 ,178 ,179 ,180 ,181 ,182 ,206 ,207 ,208 ,209 ,210 ,211 ,212 ,250 ,251 ,252 ,254 ,255 ,256 ,263 ,264 ,265 ,266 ,267 ,268 ,269 ,270 ,281 ,282 ,283 ,284 ,289 ,290 ,291 ,292 ,297 ,298 ,299 ,300 ,301 ,302 ,303 ,304 ,305 ,306 ,307 ,308 ,309 ,334 ,335 ,336 ,337 ,338 ,339 ,340 ,347 ,349 ,350 ,353 ,354 ,355 ,356 ,357 ,358 ,359 ,360 ,361 ,362 ,368 ,369 ,372 ,373 ,374 ,375 ,376 ,378 ,389 ,390 ,391 ,392 ,393 ,396 ,399 ,400 ,402 ,403 ,404 ,405 ,406 ,407 ,408 ,409 ,415 ,416 ,417 ,418 ,419 ,420 ,437 ,438 ,446 ,447 ,448 ,449 ,450 ,452 ,453 ,482 ,483 ,490 ,491 ,492 ,493 ,494 ,504 ,505 ,524 ,525 ,531 ,532 ,533 ,534 ,535 ,536 ,552 ,553 ,573 ,581 ,583 ,584 ,585 ,616 ,617 ,618 ,620 ,679 ,681 ,682 ,683 ,684 ,703 ,705 ,706 ,707 ,713 ,714 ,715 ,716 ,717 ,749 ,750 ,751 ,753 ,754 ,800 ,801 ,810 ,811 ,812 ,813 ,814 ,816 ,827 ,828 ,829 ,831 ,842 ,844 ,845 ,846 ,847 ,848 ,849 ,873 ,875 ,876 ,877 ,878 ,879 ,880 ,881 ,882 ,883 ,894 ,895 ,904 ,906 ,907 ,908 ,921 ,922 ,923 ,924 ,933 ,936 ,987 ,990 ,991 ,994 ,996 ,997 ,1033 ,1052 ,1103 ,1104 ,1105 ,1106 ,1123 ,1124 ,1126 ,1127 ,1171 ,1172 ,1173 ,1174 ,1176 ,1179 ,1181 ,1193 ,1194 ,1195 ,1196 ,1236 ,1237 ,1240 ,1256 ,1257 ,1258 ,1259 ,1260 ,1261 ,1264 ,1280 ,1282 ,1286 ,1287 ,1288 ,1289 ,1290 ,1291 ,1292 ,1293 ,1294 ,1295 ,1296 ,1297 ,1298 ,1299 ,1300 ,1328 ,1329 ,1330 ,1331 ,1332 ,1333 ,1336 ,1337 ,1338 ,1339 ,1340 ,1341 ,1343 ,1344 ,1345 ,1346 ,1362 ,1363 ,1364 ,1365 ,1371 ,1372 ,1373 ,1374 ,1375 ,1376 ,1397 ,1398 ,1400 ,1401 ,1403 ,1404 ,1405 ,1406 ,1408 ,1409 ,1410 ,1411 ,1444 ,1445 ,1446 ,1447 ,1448 ,1449 ,1450 ,1451 ,1452 ,1454 ,1457 ,1463 ,1469 ,1470 ,1471 ,1472 ,1485 ,1486 ,1488 ,1491 ,1492 ,1493 ,1494 ,1498 ,1499 ,1500 ,1501 ,1507 ,1508 ,1511 ,1512 ,1513 ,1514 ,1515 ,1527 ,1528 ,1529 ,1530 ,1531 ,1532 ,1533 ,1535 ,1536 ,1537 ,1542 ,1548 ,1551 ,1552 ,1553 ,1559 ,1571 ,1572 ,1587 ,1588 ,1589 ,1590 ,1611 ,1612 ,1618 ,1619 ,1625 ,1638 ,1639 ,1640 ,1642 ,1643 ,1645 ,1680 ,1681 ,1683 ,1689 ,1708 ,1714 ,1715 ,1716 ,1717 ,1754 ,1755 ,1756 ,1757 ,1758 ,1759 ,1782 ,1800 ,1802 ,1803 ,1824 ,1863 ,1864 ,1865 ,1866 ,1867 ,1868 ,1869 ,1870 ,1873 ,1874 ,1875 ,1877 ,1878 ,1897 ,1898 ,1899 ,1901 ,1902 ,1909 ,1910 ,1911 ,1912 ,1913 ,1914 ,1915 ,1916 ,1917 ,1927 ,1928 ,1929 ,1930 ,1951 ,1952 ,1956 ,1957 ,1966 ,1967 ,1968 ,1969 ,1970 ,1974 ,1975 ,1992 ,1993 ,1994 ,2023 ,2024 ,2025 ,2026 ,2044 ,2045 ,2046 ,2047 ,2048 ,2049 ,2050 ,2099 ,2100 ,2124 ,2125 ,2127 ,2160 ,2161 ,2162 ,2163 ,2164 ,2165 ,2167 ,2197 ,2199 ,2200 ,2201 ,2234 ,2235 ,2236 ,2237 ,2238 ,2297 ,2298 ,2299 ,2347 ,2362 ,2363 ,2364 ,2432 ,2445 ,2446 ,2447 ,2461 ,2463 ,2464 ,2468 ,2469 ,2480 ,2481 ,2482 ,2483 ,2493 ,2503 ,2504 ,2518 ,2521 ,2522 ,2523 ,2533 ,2534 ,2540 ,2541 ,2542 ,2543 ,2544 ,2567 ,2568 ,2589 ,2590 ,2591 ,2592 ,2627 ,2628 ,2673 ,2674 ,2721 ,2723 ,2724 ,2726 ,2727 ,2762 ,2763 ,2765 ,2786 ,2802 ,2803 ,2814 ,2815 ,2816 ,2828 ,2829 ,2840 ,2853 ,2854 ,2881 ,2882 ,2913 ,2914 ,2924 ,2950 ,2953 ,2965 ,2967 ,2968 ,2985 ,2986 ,2988 ,2989 ,2990 ,2991 ,3000 ,3001 ,3002 ,3003 ,3006 ,3007 ,3008 ,3009 ,3010 ,3011 ,3012 ,3013 ,3019 ,3020 ,3022 ,3023 ,3024 ,3025 ,3027 ,3029 ,3031 ,3056 ,3057 ,3060 ,3061 ,3070 ,3071 ,3083 ,3084 ,3085 ,3086 ,3112 ,3113 ,3191 ,3192 ,3193 ,3198 ,3199 ,3201 ,3202 ,3204 ,3206 ,3209 ,3211 ,3239 ,3240 ,3241 ,3242 ,3243 ,3244 ,3283 ,3284 ,3285 ,3286 ,3306 ,3307 ,3316 ,3318 ,3320 ,3321 ,3322 ,3341 ,3342 ,3343 ,3344 ,3345 ,3347 ,3365 ,3366 ,3367 ,3368 ,3369 ,3370 ,3371 ,3378 ,3379 ,3386 ,3387 ,3388 ,3391 ,3407 ,3408 ,3409 ,3425 ,3426 ,3427 ,3438 ,3439 ,3440 ,3441 ,3461 ,3477 ,3478 ,3479 ,3503 ,3504 ,3505 ,3506 ,3508 ,3509 ,3576 ,3577 ,3602 ,3610 ,3611 ,3625 ,3672 ,3708 ,3709 ,3710 ,3734 ,3735 ,3736 ,3754 ,3755 ,3760 ,3761 ,3762 ,3763 ,3764 ,3776 ,3778 ,3779 ,3780 ,3781 ,3782 ,3789 ,3790 ,3795 ,3827 ,3828 ,3917 ,3918 ,3919 ,3920 ,3921 ,3925 ,3926 ,3927 ,3930 ,3938 ,3946 ,3947 ,3953 ,3954 ,3963 ,3971 ,3972 ,3974 ,3975 ,3980 ,3981 ,3982 ,3983 ,3985 ,3986 ,3987 ,3989 ,3990 ,3991 ,3995]
    import time
    start_time = time.time()
    print(electrodePosArray1)
    electrodePosArray1 = [i+1 for i in electrodePosArray1]
    print(electrodePosArray1)
    node = slicer.util.getNode(modelNode.GetID())
    #mesh = node.GetMesh().GetCellData()
    #properties = {'useCompression': 0}; #do not compress
    #file_name = "surfaceModel.stl"
    #file_path = os.path.join(mydir, file_name)
    import time
    start_time = time.time()
    file_path ="/home/saima/volumeMesh.vtk"
    slicer.util.saveNode(node, file_path)

    import meshio
    mesh = meshio.read(r"/home/saima/volumeMesh.vtk")
    meshio.write(r"/home/saima/volumeMesh.inp", mesh)

    #reading the inp file to extract nodes for the seleted cells
    f = open("/home/saima/volumeMesh.inp","r")
    lines = f.readlines();
    nn = 1
    nodes=[]
    copy = False
    for l in lines:
        if("S3RS" in l):
            copy = True
            continue;
        if copy==False:
            lastNode = l.split(",")
            #print("lastNode",lastNode[0])
        if("C3D4" in l):
            break;
        if copy:
             #parse the next line
            #get the first number
            #match the number witht the array above
            #copy the line to a new file
            #after all numbers lines saved
            #open file and read all the nmbers excet numbers in first line
            #print(l)
            b=l.split(',')
            b1=int(b[0])
            b2=int(b[1])
            b3=int(b[2])
            b4=int(b[3])
            if b1 in electrodePosArray1:
                 #print(b1)
                 #print(b2, b3, b4)
                 nodes.append(b2)
                 nodes.append(b3)
                 nodes.append(b4)
                 print("nodes for electrode pos array1")
                 print(b2,',',b3,',',b4,',')
                 #o.write(str(b2))
                 #o.write(",")
                 #o.write(str(b3))
                 #o.write(",")
                 #o.write(str(b4))
                 #o.write(",")
                 #print(nn)
                 nn = nn+1
    print(lastNode)
    import numpy as np
    nodes_unique = np.unique(nodes)
    nodes_unique.sort()
    print(nodes_unique)
    f.close()
    o = open(displacedNodesFile,"w+")
    for i in range(len(nodes_unique)):
        o.write(str(nodes_unique[i]))
        o.write(",")

    o.close()

    o = open("/home/saima/cells.txt", "w+")
    for i in range(len(electrodePosArray1)):
        o.write(str(electrodePosArray1[i]))
        o.write(",")

    o.close()

    #searching for nodes in the file for x y z
    #nodes_unique = [i - 1 for i in nodes_unique]
    nodes_unique = [i for i in nodes_unique]
    markupsNode3 = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsFiducialNode")
    markupsNode3.CreateDefaultDisplayNodes()
    #fiducialArray = []
    #reading file until s3 elements to get all the nodes only
    f = open("/home/saima/volumeMesh.inp","r")
    while True:
        l = f.readline()
        if("Node" in l or "NODE" in l):
            continue
        if("Heading" in l or "HEADING" in l):
            continue
        if("Abaqus" in l):
            continue
        if("written" in l):
            continue
        if("S3RS" in l):
            break
        else:
            s = l.split(',')
            s1 = int(s[0])
            if(s1 in nodes_unique):
                s2 = float(s[1])
                s3 = float(s[2])
                s4 = float(s[3])
                print(s1,',',s2,',',s3,',',s4)
                markupsNode3.AddFiducial(-s2,-s3,s4,str(s1))
                #fiducialArray.append(s1,s2,s3,s4)

    f.close()
    d = markupsNode3.GetDisplayNode()
    d.PointLabelsVisibilityOff()

    #for j in range(len(nodes_unique)):
    print("--- %s seconds ---" % (time.time() - start_time))
    return True
  def registerVolumes(self, fVolume, mVolume,oVolume, transformNode, cIndex):
    #register volumes
    try:
        import Elastix
        elastixLogic = Elastix.ElastixLogic()
        parameterFilenames = elastixLogic.getRegistrationPresets()[cIndex][Elastix.RegistrationPresets_ParameterFilenames]
        useelastix = True
    except Exception as e:
        print(e)
        useelastix = False
    print(fVolume)
    print(cIndex)
    elastixLogic.registerVolumes(
                                fVolume, mVolume,
                                outputVolumeNode = oVolume,
                                parameterFilenames = parameterFilenames,
                                outputTransformNode = transformNode
                                )
    return True

  def createTransform(self, fiducial, transformNode):
    #transform fiducials
    print(fiducial, transformNode)
    #fnode = slicer.util.getNode(fiducial)
    trans = slicer.util.getNode(transformNode.GetID())
    n = fiducial.SetAndObserveTransformNodeID(transformNode.GetID())
    print(n)
    return True
  def createFuzzyClassification(self, inputImage, inputMask, intFile, mFile):
    #do fuzzy classification
    print("inside")
    import time
    start_time = time.time()
    import nrrd
    import numpy as np
    import skfuzzy as fuzz
    dir_path = os.path.dirname(os.path.realpath(__file__))
    slicer.util.saveNode(slicer.util.getNode(inputImage.GetID()), dir_path+"/brainImage.nrrd")
    slicer.util.saveNode(slicer.util.getNode(inputMask.GetID()), dir_path+"/brainMask.nrrd")

    brainMask, header = nrrd.read(dir_path+"/brainMask.nrrd")
    brainImg, header = nrrd.read(dir_path+"/brainImage.nrrd")
    #brainMask = slicer.util.arrayFromVolume(inputMask)
    #brainImg= slicer.util.arrayFromVolume(inputImage)
    #print(brainMask)
    #voxelIntensities = brainImg[brainMask > 0]
    #print(voxelIntensities)
    print(header)

    voxelIntensities = brainImg[brainMask > 0]
    ncenters = 2
    cntr, u, u0, d, jm, p, fpc = fuzz.cluster.cmeans(voxelIntensities.reshape(1, voxelIntensities.size), ncenters, 2, error=0.005, maxiter=1000, init=None)
    brain_ventricle_membership = np.zeros(brainImg.shape)
    brain_ventricle_membership[brainMask > 0] = u[0]

    brain_parenchima_membership = np.ones(brainImg.shape)
    brain_parenchima_membership[brainMask > 0] = u[1]

    nrrd.write(dir_path+"/brain_ventricle_membership.nrrd", brain_ventricle_membership, header)
    nrrd.write(dir_path+"/brain_parenchima_membership.nrrd", brain_parenchima_membership, header)
    slicer.util.loadVolume(dir_path+"/brain_ventricle_membership.nrrd")
    slicer.util.loadVolume(dir_path+"/brain_parenchima_membership.nrrd")

    #now creating material properties
    #pip_install("git+https://github.com/spezold/mvloader.git") installing in slicer
    import mvloader.nrrd as mvnrrd
    brain_ventricle_membership, header = nrrd.read(dir_path+"/brain_ventricle_membership.nrrd")

    brain_parenchima_membership_volume = mvnrrd.open_image(dir_path+"/brain_parenchima_membership.nrrd")

    brain_parenchima_membership = brain_parenchima_membership_volume.src_data
    # Create transform from world coordinates to voxel indeces
    voxels2world = brain_parenchima_membership_volume.src_transformation
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
                    material_props[idx, 1] += YM_parenchima * brain_parenchima_membership[i, j, k]+YM_ventricles * brain_ventricle_membership[i, j, k]
                    material_props[idx, 2] += PR_B * brain_parenchima_membership[i, j, k]+PR_V * brain_ventricle_membership[i, j, k]


        material_props[idx, 1]/= 8
        material_props[idx, 2]/= 8
        if material_props[idx, 1] == 0:
            print("YM is 0 for ip %d" % idx)

    np.savetxt(mFile, material_props, fmt = "%.8f, %.8f, %.8f", newline='\n')
    #np.savetxt(mFile+'mem.csv', memberships, delimiter=',', fmt="%.8f, %.8f, %.8f", newline='\n')    #np.savetxt(mFile+".mem.csv", np.hstack(brain_parenchima_membership[:],brain_ventricle_membership[:]))

    print("--- %s seconds ---" % (time.time() - start_time))
    return True

  def removeSkullElements(self, meshFile, eleFile, outFile):
    #this method removes skull elements from the created inp file with contacts
    logging.info("processing started")
    import numpy as np
    rmLst = np.genfromtxt(eleFile, delimiter=",", dtype=int)
    rmNew = rmLst[:-1]
    rmNew = rmNew+1
    print(rmNew)

    s="b"
    b="b"
    flag =0
    flag2=0
    with open(meshFile, "r")as ff:
            with open(outFile, "w+")as fj:
                new_f = ff.readlines()

                for line in new_f:
                    #print(line)
                    if "Node" in line or "NODE" in line:
                        #print(line)
                        fj.write(line)
                        continue
                    if "Abaqus" in line:
                        #print(line)
                        fj.write(line)
                        continue
                    if "written" in line:
                        #print(line)
                        fj.write(line)
                        continue
                    if "Heading" in line or "HEADING" in line:
                        #print(line)
                        fj.write(line)
                        continue
                    if "skull" in line:
                        #print(line)
                        s="skull"
                        flag2=1
                        fj.write(line)
                        continue
                    elif flag2 == 0:
                        fj.write(line)
                    if "brain" in line:
                        #print(line)
                        b = "brain"
                        flag=1
                        fj.write(line)
                    elif flag==0 and s=="skull":
                        text = line.split(',', 1)[0]
                        text = int(text)
                        print(text)
                        #print(type(text))
                        if text not in rmNew:
                          #print("inside skull")
                          #print(line)
                          fj.write(line)
                        else:
                          print("present")
                    elif flag==1 and b=="brain":
                          fj.write(line)
                          #print("no")


  def createContacts(self, model, skullEleFile, saveFile, nodeFile):
    #creating skull informationa nd saving it into inp file along with displacednodes information
    logging.info("processing started")
    import time
    start_time = time.time()
    dir_path = os.path.dirname(os.path.realpath(__file__))
    properties = {'useCompression': 0};
    slicer.util.saveNode(model,dir_path+"/brainModelContact.vtk",properties)

    import meshio
    volume_mesh = meshio.read(dir_path+"/brainModelContact.vtk")
    meshio.write(dir_path+"/brainModelContact.inp", volume_mesh)

    import numpy as np
    f = open(dir_path+"/brainModelContact.inp",'r')
    ff = open(saveFile,'w+') #for writing the lines of file

    nodes =[]
    lines = f.readlines()
    for l in lines:

            if "Node" in l or "NODE" in l:
                ff.write(l)
                continue
            if "Abaqus" in l:
                ff.write(l)
                continue
            if "written" in l:
                ff.write(l)
                continue
            if "Heading" in l or "HEADING" in l:
                ff.write(l)
                continue
            if "S3RS" in l:
                break
            else:
                ff.write(l)
                nodes.append(l)
    f.close()
    nodes_array = np.array(nodes)
    #print(nodes_array[-1])
    split_last_node = nodes_array[-1].split(',')
    n = int(split_last_node[0])
    #print(n)
    two_n = int(split_last_node[0])*2
    #print(two_n)

    for i in range(n):
        node_coord = nodes_array[i].split(',')
        node_coord1 = node_coord[0]
        print(node_coord1)
        node_coord2 = node_coord[1]
        node_coord3 = node_coord[2]
        node_coord4 = node_coord[3]
        new_coord = n+i+1
        #print(new_coord,',',node_coord2,',',node_coord3,',',node_coord4)
        ff.write(str(new_coord))
        ff.write(',')
        #ff.write(str(node_coord2)) old coords when there was no lps in slicer
        ff.write(str(node_coord2))
        ff.write(',')
        ff.write(str(node_coord3))
        ff.write(',')
        ff.write(str(node_coord4))

    #surface_triangle_cells = [28, 30, 31, 32, 34, 35, 38, 39, 40, 40, 41, 42, 43, 44, 45, 88, 91, 92, 93, 106, 107, 108, 109, 110, 111, 113, 114, 120, 143, 144, 151, 152, 153, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 181, 182, 183, 207, 208, 209, 210, 211, 211, 212, 213, 251, 252, 253, 254, 255, 256, 257, 264, 264, 265, 266, 267, 268, 269, 270, 270, 271, 271, 282, 283, 284, 285, 290, 291, 292, 293, 293, 298, 299, 300, 301, 302, 303, 303, 304, 305, 306, 306, 307, 308, 309, 310, 310, 334, 335, 336, 337, 338, 339, 340, 341, 348, 350, 351, 354, 355, 356, 357, 358, 359, 360, 361, 362, 363, 363, 369, 370, 373, 374, 375, 375, 376, 377, 377, 379, 390, 390, 391, 392, 393, 394, 397, 400, 401, 402, 403, 403, 404, 404, 405, 406, 407, 408, 409, 410, 416, 417, 418, 419, 420, 421, 438, 439, 447, 448, 449, 450, 451, 453, 454, 483, 484, 491, 492, 493, 493, 494, 495, 505, 506, 525, 526, 532, 533, 533, 534, 535, 536, 537, 537, 553, 554, 574, 582, 583, 584, 585, 586, 617, 618, 619, 620, 621, 680, 681, 682, 683, 684, 685, 704, 706, 707, 708, 708, 714, 715, 716, 717, 718, 750, 751, 752, 754, 755, 755, 801, 802, 811, 812, 813, 814, 815, 816, 817, 828, 829, 830, 832, 843, 844, 845, 846, 847, 848, 849, 850, 874, 875, 876, 877, 878, 879, 880, 881, 882, 883, 884, 894, 895, 896, 905, 907, 908, 909, 921, 922, 923, 924, 925, 934, 937, 938, 988, 991, 992, 995, 997, 998, 1034, 1053, 1104, 1105, 1106, 1107, 1108, 1124, 1125, 1126, 1127, 1128, 1172, 1173, 1174, 1175, 1176, 1177, 1180, 1181, 1182, 1194, 1195, 1196, 1197, 1237, 1238, 1241, 1257, 1258, 1259, 1260, 1261, 1262, 1263, 1265, 1281, 1283, 1286, 1287, 1288, 1289, 1290, 1291, 1292, 1293, 1294, 1295, 1296, 1297, 1298, 1299, 1300, 1301, 1302, 1329, 1329, 1330, 1331, 1332, 1333, 1334, 1337, 1338, 1339, 1340, 1341, 1342, 1343, 1344, 1345, 1346, 1347, 1363, 1364, 1365, 1366, 1372, 1373, 1374, 1374, 1375, 1376, 1377, 1398, 1399, 1401, 1402, 1403, 1404, 1405, 1406, 1407, 1409, 1410, 1411, 1412, 1444, 1445, 1446, 1447, 1448, 1449, 1450, 1451, 1452, 1453, 1455, 1458, 1464, 1470, 1471, 1472, 1473, 1486, 1487, 1489, 1492, 1493, 1494, 1494, 1495, 1499, 1500, 1501, 1502, 1508, 1509, 1511, 1512, 1513, 1514, 1515, 1516, 1528, 1529, 1530, 1531, 1532, 1532, 1533, 1534, 1535, 1536, 1537, 1538, 1543, 1549, 1552, 1553, 1554, 1560, 1572, 1573, 1588, 1589, 1590, 1591, 1612, 1613, 1619, 1620, 1621, 1626, 1639, 1640, 1641, 1642, 1643, 1644, 1646, 1681, 1682, 1683, 1684, 1690, 1709, 1715, 1716, 1717, 1718, 1755, 1756, 1757, 1758, 1758, 1759, 1760, 1783, 1801, 1803, 1804, 1825, 1864, 1864, 1865, 1866, 1867, 1868, 1868, 1869, 1870, 1870, 1871, 1874, 1875, 1876, 1878, 1879, 1898, 1899, 1900, 1900, 1902, 1903, 1910, 1910, 1911, 1912, 1913, 1914, 1914, 1915, 1916, 1917, 1917, 1918, 1928, 1929, 1929, 1930, 1931, 1932, 1952, 1953, 1957, 1957, 1958, 1967, 1968, 1969, 1970, 1971, 1975, 1976, 1993, 1994, 1995, 1996, 2024, 2024, 2025, 2026, 2027, 2027, 2045, 2046, 2046, 2047, 2048, 2049, 2050, 2050, 2051, 2100, 2101, 2125, 2126, 2128, 2161, 2162, 2163, 2164, 2165, 2166, 2167, 2168, 2198, 2200, 2201, 2202, 2234, 2235, 2236, 2237, 2238, 2239, 2298, 2299, 2300, 2348, 2363, 2364, 2364, 2365, 2433, 2446, 2447, 2448, 2462, 2464, 2465, 2469, 2470, 2481, 2482, 2483, 2484, 2494, 2504, 2505, 2519, 2522, 2523, 2524, 2534, 2535, 2541, 2542, 2542, 2543, 2544, 2545, 2568, 2569, 2590, 2590, 2591, 2592, 2593, 2628, 2628, 2629, 2674, 2675, 2722, 2724, 2725, 2727, 2728, 2763, 2764, 2765, 2766, 2787, 2803, 2804, 2815, 2816, 2817, 2829, 2830, 2841, 2854, 2855, 2857, 2882, 2883, 2914, 2915, 2925, 2951, 2952, 2954, 2966, 2968, 2969, 2986, 2987, 2989, 2990, 2991, 2992, 3001, 3002, 3003, 3004, 3007, 3008, 3009, 3010, 3011, 3012, 3013, 3013, 3014, 3020, 3021, 3023, 3024, 3025, 3026, 3028, 3029, 3030, 3031, 3032, 3033, 3057, 3058, 3061, 3062, 3071, 3072, 3084, 3084, 3085, 3086, 3087, 3113, 3114, 3192, 3193, 3194, 3199, 3200, 3202, 3203, 3204, 3205, 3206, 3207, 3210, 3212, 3240, 3241, 3242, 3243, 3244, 3245, 3284, 3285, 3286, 3287, 3288, 3307, 3308, 3317, 3319, 3321, 3322, 3323, 3323, 3342, 3343, 3343, 3344, 3345, 3346, 3348, 3366, 3367, 3368, 3369, 3370, 3371, 3372, 3379, 3380, 3387, 3388, 3389, 3390, 3391, 3392, 3408, 3409, 3410, 3426, 3427, 3428, 3428, 3439, 3440, 3441, 3442, 3462, 3478, 3479, 3479, 3480, 3481, 3504, 3505, 3506, 3507, 3508, 3509, 3510, 3577, 3578, 3603, 3611, 3612, 3626, 3673, 3709, 3710, 3711, 3735, 3736, 3737, 3755, 3756, 3761, 3761, 3762, 3763, 3764, 3765, 3777, 3779, 3779, 3780, 3781, 3782, 3783, 3790, 3791, 3791, 3796, 3828, 3829, 3918, 3919, 3920, 3921, 3922, 3926, 3927, 3928, 3931, 3932, 3939, 3947, 3948, 3954, 3955, 3956, 3964, 3972, 3973, 3974, 3975, 3976, 3981, 3982, 3983, 3984, 3986, 3987, 3988, 3990, 3991, 3992, 3996]
    #surface_triangle_cells = np.array(surface_triangle_cells)
    #reading the s3ds elements from the old file and putting it in the new file with all the nodes+n
    brainElements =[]
    #brainElementFile = open(dir_path+"/brainSurfaceElements.txt",'w+')
    with open(dir_path+"/brainModelContact.inp",'r') as fh:
        while True:
            line = fh.readline()
            if not "S3RS" in line:
                continue
            if "S3RS" in line:
                print("*Element,type=S3RS, ELSET=skull")
                #print the s3 ine in the file
                ff.write("*Element,type=S3RS, ELSET=skull")
                ff.write("\n")
                break
        while True:
            line = fh.readline()
            if "C3D4" in line:
                print("*Element,type=C3D4, ELSET=brain")
                ff.write("*Element,type=C3D4, ELSET=brain")
                ff.write("\n")
                break
            s = line.split(',')
            s1 = int(s[0])
            s2 = int(s[1])+n
            s3 = int(s[2])+n
            s4 = int(s[3])+n

            #print(s[1],s[2],s[3])
            brainElements.append(int(s[1]))
            brainElements.append(int(s[2]))
            brainElements.append(int(s[3]))

            #print(brainElements)
            #brain surface elements saving to some file so it can be included later to the inp file for contacts with the skull
            """brainElementFile.write(s2-n)
            brainElementFile.write(',')
            brainElementFile.write(s3-n)
            brainElementFile.write(',')
            brainElementFile.write(s4-n)
            brainElementFile.write(',')"""
            #write these updated node numbers for skull into the new inp file
            ff.write(str(s1))
            ff.write(',')
            ff.write(str(s3))
            ff.write(',')
            ff.write(str(s2))
            ff.write(',')
            ff.write(str(s4))
            ff.write('\n')
        while True:
            line = fh.readline()
            #brainElementFile.writelines(str(brainElements))

            #print(brainElements)
            #print(line)
            if "end" in line or (""==line):
                sbrain = np.unique(np.array(brainElements)     )
                print(sbrain)
                #np.savetxt(dir_path+'/data.txt', sbrain, delimiter=',')
                #from numpy import savetxt
                #savetxt(dir_path+'/data.txt', sbrain, dtype = int,  delimiter=',')
                #nodes2 = np.genfromtxt(dir_path+'/data.txt', dtype=int, delimiter=',')
                #print(nodes2)
                #nodes2 = nodes2[:]
                #nodes2 = list(set(nodes2.flatten().tolist()))
                #print(nodes2)
                nodeFileRead = open(nodeFile,'r')
                #brainElementFile = open(dir_path+"/brainSurfaceElements.txt",'r')
                #surfaceElementsBrain = brainElementFile.readlines()
                lines = nodeFileRead.readlines()
                ff.write("*NSET, NSET=displaced")
                ff.write("\n")
                ff.writelines(lines)
                ff.write("\n")
                ff.write("*NSET, NSET=surface")
                ff.write("\n")
                for sm in range(len(sbrain)):
                    print(sbrain[sm])
                    ff.write(str(sbrain[sm]))
                    ff.write(",")
                    if (sm+1) % 8 == 0 and sm < len(sbrain):
                        ff.write("\n")
                #ff.write("*NSET, NSET=surface")
                ff.write("\n")
                if(""==line):
                    ff.write("*end")
            if not line:
                break
                #ff.writelines(surfaceElementsBrain)
                #ff.write("\n")
            ff.write(line)
    ff.close()
    fh.close()
    #deleting displaced nodes from surface nodes


    print("--- %s seconds ---" % (time.time() - start_time))
    logging.info("processing completed")
    return True

  def run(self, inputVolume, outputVolume, eleFile, nodeFile):
    """
    Run the actual algorithm
    """

    if not self.isValidInputOutputData(inputVolume, outputVolume):
      slicer.util.errorDisplay('Input volume is the same as output volume. Choose a different output volume.')
      return False

    logging.info('Processing started')

    # Compute the thresholded output volume using the Threshold Scalar Volume CLI module
    #cliParams = {'InputVolume': inputVolume.GetID(), 'OutputVolume': outputVolume.GetID(), 'ThresholdValue' : imageThreshold, 'ThresholdType' : 'Above'}
    #cliNode = slicer.cli.run(slicer.modules.thresholdscalarvolume, None, cliParams, wait_for_completion=True)
    #get input model node
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
    """dir_path = os.path.dirname(os.path.realpath(__file__))
    #getting thre seconf mesh model and highlight the cells on the model using the created fiducials
    modelNode2 = slicer.util.getNode(outputVolume.GetID()) # select cells in this model
    #the model selected will be the volumetric mesh, extract the s3 elements from it make the stl file and then this stl will be use to get mesh and cell data
    properties = {'useCompression': 0}; #do not compress
    file_name = "surfaceModel.stl"
    #file_path = os.path.join(dir_path, file_name)
    #file_path ="/home/saima/slicer/Slicer-4.11.0-2019-09-17-linux-amd64/ImageAsaModel/MeshNodesToFiducials/volumeMesh.vtk"
    slicer.util.saveNode(modelNode2, dir_path+"/volumeMesh.vtk",properties)
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
    #loading stl into slicer
    #properties = {'useCompression': 0}"""
    surface_model_1 = slicer.util.getNode(outputVolume.GetID())

    cellScalars = surface_model_1.GetMesh().GetCellData()
    selectionArray = cellScalars.GetArray('selection')
    if not selectionArray:
      selectionArray = vtk.vtkIntArray()
      selectionArray.SetName('selection')
      selectionArray.SetNumberOfValues(surface_model_1.GetMesh().GetNumberOfCells())
      selectionArray.Fill(0)
      cellScalars.AddArray(selectionArray)

    surface_model_1.GetDisplayNode().SetActiveScalar("selection", vtk.vtkAssignAttribute.CELL_DATA)
    surface_model_1.GetDisplayNode().SetAndObserveColorNodeID("vtkMRMLColorTableNodeWarm1")
    surface_model_1.GetDisplayNode().SetScalarVisibility(True)

    cell = vtk.vtkCellLocator()
    cell.SetDataSet(surface_model_1.GetMesh())
    cell.BuildLocator()


    # Initial update
    arr = self.onPointsModified(selectionArray, markupsNode, cell)
    print("slicer cells mesh")
    print(arr)
    import numpy as np
    #[x+1 for x in arr]
    arrNumpy = np.array(arr)
    np.savetxt(eleFile,arrNumpy, fmt="%s", delimiter=",")
    #get the cell nodes using the arr
    import numpy
    markupsNode2 = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsFiducialNode")
    markupsNode2.CreateDefaultDisplayNodes()
    mesh = surface_model_1.GetMesh()
    print("nodes within slicer")
    nodes_array = []
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
        #ff.write(str(p1))
        #ff.write("\n")
        #ff.write(str(p2))
        #ff.write("\n")
        #ff.write(str(p3))
        #ff.write("\n")
        #points = closestCell.GetPoints()
        pointOne = points.GetPoint(0)
        a1 = numpy.array(pointOne)
        pointTwo = points.GetPoint(1)
        a2 = numpy.array(pointTwo)
        pointThree = points.GetPoint(2)
        a3 = numpy.array(pointThree)
        #print(p1,',',a1[0],',',a1[1],',',a1[2])
        #print(p2,',',a2[0],',',a2[1],',',a2[2])
        #print(p3,',',a3[0],',',a3[1],',',a3[2])

        if p1+1 in nodes_array:
            print("present already in array skip"+str(p1))
        else:
            markupsNode2.AddFiducial(a1[0],a1[1],a1[2],str(p1+1))
        if p2+1 in nodes_array:
            print("present already in array skip"+str(p2))
        else:
            markupsNode2.AddFiducial(a2[0],a2[1],a2[2],str(p2+1))
        if p3+1 in nodes_array:
            print("present already in array skip"+str(p3))
        else:
            markupsNode2.AddFiducial(a3[0],a3[1],a3[2],str(p3+1))
        nodes_array.append(p1+1)
        nodes_array.append(p2+1)
        nodes_array.append(p3+1)

    d = markupsNode2.GetDisplayNode()
    d.PointLabelsVisibilityOff()

    # converting node array to numpy array and then sacving to text file
    node_array_new = numpy.array(nodes_array)
    node_array_new = numpy.unique(node_array_new)
    np.savetxt(nodeFile,node_array_new, fmt="%s", delimiter=",")
    # Capture screenshot
    #if enableScreenshots:
    #  self.takeScreenshot('MeshNodesToFiducialsTest-Start','MyScreenshot',-1)

    logging.info('Processing completed')
    print("--- %s seconds ---" % (time.time() - start_time))
    return True


class MeshNodesToFiducialsTest(ScriptedLoadableModuleTest):
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
    self.test_MeshNodesToFiducials1()

  def test_MeshNodesToFiducials1(self):
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
    #
    # first, get some data
    #
    import SampleData
    SampleData.downloadFromURL(
      nodeNames='FA',
      fileNames='FA.nrrd',
      uris='http://slicer.kitware.com/midas3/download?items=5767',
      checksums='SHA256:12d17fba4f2e1f1a843f0757366f28c3f3e1a8bb38836f0de2a32bb1cd476560')
    self.delayDisplay('Finished with download and loading')

    volumeNode = slicer.util.getNode(pattern="FA")
    logic = MeshNodesToFiducialsLogic()
    self.assertIsNotNone( logic.hasImageData(volumeNode) )
    self.delayDisplay('Test passed!')
