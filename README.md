# SlicerCBM

*Computational Biophysics for Medicine in 3D Slicer*

[SlicerCBM](https://github.com/SlicerCBM/SlicerCBM)
is an extension for
[3D Slicer](http://slicer.org)
that provides tools for creating and solving
computational models of biophysical systems and processes
with a focus on clinical and biomedical applications.

SlicerCBM is under development at the
[Intelligent Systems for Medicine Lab](https://isml.ecm.uwa.edu.au)
at
[The University of Western Australia](https://www.uwa.edu.au).

## Features

The SlicerCBM extension currently includes the following features implemented as 3D Slicer modules:

- Segmentation
  - DTISegmentation: segment DTI into gray matter (GM), white matter (WM) and cerebrospinal fluid (CSF) tissue classes using fuzzy C-means clustering (FCM) algorithm
  - Fusion
  - Fusion2

- Geometry
  - CranCreator
  - FiducialsToSurface
  - MeshNodesToFiducials
  - SheetFromPoints
  - SkullGenerator
  - SurfaceTriangulation

- Mesh/Grid
  - MVoxMeshGenerator: create structured hexahedral grid using MVox
  - TetrahedralMeshGenerator: create tetrahedral grid using Gmsh
  - TumorResectionAndBRainRemodelling: create tetrahedral grid of brain with tumor cavity using Gmsh

- Property
  - BrainMaterialProperties
  - ElectricalConductivity: assign electrical conductivity to an image volume
  - FuzzyClassification

- BCs/Load
  - BrainMeshSurfaceCellsSelection
  - BrainSurfaceNeighbouringCellsSelection
  - ElectrodesToMarkups
  - FiducialToModelDistance
  - NodeSelector

- Solver
  - EEGSolver
  - MTLEDSimulator

- Visualization
  - Visualisation

## External software

SlicerCBM depends on the following software:

- [ExplicitSim](https://bitbucket.org/explicitsim/explicitsim) (GPL)
- [Gmsh](https://gmsh.info) (GPL)
- [MVox Mesh Voxelizer](https://github.com/benzwick/mvox) (BSD-3-Clause license)
- [PyACVD](https://github.com/pyvista/pyacvd) (MIT license)
- [scikit-fuzzy Fuzzy Logic SciKit (Toolkit for SciPy)](https://github.com/scikit-fuzzy/scikit-fuzzy)

## Contributing

Pull requests are welcome.
For major changes,
please open an issue first to discuss what you would like to change.


<a href="https://isml.ecm.uwa.edu.au"><img src="ISML.gif" alt="ISML Logo" style="width:190px;height:190px;"></a>
