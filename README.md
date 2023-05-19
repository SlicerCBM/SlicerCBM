# SlicerCBM

*Computational Biophysics for Medicine in 3D Slicer*

[SlicerCBM](https://github.com/SlicerCBM/SlicerCBM)
is an extension for
[3D Slicer](http://slicer.org)
that provides tools for creating and solving
computational models of biophysical systems and processes
with a focus on clinical and biomedical applications.
Features include grid generation, assignment of material properties and boundary conditions, and solvers for biomechanical modeling and biomechanics-based non-rigid image registration.

SlicerCBM is under development at the
[Intelligent Systems for Medicine Lab](https://isml.ecm.uwa.edu.au)
at
[The University of Western Australia](https://www.uwa.edu.au).

## Modules

The SlicerCBM extension currently includes the following features implemented as 3D Slicer modules:

- Segmentation
  - DTI Segmentation: Segment diffusion tensor image (DTI) into gray matter (GM), white matter (WM) and cerebrospinal fluid (CSF) tissue classes using fuzzy C-means clustering (FCM) algorithm.
  - Fusion
  - Fusion2

- Geometry
  - Cran Creator
  - Fiducials To Surface
  - MeshNodes To Fiducials
  - Sheet From Points
  - Skull Generator
  - Surface Triangulation (deprecated): Create uniform triangulation of 3D surface model using PyACVD. This module is deprecated. Please use 3D Slicer's built-in Surface Toolbox instead.

- Mesh/Grid
  - MVox Mesh Generator: Create structured hexahedral grid using MVox.
  - Tetrahedral Mesh Generator (deprecated): Create tetrahedral grid using Gmsh. This module is deprecated and will be removed. Please use the ComputationalGridGenerator module instead.
  - Computational Grid Generator (todo): Create tetrahedral grid using Gmsh.
  - Tumor Resection And BRain Remodelling: Create tetrahedral grid of brain with tumor cavity using Gmsh.

- Property
  - Brain Material Properties
  - Electrical Conductivity: Assign electrical conductivity to an image volume.
  - Fuzzy Classification

- BCs/Load
  - Brain Mesh Surface Cells Selection
  - Brain Surface Neighbouring Cells Selection
  - Electrodes To Markups
  - Fiducial To Model Distance
  - Node Selector

- Solver
  - EEG Solver (todo)
  - MTLED Simulator

- Visualization
  - Visualisation

### Deprecated Modules

The following modules are no longer actively developed
or automatically loaded when installing SlicerCBM,
but may be useful for some applications:

- Mesh Nodes To Fiducials (TODO) (see [#51](https://github.com/SlicerCBM/SlicerCBM/issues/51))
- Tetrahedral Mesh Generator (TODO)

## Installation

Please note that the SlicerCBM extension for 3D Slicer
is currently supported on Linux and macOS operating systems only.

Some of the SlicerCBM modules require the following external dependencies to be installed.

### Gmsh

[Gmsh](https://gmsh.info) should be installed automatically when it is required by one of the SlicerCBM modules.

Due to GCC C++ ABI incompatibility between Gmsh and 3D Slicer,
Gmsh cannot be installed automatically within 3D Slicer using the `pip_install` command
(see [#41](https://github.com/SlicerCBM/SlicerCBM/issues/41)).
To install [Gmsh](https://gmsh.info) on Linux please see this
[workaround](https://github.com/SlicerCBM/SlicerCBM/issues/41#issuecomment-1553212336).

### MVox Mesh Voxelizer

To install [MVox Mesh Voxelizer](https://github.com/benzwick/mvox)
please refer to its [Installation Guide](https://github.com/benzwick/mvox#installing).

### ExplicitSim

To install [ExplicitSim](https://bitbucket.org/explicitsim/explicitsim)
please refer to its [Installation Guide](https://bitbucket.org/explicitsim/explicitsim/src/master/INSTALL.md).

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
