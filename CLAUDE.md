# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

SlicerCBM is a 3D Slicer extension for computational biophysics in medicine. It provides tools for creating and solving computational models of biophysical systems with a focus on clinical and biomedical applications, including grid generation, material property assignment, boundary conditions, and solvers for biomechanical modeling.

Documented platform support: Linux and macOS.

## Build System

This is a CMake-based 3D Slicer extension, not a standalone Python package:

- Requires Slicer's CMake infrastructure (`find_package(Slicer REQUIRED)`)
- Builds are done through 3D Slicer's extension build system
- No traditional `make` or `pip install` workflow

## Code Quality

**Linting/Formatting:** Ruff (configured in `.ruff.toml`)
```bash
ruff check .           # Lint
ruff format .          # Format
```

Key settings:
- Python 3.12+ target
- Line length: 88
- PEP 257 docstring convention

## Module Architecture

Each module follows the 3D Slicer ScriptedLoadableModule pattern with three classes:

```python
# 1. Module metadata (ScriptedLoadableModule)
class ModuleName(ScriptedLoadableModule):
    def __init__(self, parent):
        # Set: title, categories, dependencies, contributors, helpText

# 2. UI/Widget (ScriptedLoadableModuleWidget, VTKObservationMixin)
class ModuleNameWidget(ScriptedLoadableModuleWidget, VTKObservationMixin):
    def setup(self)                      # Initialize UI from .ui file
    def updateGUIFromParameterNode()     # Sync UI from MRML parameter node
    def updateParameterNodeFromGUI()     # Sync MRML from UI
    def onApplyButton()                  # Main action handler

# 3. Business logic (ScriptedLoadableModuleLogic)
class ModuleNameLogic(ScriptedLoadableModuleLogic):
    def setDefaultParameters(parameterNode)
    def run(...)                         # Core algorithm
```

**UI files:** Qt Designer `.ui` files in `Resources/UI/`

**Module categories:** Follow pattern `CBM.Category.Subcategory` (e.g., `CBM.Physics.Electromagnetics.Property`)

## Dependency Installation Pattern

For Python dependencies not bundled with Slicer, modules use dynamic pip installation:

```python
try:
    import skfuzzy
except ModuleNotFoundError:
    slicer.util.pip_install("scikit-fuzzy")
    import skfuzzy
```

## External Dependencies

Some modules require external tools installed separately:
- **Gmsh**: Has GCC C++ ABI incompatibility with Slicer on Linux (see issue #41 for workaround)
- **MVox**: https://github.com/benzwick/mvox
- **ExplicitSim**: https://bitbucket.org/explicitsim/explicitsim

## Testing

Tests are in `ModuleName/Testing/Python/` and run through Slicer's test framework using unittest.

## Documentation

Sphinx-based docs in `docs/` directory:
```bash
cd docs && make html   # Build to docs/_build/html
```
