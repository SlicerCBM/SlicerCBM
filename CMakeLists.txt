cmake_minimum_required(VERSION 3.13.4)

project(SlicerCBM)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "https://www.slicer.org/wiki/Documentation/Nightly/Extensions/SlicerCBM")
set(EXTENSION_CATEGORY "CBM")
set(EXTENSION_CONTRIBUTORS "Saima Safdar, Benjamin Zwick")
set(EXTENSION_DESCRIPTION "Computational Biophysics for Medicine in 3D Slicer.")
set(EXTENSION_ICONURL "https://github.com/SlicerCBM/SlicerCBM/SlicerCBM.png")
set(EXTENSION_SCREENSHOTURLS "https://github.com/SlicerCBM/SlicerCBM/Screenshots/1.png")
set(EXTENSION_DEPENDS "NA") # Specified as a list or "NA" if no dependencies

#-----------------------------------------------------------------------------
# Extension dependencies
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#-----------------------------------------------------------------------------
# Extension modules
add_subdirectory(DTISegmentation)
add_subdirectory(ElectricalConductivity)
add_subdirectory(MVoxMeshGenerator)
add_subdirectory(SheetFromPoints)

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_GENERATE_CONFIG})
include(${Slicer_EXTENSION_CPACK})
