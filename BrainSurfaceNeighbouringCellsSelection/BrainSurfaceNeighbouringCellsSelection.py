import os
import unittest
import logging
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin

#
# BrainSurfaceNeighbouringCellsSelection
#

class BrainSurfaceNeighbouringCellsSelection(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "BrainSurfaceNeighbouringCellsSelection"  # TODO: make this more human readable by adding spaces
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
# BrainSurfaceNeighbouringCellsSelectionWidget
#

class BrainSurfaceNeighbouringCellsSelectionWidget(ScriptedLoadableModuleWidget, VTKObservationMixin):
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
    uiWidget = slicer.util.loadUI(self.resourcePath('UI/BrainSurfaceNeighbouringCellsSelection.ui'))
    self.layout.addWidget(uiWidget)
    self.ui = slicer.util.childWidgetVariables(uiWidget)

    # Set scene in MRML widgets. Make sure that in Qt designer
    # "mrmlSceneChanged(vtkMRMLScene*)" signal in is connected to each MRML widget's.
    # "setMRMLScene(vtkMRMLScene*)" slot.
    uiWidget.setMRMLScene(slicer.mrmlScene)

    # Create a new parameterNode (it stores user's node and parameter values choices in the scene)
    self.logic = BrainSurfaceNeighbouringCellsSelectionLogic()
    self.ui.parameterNodeSelector.addAttribute("vtkMRMLScriptedModuleNode", "ModuleName", self.moduleName)
    self.setParameterNode(self.logic.getParameterNode())

    # Connections
    self.ui.parameterNodeSelector.connect('currentNodeChanged(vtkMRMLNode*)', self.setParameterNode)

    self.ui.inputSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
    #self.ui.outputSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
    self.ui.brainVolume.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)

    #self.ui.imageThresholdSliderWidget.connect("valueChanged(double)", self.updateParameterNodeFromGUI)
    #self.ui.invertOutputCheckBox.connect("toggled(bool)", self.updateParameterNodeFromGUI)
    self.ui.createFiducialsButton.connect('clicked(bool)', self.onApplyCreateFiducialsButton)

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
    self.ui.secondCollapsibleButton.enabled = self._parameterNode is not None

    #self.ui.advancedCollapsibleButton.enabled = self._parameterNode is not None
    if self._parameterNode is None:
      return

    # Update each widget from parameter node

    wasBlocked = self.ui.inputSelector.blockSignals(True)
    self.ui.inputSelector.setCurrentNode(self._parameterNode.GetNodeReference("InputVolume"))
    self.ui.inputSelector.blockSignals(wasBlocked)

    #wasBlocked = self.ui.outputSelector.blockSignals(True)
    #self.ui.outputSelector.setCurrentNode(self._parameterNode.GetNodeReference("OutputVolume"))
    #self.ui.outputSelector.blockSignals(wasBlocked)

    wasBlocked = self.ui.brainVolume.blockSignals(True)
    self.ui.brainVolume.setCurrentNode(self._parameterNode.GetNodeReference("InputModel"))
    self.ui.brainVolume.blockSignals(wasBlocked)
    #wasBlocked = self.ui.imageThresholdSliderWidget.blockSignals(True)
    #self.ui.imageThresholdSliderWidget.value = float(self._parameterNode.GetParameter("Threshold"))
    #self.ui.imageThresholdSliderWidget.blockSignals(wasBlocked)

    #wasBlocked = self.ui.invertOutputCheckBox.blockSignals(True)
    #self.ui.invertOutputCheckBox.checked = (self._parameterNode.GetParameter("Invert") == "true")
    #self.ui.invertOutputCheckBox.blockSignals(wasBlocked)

    # Update buttons states and tooltips
    if self._parameterNode.GetNodeReference("InputVolume"):
      self.ui.applyButton.toolTip = "Select Neighbouring cells on brain surface mesh"
      self.ui.applyButton.enabled = True
    else:
      self.ui.applyButton.toolTip = "Select input model node"
      self.ui.applyButton.enabled = False
      
    if self._parameterNode.GetNodeReference("InputModel"):
      self.ui.createFiducialsButton.toolTip = "create fiducials"
      self.ui.createFiducialsButton.enabled = True
    else:
      self.ui.createFiducialsButton.toolTip = "Select input model"
      self.ui.createFiducialsButton.enabled = False  

  def updateParameterNodeFromGUI(self, caller=None, event=None):
    """
    This method is called when the user makes changes in the GUI.
    The changes are saved into the parameter node (so that they are preserved when the scene is saved and loaded).
    """

    if self._parameterNode is None:
      return

    self._parameterNode.SetNodeReferenceID("InputVolume", self.ui.inputSelector.currentNodeID)
    #self._parameterNode.SetNodeReferenceID("OutputVolume", self.ui.outputSelector.currentNodeID)
    self._parameterNode.SetNodeReferenceID("InputModel", self.ui.brainVolume.currentNodeID)

    #self._parameterNode.SetParameter("Threshold", str(self.ui.imageThresholdSliderWidget.value))
    #self._parameterNode.SetParameter("Invert", "true" if self.ui.invertOutputCheckBox.checked else "false")

  def onApplyCreateFiducialsButton(self):
    """
    Run processing when user clicks "Apply" button.
    """
    try:
      self.logic.createFiducials(self.ui.brainVolume.currentNode(), self.ui.brainCells.currentPath, self.ui.disFile.currentPath)
    except Exception as e:
      slicer.util.errorDisplay("Failed to compute results: "+str(e))
      import traceback
      traceback.print_exc()
    
      
  def onApplyButton(self):
    """
    Run processing when user clicks "Apply" button.
    """
    try:
      self.logic.run(self.ui.inputSelector.currentNode(), self.ui.meshCellFile.currentPath, self.ui.allElectrodeCellsFile.currentPath)
    except Exception as e:
      slicer.util.errorDisplay("Failed to compute results: "+str(e))
      import traceback
      traceback.print_exc()


