cmake_minimum_required(VERSION 3.13.4)

project(ComputationalGridGenerator)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "https://www.slicer.org/wiki/Documentation/Nightly/Extensions/ComputationalGridGenerator")
set(EXTENSION_CATEGORY "Computational Grid Generator")
set(EXTENSION_CONTRIBUTORS "Saima Safdar (ISML. University of Western Australia.)")
set(EXTENSION_DESCRIPTION "This extension generates a computational grid based on the 
patient-specific MRI after skull stripping given as an input. ")
set(EXTENSION_ICONURL "http://www.example.com/Slicer/Extensions/ComputationalGridGenerator.png")
set(EXTENSION_SCREENSHOTURLS "http://www.example.com/Slicer/Extensions/ComputationalGridGenerator/Screenshots/1.png")
set(EXTENSION_DEPENDS "NA") # Specified as a list or "NA" if no dependencies

#-----------------------------------------------------------------------------
# Extension dependencies
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#-----------------------------------------------------------------------------
# Extension modules
add_subdirectory(ComputationalGridGenerator)
## NEXT_MODULE

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_GENERATE_CONFIG})
include(${Slicer_EXTENSION_CPACK})
