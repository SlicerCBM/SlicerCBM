# Create Head Tetrahedral Grid

## Overview

This module creates a computational grid of a head containing brain volume (tetrahedral) elements and skull surface (triangle) elements from a brain surface model, and saves it as a '.inp' mesh file. [Gmsh](https://gmsh.info/) is used internally to generate the grid.

## Panels and their use

### Inputs

- **Input brain surface:** Brain surface model that will be used to create the grid.

### Outputs

- **Model .inp file:** Grid file in `.inp` format that contains the nodal coordinates, brain volume tetrahedral elements and element set (`ELSET=brain`), skull surface shell elements and element set (`ELSET=skull`), and node set of brain nodes in contact with the skull (`NSET=contact`).