#
# BrainSurfaceNeighbouringCellsSelectionLogic
#

class BrainSurfaceNeighbouringCellsSelectionLogic(ScriptedLoadableModuleLogic):
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
  
  def createFiducials(self, inputmodel, cellFile, disFile):
    """
    Run the processing algorithm.
    Can be used without GUI widget.
    """

    if not inputmodel:
      raise ValueError("Input model is invalid")

    logging.info('Processing started')
    
    electrodePos1=[]
    f=open(cellFile,"r")
    for line in f:
        b=line.split(',')
        for n in b:
            print(n)
            electrodePos1.append(n)
    f.close()
    del electrodePos1[-1]
    electrodePosArray1 = [int(n) for n in electrodePos1]
    print(electrodePosArray1)
    #electrodePosArray1 = [5,6,7,20,21,22,26,28,29,44,45,46,61,62,69,77,78,79,80,81]
    #global electrodePosArray1
    #read the node and save the node to file in inp
    #electrodePosArray1 = [27 ,29 ,30 ,31 ,33 ,34 ,37 ,38 ,39 ,41 ,42 ,43 ,44 ,87 ,90 ,92 ,105 ,106 ,107 ,108 ,110 ,112 ,113 ,119 ,142 ,143 ,150 ,151 ,152 ,167 ,168 ,169 ,170 ,171 ,172 ,173 ,174 ,175 ,176 ,177 ,178 ,179 ,180 ,181 ,182 ,206 ,207 ,208 ,209 ,210 ,211 ,212 ,250 ,251 ,252 ,254 ,255 ,256 ,263 ,264 ,265 ,266 ,267 ,268 ,269 ,270 ,281 ,282 ,283 ,284 ,289 ,290 ,291 ,292 ,297 ,298 ,299 ,300 ,301 ,302 ,303 ,304 ,305 ,306 ,307 ,308 ,309 ,334 ,335 ,336 ,337 ,338 ,339 ,340 ,347 ,349 ,350 ,353 ,354 ,355 ,356 ,357 ,358 ,359 ,360 ,361 ,362 ,368 ,369 ,372 ,373 ,374 ,375 ,376 ,378 ,389 ,390 ,391 ,392 ,393 ,396 ,399 ,400 ,402 ,403 ,404 ,405 ,406 ,407 ,408 ,409 ,415 ,416 ,417 ,418 ,419 ,420 ,437 ,438 ,446 ,447 ,448 ,449 ,450 ,452 ,453 ,482 ,483 ,490 ,491 ,492 ,493 ,494 ,504 ,505 ,524 ,525 ,531 ,532 ,533 ,534 ,535 ,536 ,552 ,553 ,573 ,581 ,583 ,584 ,585 ,616 ,617 ,618 ,620 ,679 ,681 ,682 ,683 ,684 ,703 ,705 ,706 ,707 ,713 ,714 ,715 ,716 ,717 ,749 ,750 ,751 ,753 ,754 ,800 ,801 ,810 ,811 ,812 ,813 ,814 ,816 ,827 ,828 ,829 ,831 ,842 ,844 ,845 ,846 ,847 ,848 ,849 ,873 ,875 ,876 ,877 ,878 ,879 ,880 ,881 ,882 ,883 ,894 ,895 ,904 ,906 ,907 ,908 ,921 ,922 ,923 ,924 ,933 ,936 ,987 ,990 ,991 ,994 ,996 ,997 ,1033 ,1052 ,1103 ,1104 ,1105 ,1106 ,1123 ,1124 ,1126 ,1127 ,1171 ,1172 ,1173 ,1174 ,1176 ,1179 ,1181 ,1193 ,1194 ,1195 ,1196 ,1236 ,1237 ,1240 ,1256 ,1257 ,1258 ,1259 ,1260 ,1261 ,1264 ,1280 ,1282 ,1286 ,1287 ,1288 ,1289 ,1290 ,1291 ,1292 ,1293 ,1294 ,1295 ,1296 ,1297 ,1298 ,1299 ,1300 ,1328 ,1329 ,1330 ,1331 ,1332 ,1333 ,1336 ,1337 ,1338 ,1339 ,1340 ,1341 ,1343 ,1344 ,1345 ,1346 ,1362 ,1363 ,1364 ,1365 ,1371 ,1372 ,1373 ,1374 ,1375 ,1376 ,1397 ,1398 ,1400 ,1401 ,1403 ,1404 ,1405 ,1406 ,1408 ,1409 ,1410 ,1411 ,1444 ,1445 ,1446 ,1447 ,1448 ,1449 ,1450 ,1451 ,1452 ,1454 ,1457 ,1463 ,1469 ,1470 ,1471 ,1472 ,1485 ,1486 ,1488 ,1491 ,1492 ,1493 ,1494 ,1498 ,1499 ,1500 ,1501 ,1507 ,1508 ,1511 ,1512 ,1513 ,1514 ,1515 ,1527 ,1528 ,1529 ,1530 ,1531 ,1532 ,1533 ,1535 ,1536 ,1537 ,1542 ,1548 ,1551 ,1552 ,1553 ,1559 ,1571 ,1572 ,1587 ,1588 ,1589 ,1590 ,1611 ,1612 ,1618 ,1619 ,1625 ,1638 ,1639 ,1640 ,1642 ,1643 ,1645 ,1680 ,1681 ,1683 ,1689 ,1708 ,1714 ,1715 ,1716 ,1717 ,1754 ,1755 ,1756 ,1757 ,1758 ,1759 ,1782 ,1800 ,1802 ,1803 ,1824 ,1863 ,1864 ,1865 ,1866 ,1867 ,1868 ,1869 ,1870 ,1873 ,1874 ,1875 ,1877 ,1878 ,1897 ,1898 ,1899 ,1901 ,1902 ,1909 ,1910 ,1911 ,1912 ,1913 ,1914 ,1915 ,1916 ,1917 ,1927 ,1928 ,1929 ,1930 ,1951 ,1952 ,1956 ,1957 ,1966 ,1967 ,1968 ,1969 ,1970 ,1974 ,1975 ,1992 ,1993 ,1994 ,2023 ,2024 ,2025 ,2026 ,2044 ,2045 ,2046 ,2047 ,2048 ,2049 ,2050 ,2099 ,2100 ,2124 ,2125 ,2127 ,2160 ,2161 ,2162 ,2163 ,2164 ,2165 ,2167 ,2197 ,2199 ,2200 ,2201 ,2234 ,2235 ,2236 ,2237 ,2238 ,2297 ,2298 ,2299 ,2347 ,2362 ,2363 ,2364 ,2432 ,2445 ,2446 ,2447 ,2461 ,2463 ,2464 ,2468 ,2469 ,2480 ,2481 ,2482 ,2483 ,2493 ,2503 ,2504 ,2518 ,2521 ,2522 ,2523 ,2533 ,2534 ,2540 ,2541 ,2542 ,2543 ,2544 ,2567 ,2568 ,2589 ,2590 ,2591 ,2592 ,2627 ,2628 ,2673 ,2674 ,2721 ,2723 ,2724 ,2726 ,2727 ,2762 ,2763 ,2765 ,2786 ,2802 ,2803 ,2814 ,2815 ,2816 ,2828 ,2829 ,2840 ,2853 ,2854 ,2881 ,2882 ,2913 ,2914 ,2924 ,2950 ,2953 ,2965 ,2967 ,2968 ,2985 ,2986 ,2988 ,2989 ,2990 ,2991 ,3000 ,3001 ,3002 ,3003 ,3006 ,3007 ,3008 ,3009 ,3010 ,3011 ,3012 ,3013 ,3019 ,3020 ,3022 ,3023 ,3024 ,3025 ,3027 ,3029 ,3031 ,3056 ,3057 ,3060 ,3061 ,3070 ,3071 ,3083 ,3084 ,3085 ,3086 ,3112 ,3113 ,3191 ,3192 ,3193 ,3198 ,3199 ,3201 ,3202 ,3204 ,3206 ,3209 ,3211 ,3239 ,3240 ,3241 ,3242 ,3243 ,3244 ,3283 ,3284 ,3285 ,3286 ,3306 ,3307 ,3316 ,3318 ,3320 ,3321 ,3322 ,3341 ,3342 ,3343 ,3344 ,3345 ,3347 ,3365 ,3366 ,3367 ,3368 ,3369 ,3370 ,3371 ,3378 ,3379 ,3386 ,3387 ,3388 ,3391 ,3407 ,3408 ,3409 ,3425 ,3426 ,3427 ,3438 ,3439 ,3440 ,3441 ,3461 ,3477 ,3478 ,3479 ,3503 ,3504 ,3505 ,3506 ,3508 ,3509 ,3576 ,3577 ,3602 ,3610 ,3611 ,3625 ,3672 ,3708 ,3709 ,3710 ,3734 ,3735 ,3736 ,3754 ,3755 ,3760 ,3761 ,3762 ,3763 ,3764 ,3776 ,3778 ,3779 ,3780 ,3781 ,3782 ,3789 ,3790 ,3795 ,3827 ,3828 ,3917 ,3918 ,3919 ,3920 ,3921 ,3925 ,3926 ,3927 ,3930 ,3938 ,3946 ,3947 ,3953 ,3954 ,3963 ,3971 ,3972 ,3974 ,3975 ,3980 ,3981 ,3982 ,3983 ,3985 ,3986 ,3987 ,3989 ,3990 ,3991 ,3995]
    import time
    start_time = time.time()
    print(electrodePosArray1)
    electrodePosArray1 = [i+1 for i in electrodePosArray1]
    #print(electrodePosArray1)
    node = slicer.util.getNode(inputmodel.GetID())
    #mesh = node.GetMesh().GetCellData()
    #properties = {'useCompression': 0}; #do not compress
    #file_name = "surfaceModel.stl"
    #file_path = os.path.join(mydir, file_name)
    import time
    start_time = time.time()
    dir_path = os.path.dirname(os.path.realpath(__file__))
    file_path ="/home/saima/volumeMesh.vtk" 
    slicer.util.saveNode(node, dir_path+"/volumeMesh.vtk")    
    
    import meshio
    mesh = meshio.read(dir_path+"/volumeMesh.vtk")
    meshio.write(dir_path+"/volumeMesh.inp", mesh)
    
    #reading the inp file to extract nodes for the seleted cells
    f = open(dir_path+"/volumeMesh.inp","r")
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
    f.close()

    print(lastNode)
    import numpy as np
    nodes_unique = np.unique(nodes)
    nodes_unique.sort()
    print(nodes_unique) 
    o = open(disFile,"w+") 
    for i in range(len(nodes_unique)):
        o.write(str(nodes_unique[i]))
        o.write(",")
        
    o.close()
    print(nodes_unique)
    

    """f = open("/home/saima/surface_nodes.txt",'w+')
    i = 1
    for i in range(int(lastNode[0])+1):
        if(i not in nodes_unique):
         #print(i,end=',')
         f.write(str(i))
         f.write(",")
        
    f.close()  """
    
    #searching for nodes in the file for x y z
    #nodes_unique = [i - 1 for i in nodes_unique]
    #nodes_unique = [i for i in nodes_unique]
    markupsNode3 = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsFiducialNode")
    markupsNode3.CreateDefaultDisplayNodes()
    #fiducialArray = []
    #reading file until s3 elements to get all the nodes only
    f = open(dir_path+"/volumeMesh.inp","r")
    print(dir_path)
    f_new = open(dir_path+"/electrodeLocations.txt",'w+')
    while True:
        l = f.readline()
        print(l)
        if("NODE" in l or "Node" in l):
            continue
        if("HEADING" in l or "Heading" in l):
            print("inside heading")
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
            #print(s1)
            if(s1 in nodes_unique):
                s2 = float(s[1])
                s3 = float(s[2])
                s4 = float(s[3])
                f_new.write(str(s1))
                f_new.write(',')
                f_new.write(str(s2))
                f_new.write(',')
                f_new.write(str(s3))
                f_new.write(',')
                f_new.write(str(s4))
                f_new.write("\n")
                print(s1,',',s2,',',s3,',',s4)
                markupsNode3.AddFiducial(-s2,-s3,s4,str(s1))
                #markupsNode3.AddFiducial(-s2,-s3,s4,str(s1))
                #fiducialArray.append(s1,s2,s3,s4)
     
    f.close()  
    f_new.close()
    d = markupsNode3.GetDisplayNode()
    d.PointLabelsVisibilityOff()  
           
    #for j in range(len(nodes_unique)):
    print("--- %s seconds ---" % (time.time() - start_time))
    return True    



      
  def run(self, inputVolume, meshCellFile, allElectrodeCellsFile):
    """
    Run the processing algorithm.
    Can be used without GUI widget.
    """

    if not inputVolume:
      raise ValueError("Input volume is invalid")

    logging.info('Processing started')

    # Compute the thresholded output volume using the Threshold Scalar Volume CLI module
    """cliParams = {
      'InputVolume': inputVolume.GetID(),
      'OutputVolume': outputVolume.GetID(),
      'ThresholdValue' : imageThreshold,
      'ThresholdType' : 'Below' if invert else 'Above'
      }
    cliNode = slicer.cli.run(slicer.modules.thresholdscalarvolume, None, cliParams, wait_for_completion=True)"""
    electrodePos1=[]
    f=open(meshCellFile,"r")
    for line in f:
        b=line.split(',')
        for n in b:
            print(n)
            electrodePos1.append(n)
    
    del electrodePos1[-1] #remove last element of array which is empty
    electrodePos = [int(n) for n in electrodePos1]
    print(electrodePos)
    
    #electrodePos = [9338, 19575, 14647, 18007, 16394, 12795, 22412, 23777, 24113, 6229, 8064, 5777, 23120, 12895, 9652, 9437, 14295, 7741, 23801, 18897, 21348, 1510, 3389, 3390, 874, 21434, 18638, 4139, 15455, 22897, 3342, 3322, 23290, 10204, 7614, 4047, 6004, 19068, 23253, 15729, 5864, 4026, 4073, 9265, 19206, 20071, 4448, 23504, 24189, 14432, 9874, 18070, 22952, 12396, 5614, 23342, 18118, 19254, 4451, 17856, 20649, 20708, 19856, 6968, 11892, 7853, 16309, 23504, 15738, 15340, 11618, 4293, 11996, 7721, 16839, 14063, 11254, 15588, 6173, 8610, 7853, 20624, 10774, 4632, 18834, 22152, 19628, 20137, 6462, 24030, 13023, 7604, 24043, 18348, 4060, 17127, 18062, 8607, 5362, 20796, 6875, 19588, 11183, 5128, 18401, 22011, 532, 23280]
    #electrodePos = [2951, 2764, 3032, 401, 3760, 3083, 1373, 3028, 3030, 3203, 3205, 1262, 3778, 1402, 1342, 1285, 1301, 3287, 1682, 1641, 3973, 1510, 3389, 3390, 874, 1180, 1916, 1913, 3955, 3931, 3342, 3322, 815, 843, 937, 1931, 920, 893, 707, 389, 333, 1534, 3012, 1956, 2856, 40, 39, 91, 253, 1620, 2166, 2233, 1863, 1867, 2045, 2049, 109, 3427, 1899, 1443, 1869, 2026, 2541, 2627, 210, 270, 3478, 91, 1757, 2023, 2541, 2589, 309, 402, 492, 680, 1493, 1995, 1909, 3478, 269, 263, 292, 2589, 1531, 2363, 1928, 3480, 1328, 302, 305, 362, 376, 3790, 3507, 1175, 619, 403, 402, 536, 374, 180, 166, 1125, 1107, 582, 532, 754]
    modelNode = slicer.util.getNode(inputVolume.GetID())
    m = modelNode.GetMesh()
    
    print(m)
    neigborCells = []
    cellPointIdArray = []
    GeomFilt2 = vtk.vtkGeometryFilter()
    GeomFilt2.SetInputData(m)
    GeomFilt2.Update()
    y = GeomFilt2.GetOutput()
    print(y)
    
    mm = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLModelNode")
    mm.SetAndObservePolyData(y)
    #slicer.util.loadModel(m)
    
    for e in range(len(electrodePos)):
        
      trianglefilter = vtk.vtkTriangleFilter()
    
      trianglefilter.SetInputData(y)
      trianglefilter.Update()
    
      cellPointIds = vtk.vtkIdList()
    
      trianglefilter.GetOutput().GetCellPoints(electrodePos[e], cellPointIds)
    
      for i in range(0,3):
          print(cellPointIds.GetId(i))
          cellPointIdArray.append(cellPointIds.GetId(i))
        
      neighbourcells = vtk.vtkIdList()
      neighbors = vtk.vtkIdTypeArray()
      for i in range(0,cellPointIds.GetNumberOfIds()):
   
        idList = vtk.vtkIdList()
        idList.InsertNextId(cellPointIds.GetId(i));

        #get the neighbors of the cell
        neighborCellIds = vtk.vtkIdList()

        trianglefilter.GetOutput().GetCellNeighbors(electrodePos[e], idList,
                                                  neighborCellIds);
        print(neighborCellIds.GetNumberOfIds())
        for j in range(0,neighborCellIds.GetNumberOfIds()):
            print(neighborCellIds.GetId(j))
            neigborCells.append(neighborCellIds.GetId(j))

        #self.colorNeighbors()
    print("nodes with each cell")
    print(cellPointIdArray)
    print("number of nodes")
    print(len(cellPointIdArray))
    print("Number of neighbouring cells")
    print(len(neigborCells))
    import numpy as np
    n = np.array(neigborCells)
    uni = np.unique(n)
    n_new_neighbourcells = np.array(uni)
    print("Number of unique neigbhouring mesh cells")
    print(n_new_neighbourcells)
    #for s in range(len(n_new_neighbourcells)):
     #print(n_new_neighbourcells[s])
    fff=open(allElectrodeCellsFile,"w+")
    i=0
    for x in uni:
        fff.write(str(uni[i]))
        fff.write(',')
        print(uni[i])
        i=i+1
    fff.close()    
    #electrodePosArray = np.array(electrodePos)
    #n_concatenate = np.concatenate((n_new_neighbourcells, electrodePosArray))   
    #print(uni[0])
    
    cellScalars = mm.GetMesh().GetCellData()
    selectionArray = cellScalars.GetArray('selection')
    if not selectionArray:
      selectionArray = vtk.vtkIntArray()
      selectionArray.SetName('selection')
      selectionArray.SetNumberOfValues(mm.GetMesh().GetNumberOfCells())
      selectionArray.Fill(0)
      cellScalars.AddArray(selectionArray)
    #idList = vtk.vtkIdList()
    #idList.SetNumberOfIds(3)
    #idList.SetId(0,1552)
    for nCels in range(len(uni)):
      selectionArray.SetValue(uni[nCels], 100)


    """markupsNode2 = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsFiducialNode")
    markupsNode2.CreateDefaultDisplayNodes()
    mesh = modelNode2.GetMesh()
    print("nodes within slicer")
    for i in range(len(uni)):
        
        cell = mesh.GetCell(int(uni[i]))
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
        print(p1,',',a1[0],',',a1[1],',',a1[2])
        print(p2,',',a2[0],',',a2[1],',',a2[2])
        print(p3,',',a3[0],',',a3[1],',',a3[2])

        markupsNode2.AddFiducial(a1[0],a1[1],a1[2])
        markupsNode2.AddFiducial(a2[0],a2[1],a2[2])
        markupsNode2.AddFiducial(a3[0],a3[1],a3[2])
    
    d = markupsNode2.GetDisplayNode()
    d.PointLabelsVisibilityOff()"""
    logging.info('Processing completed')

#
# BrainSurfaceNeighbouringCellsSelectionTest
#

class BrainSurfaceNeighbouringCellsSelectionTest(ScriptedLoadableModuleTest):
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
    self.test_BrainSurfaceNeighbouringCellsSelection1()

  def test_BrainSurfaceNeighbouringCellsSelection1(self):
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

    logic = BrainSurfaceNeighbouringCellsSelectionLogic()

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
