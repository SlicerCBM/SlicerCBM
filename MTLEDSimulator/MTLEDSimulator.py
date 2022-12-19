import os
import unittest
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging

#
# MTLEDSimulator
#

class MTLEDSimulator(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "MTLEDSimulator" # TODO make this more human readable by adding spaces
    self.parent.categories = ["CBM.Biomechanical.Solver"]
    self.parent.dependencies = []
    self.parent.contributors = ["saima safdar"] # replace with "Firstname Lastname (Organization)"
    self.parent.helpText = """
This is an example of scripted loadable module bundled in an extension.
It performs a simple thresholding on the input volume and optionally captures a screenshot.
"""
    self.parent.helpText += self.getDefaultModuleDocumentationLink()
    self.parent.acknowledgementText = """
This file was originally developed by Jean-Christophe Fillion-Robin, Kitware Inc.
and Steve Pieper, Isomics, Inc. and was partially funded by NIH grant 3P41RR013218-12S1.
""" # replace with organization, grant and thanks.

#
# MTLEDSimulatorWidget
#

class MTLEDSimulatorWidget(ScriptedLoadableModuleWidget):
  """Uses ScriptedLoadableModuleWidget base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setup(self):
    ScriptedLoadableModuleWidget.setup(self)

    # Load widget from .ui file (created by Qt Designer)
    uiWidget = slicer.util.loadUI(self.resourcePath('UI/MTLEDSimulator.ui'))
    self.layout.addWidget(uiWidget)
    self.ui = slicer.util.childWidgetVariables(uiWidget)

    #self.ui.Model
    #self.ui.pathLineEdit.setCurrentPath(ctk.ctkPathLineEdit.Dirs)
    
    #parametersCollapsibleButton = ctk.ctkCollapsibleButton()
    #parametersCollapsibleButton.text = "Model"
    #self.layout.addWidget(parametersCollapsibleButton)
    
    #parametersFormLayout = qt.QFormLayout(parametersCollapsibleButton)
    #self.inputDirSelector = ctk.ctkPathLineEdit()
    #self.inputDirSelector.filters = ctk.ctkPathLineEdit.Dirs
    #self.inputDirSelector.settingKey = 'DICOMPatcherInputDir'
    #parametersFormLayout.addRow("Input mesh file:", self.inputDirSelector)
    
    
    #second collapsible
    #parametersCollapsibleButton2 = ctk.ctkCollapsibleButton()
    #parametersCollapsibleButton2.text = "Integration Points"
    #self.layout.addWidget(parametersCollapsibleButton2)
    
    #parametersFormLayout = qt.QFormLayout(parametersCollapsibleButton2)
    #self.inputDirSelector2 = ctk.ctkPathLineEdit()
    #self.inputDirSelector2.filters = ctk.ctkPathLineEdit.Dirs
    #self.inputDirSelector2.settingKey = 'DICOMPatcherInputDir'
    #parametersFormLayout.addRow("Input integration points file:", self.inputDirSelector2)
    
    
    
    #3rd collapsible button
    #parametersCollapsibleButton3 = ctk.ctkCollapsibleButton()
    #parametersCollapsibleButton3.text = "Materials"
    #self.layout.addWidget(parametersCollapsibleButton3)
    
    #parametersFormLayout = qt.QFormLayout(parametersCollapsibleButton3)
    #self.inputDirSelector4 = ctk.ctkPathLineEdit()
    #self.inputDirSelector4.filters = ctk.ctkPathLineEdit.Dirs
    #self.inputDirSelector4.settingKey = 'DICOMPatcherInputDir'
    #parametersFormLayout.addRow("Input material properties file:", self.inputDirSelector4)
    
    #4th button
    #parametersCollapsibleButton4 = ctk.ctkCollapsibleButton()
    #parametersCollapsibleButton4.text = "Shape function"
    #self.layout.addWidget(parametersCollapsibleButton4)
    
    #parametersFormLayout = qt.QFormLayout(parametersCollapsibleButton4)

    #loadReferencesComboBox = ctk.ctkComboBox()
    #loadReferencesComboBox.toolTip = "Determines whether referenced DICOM series are " \
      #"offered when loading DICOM, or the automatic behavior if interaction is disabled. " \
     # "Interactive selection of referenced series is the default selection"
    #loadReferencesComboBox.addItem("Ask user", qt.QMessageBox.InvalidRole)
    #loadReferencesComboBox.addItem("Always", qt.QMessageBox.Yes)
    #loadReferencesComboBox.addItem("Never", qt.QMessageBox.No)
    #loadReferencesComboBox.currentIndex = 0
    #parametersFormLayout.addRow("Load referenced series:", loadReferencesComboBox)
    
    #5th button
    #parametersCollapsibleButton5 = ctk.ctkCollapsibleButton()
    #parametersCollapsibleButton5.text = "Loading"
    #self.layout.addWidget(parametersCollapsibleButton5)
    
    #6th
    #parametersCollapsibleButton6 = ctk.ctkCollapsibleButton()
    #parametersCollapsibleButton6.text = "Contacts"
    #self.layout.addWidget(parametersCollapsibleButton6)
    
    #7th
    #parametersCollapsibleButton7 = ctk.ctkCollapsibleButton()
    #parametersCollapsibleButton7.text = "Dynamic relaxation"
    #self.layout.addWidget(parametersCollapsibleButton7)
    
    #8th
    #parametersCollapsibleButton8 = ctk.ctkCollapsibleButton()
    #parametersCollapsibleButton8.text = "Output"
    #self.layout.addWidget(parametersCollapsibleButton8)
    
    
    self.ui.inputSelector.setMRMLScene(slicer.mrmlScene)
    self.ui.outputSelector.setMRMLScene(slicer.mrmlScene)
    self.ui.applyButton.enabled =True
    # connections
    self.ui.applyButton.connect('clicked(bool)', self.onApplyButton)
    #self.ui.inputSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)
    #self.ui.outputSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)

    # Add vertical spacer
    self.layout.addStretch(1)

    # Refresh Apply button state
    #self.onSelect()

  def cleanup(self):
    pass

  #def onSelect(self):
    #self.ui.applyButton.enabled = self.ui.inputSelector.currentNode() and self.ui.outputSelector.currentNode()

  def onApplyButton(self):
    logic = MTLEDSimulatorLogic()
    enableScreenshotsFlag = self.ui.enableScreenshotsFlagCheckBox.checked
    imageThreshold = self.ui.imageThresholdSliderWidget.value
    
    #Model
    meshFile = self.ui.meshFile.currentPath
    mass_scaling = self.ui.massscaling.currentText
    #integration options
    adap = self.ui.adaptive.currentText
    adaptive_eps = self.ui.adaptiveEps.value
    adap_level = self.ui.adaptiveLevel.value
    tDivision = self.ui.tDevision.value
    iTetra = self.ui.iTetra.value
    intFile = self.ui.intFile.currentPath
    
    #materials
    mFile = self.ui.mFile.currentPath
    
    #shape function
    tFunction = self.ui.type.currentText
    bFunction = self.ui.bFunction.currentText
    uDerivative = self.ui.uDerivative.currentText
    dilationCoefficient = self.ui.dilationCoefficient.value
    #loading
    lFile = self.ui.lFile.currentPath
    loadCurve = self.ui.loadCurve.currentText
    
    #contacts
    contact = self.ui.contact.text
    skull = self.ui.skull.text
    
    #dynamic relaxation
    loadIntegration = self.ui.loadIntegration.value
    loadRunning = self.ui.loadRunning.value
    eTime = self.ui.eTime.value
    
    #outputfiles
    dButton = self.ui.sPath.currentPath
    
    logic.run(self.ui.inputSelector.currentNode(), self.ui.outputSelector.currentNode(), imageThreshold, meshFile, mass_scaling,adap, adaptive_eps, adap_level, tDivision, iTetra,intFile, mFile, tFunction,bFunction, uDerivative, dilationCoefficient, lFile, loadCurve, contact, skull,loadIntegration, loadRunning, eTime, dButton, enableScreenshotsFlag)

#
# MTLEDSimulatorLogic
#

class MTLEDSimulatorLogic(ScriptedLoadableModuleLogic):
  """This class should implement all the actual
  computation done by your module.  The interface
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget.
  Uses ScriptedLoadableModuleLogic base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

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

  def run(self, inputVolume, outputVolume, imageThreshold, meshFile, mass_scaling,adap, adaptive_eps, adap_level, tDivision, intPerTetra, intFile, mFile, tFunction, bFunction, uDerivative, dilationCoefficient, lFile, loadCurve, contact, skull, loadIntegration, loadRunning, eTime,dButton, enableScreenshots=0):
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
   
    print(meshFile, mass_scaling)
    print(adap)
    print(adaptive_eps)
    print(adap_level)
    print(tDivision)
    print(intPerTetra)
    print(tFunction)
    print(bFunction, uDerivative, dilationCoefficient, loadCurve, contact, skull, loadIntegration, loadRunning, eTime)
    print(dButton)
    print(mFile, intFile, lFile)
    
    #writing the information to ini file
    import os
    dir_path = os.path.dirname(os.path.realpath(__file__))
    print(dir_path)
    file = open(dir_path+"/demo.ini",'w+')
    
    file.write("[Model]\n")
    file.write("MeshFile = "+meshFile+"\n")
    file.write("MassScaling = "+mass_scaling+"\n")
    file.write("[IntegrationOptions]\n")
    file.write("Adaptive = "+adap+"\n")
    file.write("AdaptiveEps = "+str(adaptive_eps)+"\n")
    file.write("AdaptiveLevel = "+str(int(adap_level))+"\n")
    file.write("TetrahedronDivisions ="+str(int(tDivision))+"\n")
    file.write("IntegPointsPerTetrahedron ="+str(int(intPerTetra))+"\n")
    if intFile:
        file.write("SaveToFile ="+intFile+"\n")
    file.write("[Material]"+"\n")
    file.write("ReadFromFile ="+mFile+"\n")
    
    file.write("[ShapeFunction]"+"\n")
    file.write("Type = "+tFunction+"\n")
    file.write("BasisFunctionType = "+bFunction+"\n")
    file.write("UseExactDerivatives ="+uDerivative+"\n")
    file.write("DilatationCoefficient = "+str(dilationCoefficient)+"\n")
    
    file.write("[Boundary]  "+"\n")
    file.write("[Loading]"+"\n")
    file.write("ReadFromFile ="+lFile+"\n")
    file.write("FileLoadCurve = "+loadCurve+"\n")
    
    file.write("[Contacts]"+"\n")
    file.write("NodeSet = "+contact+"\n")
    file.write("Surface = "+skull +"\n")
    
    file.write("[EBCIEM]"+"\n")
    file.write("UseEBCIEM = false"+"\n")
    file.write("UseSimplifiedVersion = false"+"\n")
    
    file.write("[DynamicRelaxation]"+"\n")
    if loadIntegration==0.0:
        file.write("LoadTime = "+str(loadRunning)+"\n")
    else:
        file.write("LoadTime = "+str(loadIntegration)+"\n")
    file.write("EquilibriumTime ="+str(int(eTime))+"\n")
    
    file.write("LoadConvRate = 0.999"+"\n")
    file.write("AfterLoadConvRate = 0.99"+"\n")
    file.write("StopUpdateConvRateStepsNum = 2000"+"\n")
    file.write("ConvRateDeviation = 0.0001"+"\n")
    file.write("ForceDispUpdateStepsNum = 200"+"\n")
    file.write("StableConvRateStepsNum = 20"+"\n")
    file.write("ConvRateStopDeviation = 0.002"+"\n")
    file.write("StopConvRateError = 0.2"+"\n")
    file.write("StopAbsError = 0.00001"+"\n")
    file.write("StopStepsNum = 100"+"\n")
    
    file.write("[MTLED]"+"\n")
    file.write("SaveProgressSteps = 500"+"\n")
    file.write("UsePredefinedStableTimeStep = true "+"\n")
    file.write("StableTimeStep = 0.001"+"\n")
    
    file.write("[Output]"+"\n")
    file.write("FilePath ="+dir_path+"/results"+"\n")
    file.write("FileName = brain.vtu"+"\n")
    file.write("AnimationName = animation_brain.pvd"+"\n")
    file.close()
    
  
    file_mtledSimulator = dButton
    command_line = ["/home/saima/explicitsim/build-bucketsearch/ExplicitSimRun", dir_path+"/demo.ini"]
    
    from subprocess import Popen
    import subprocess
    import sys
    result = subprocess.Popen(command_line, stdout=subprocess.PIPE, stderr = subprocess.PIPE,  env=slicer.util.startupEnvironment())
    stdout, stderr = result.communicate()
    print(stdout, stderr)
    print(result)
    
    #file = "/home/saima/benzwick-explicitsim-f7f515ec1301/build/Saima/brain_withmaterial_results/brain2.vtu"
    #import meshio
    #mesh = meshio.read(file)
    #meshio.write(r"home/saima/benzwick-explicitsim-f7f515ec1301/build/Saima/brain_withmaterial_results/brain2.vtk", mesh)
    
    #model = slicer.util.loadModel(dir_path+"/results/brain)
    
    
    
    # Capture screenshot
    if enableScreenshots:
      self.takeScreenshot('MTLEDSimulatorTest-Start','MyScreenshot',-1)

    logging.info('Processing completed')

    return True


class MTLEDSimulatorTest(ScriptedLoadableModuleTest):
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
    self.test_MTLEDSimulator1()

  def test_MTLEDSimulator1(self):
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
    logic = MTLEDSimulatorLogic()
    self.assertIsNotNone( logic.hasImageData(volumeNode) )
    self.delayDisplay('Test passed!')
