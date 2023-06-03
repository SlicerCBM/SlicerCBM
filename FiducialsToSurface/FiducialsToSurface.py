import os
import unittest
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging
import numpy as np
#import pyvista as pv
#import pyacvd
#
# FiducialsToSurface
#

class FiducialsToSurface(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "Fiducials To Surface"
    self.parent.categories = ["CBM.Surface Models"]
    self.parent.dependencies = []
    self.parent.contributors = ["Saima Safdar"] # replace with "Firstname Lastname (Organization)"
    self.parent.helpText = """
This is an example of scripted loadable module bundled in an extension.
It creates a surface utilising fiducials as cloud of points.
"""
    self.parent.helpText += self.getDefaultModuleDocumentationLink()
    self.parent.acknowledgementText = """
""" # replace with organization, grant and thanks.

#
# FiducialsToSurfaceWidget
#

class FiducialsToSurfaceWidget(ScriptedLoadableModuleWidget):
  """Uses ScriptedLoadableModuleWidget base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setup(self):
    ScriptedLoadableModuleWidget.setup(self)

    # Load widget from .ui file (created by Qt Designer)
    uiWidget = slicer.util.loadUI(self.resourcePath('UI/FiducialsToSurface.ui'))
    self.layout.addWidget(uiWidget)
    self.ui = slicer.util.childWidgetVariables(uiWidget)

    self.ui.inputSelector.setMRMLScene(slicer.mrmlScene)
    self.ui.outputSelector.setMRMLScene(slicer.mrmlScene)

    # connections
    self.ui.applyButton.connect('clicked(bool)', self.onApplyButton)
    self.ui.inputSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)
    self.ui.outputSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)

    # Add vertical spacer
    self.layout.addStretch(1)

    # Refresh Apply button state
    self.onSelect()

  def cleanup(self):
    pass

  def onSelect(self):
    self.ui.applyButton.enabled = self.ui.inputSelector.currentNode() and self.ui.outputSelector.currentNode()

  def onApplyButton(self):
    try:
       import pyacvd
       import pyvista as pv
    except ModuleNotFoundError as e:
        if slicer.util.confirmOkCancelDisplay("This module requires 'pyacvd, pyvista' Python package. Click OK to install."):
            slicer.util.pip_install("pyacvd")
            slicer.util.pip_install("pyvista")
            #import tensorflow
            import pyacvd
            import pyvista as pv


    logic = FiducialsToSurfaceLogic()
    enableScreenshotsFlag = self.ui.enableScreenshotsFlagCheckBox.checked
    try:
      logic.run(self.ui.inputSelector.currentNode(), self.ui.outputSelector.currentNode(), enableScreenshotsFlag)
    except Exception as e:
      slicer.util.errorDisplay("Failed to compute results: "+str(e))
      import traceback
      traceback.print_exc()

#
# FiducialsToSurfaceLogic
#

class FiducialsToSurfaceLogic(ScriptedLoadableModuleLogic):
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

  def run(self, inputFiducial, outputModel, enableScreenshots=0):
    """
    Run the actual algorithm
    """

    if not self.isValidInputOutputData(inputFiducial, outputModel):
      slicer.util.errorDisplay('Input Fiducial is the same as output model. Choose a different output volume.')
      return False

    logging.info('Processing started')

    # Compute the thresholded output volume using the Threshold Scalar Volume CLI module
    markupsNode = slicer.util.getNode(inputFiducial.GetID())
    markupsIndex = 0
    n = markupsNode.GetNumberOfFiducials()
    modelNode = slicer.util.getNode(outputModel.GetID())

    ar = []
    print(n)
    for j in range(n):
        point_Ras = [0, 0, 0, 1]
        markupsNode.GetNthFiducialWorldCoordinates(markupsIndex, point_Ras)
        ar.append(point_Ras[0:3])
        markupsIndex = markupsIndex+1

    ar2 = np.array(ar)
    print(ar2)
    print(ar2.shape)

    cloud = pv.PolyData(ar2)
    surf = cloud.delaunay_2d(alpha = 0.0, offset=-5.0)
    newMesh1 = surf.compute_normals()
    cpos = newMesh1.plot()


    outputModel.SetAndObservePolyData(newMesh1)


    # Capture screenshot
    if enableScreenshots:
      self.takeScreenshot('FiducialsToSurfaceTest-Start','MyScreenshot',-1)

    logging.info('Processing completed')

    return True


class FiducialsToSurfaceTest(ScriptedLoadableModuleTest):
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
    self.test_FiducialsToSurface1()

  def test_FiducialsToSurface1(self):
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
    logic = FiducialsToSurfaceLogic()
    self.assertIsNotNone( logic.hasImageData(volumeNode) )
    self.delayDisplay('Test passed!')
