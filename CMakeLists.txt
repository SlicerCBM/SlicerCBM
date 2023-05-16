cmake_minimum_required(VERSION 3.13.4)

project(SlicerCBM)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "https://slicercbm.org")
set(EXTENSION_CATEGORY "Physics")
set(EXTENSION_CONTRIBUTORS "Saima Safdar, Benjamin Zwick")
set(EXTENSION_DESCRIPTION "Computational Biophysics for Medicine in 3D Slicer")
set(EXTENSION_ICONURL "https://github.com/SlicerCBM/SlicerCBM/SlicerCBM.png")
set(EXTENSION_SCREENSHOTURLS "https://github.com/SlicerCBM/SlicerCBM/Screenshots/1.png")
set(EXTENSION_DEPENDS "NA") # Specified as a list or "NA" if no dependencies

#-----------------------------------------------------------------------------
# Extension dependencies
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#-----------------------------------------------------------------------------
# Extension modules
add_subdirectory(BrainMaterialProperties)
add_subdirectory(BrainMeshSurfaceCellsSelection)
add_subdirectory(BrainSurfaceNeighbouringCellsSelection)
add_subdirectory(ComputationalGridGenerator)
add_subdirectory(CranCreator)
add_subdirectory(DTISegmentation)
add_subdirectory(ElectricalConductivity)
add_subdirectory(ElectrodesToMarkups)
add_subdirectory(FiducialsToSurface)
add_subdirectory(FiducialToModelDistance)
add_subdirectory(Fusion)
add_subdirectory(Fusion2)
add_subdirectory(FuzzyClassification)
add_subdirectory(MeshNodesToFiducials)
add_subdirectory(MTLEDSimulator)
add_subdirectory(MVoxMeshGenerator)
add_subdirectory(NodeSelector)
add_subdirectory(SheetFromPoints)
add_subdirectory(SkullGenerator)
add_subdirectory(SurfaceTriangulation)
add_subdirectory(TetrahedralMeshGenerator) # TODO: remove this?
add_subdirectory(TumorResectionAndBRainRemodelling)
add_subdirectory(Visualisation)

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_GENERATE_CONFIG})
include(${Slicer_EXTENSION_CPACK})
