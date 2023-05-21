# Electrode placement induced brain shift

In case of electrode placement-induced brain shift, we constructed an
electrode sheet in order to select the underlying brain nodes on which
displacements are applied. The procedure begins with selecting original
electrode positions from intra-operative CT and is divided into
following steps:

1.  Select the "ElectrodesToMarkups" module (see
    Fig. [1.25](#fig:electrode){reference-type="ref"
    reference="fig:electrode"}).

2.  Select the "Input Electrode" image, which is a ".nrrd" image with
    segmented electrodes from intra-operative CT.

3.  Select the "Minimum Size (Split island)", which is the size of the
    number of voxels that defined a single electrode.

4.  Select the "Save Electrode Centroid Positions", which is the .txt
    file for saving the x,y,z coordinates for each electrode or (save
    the fiducials file .fcsv, which are the generated red dots placed at
    the identified location for each electrode).

5.  Hit "Apply"

6.  The results is the Markups/fiducials (red dots). The file of which
    can be saved separately as .fcsv file.

!["fiducialtomodeldistance" module for selecting projected electrode
locations on an undeformed brain surface with reference to original
electrode locations within 3D Slicer.
](./figs/electrode_2.png){#fig:electrode_2 width="\\textwidth"}

After you get the fiducials (red dots = identified original electrode
locations), we use these to identify the projected electrode locations
(the position of each of the electrode on an undeformed brain surface).
We use the "fiducialtomodeldistance" (see
Fig. [1.26](#fig:electrode_2){reference-type="ref"
reference="fig:electrode_2"}) for this purpose, the steps are as
follows:

1.  Select the "fiducialtomodeldistance" module.

2.  Select the "Input Markups", which are the identified original
    electrodes represented by the fiducials (red dots).

3.  Select the "Input Model", which is the patient-specific triangulated
    surface model.

4.  Hit "Apply"

5.  The result is the set of fiducials representing the projected
    electrode locations on the brain surface.

![\"Markupstosurfacemesh\" module for constructing an electrode sheet
model using projected electrode locations within 3D Slicer.
](./figs/electrode_3.png){#fig:electrode_3 width="\\textwidth"}

After getting the projected electrode locations, we construct an
electrode sheet model using the information of the locations of the
projected electrodes on the brain surface (see
Fig. [1.27](#fig:electrode_3){reference-type="ref"
reference="fig:electrode_3"}). The steps are as follows:

1.  Select "Markupstosurfacemesh" module.

2.  Select the "Input fiducials", which are the projected electrode
    locations.

3.  Select the "Output Model", which is the resulting electrode sheet
    model.

4.  Hit "Apply", to get the electrode sheet model as in
    Fig. [1.27](#fig:electrode_3){reference-type="ref"
    reference="fig:electrode_3"}.

![\"SurfaceTriangulation\" module for uniform triangulation of the
electrode sheet model within 3D Slicer.
](./figs/electrode_4.png){#fig:electrode_4 width="\\textwidth"}

After getting the electrode sheet surface model, we do the uniform
triangulation of the electrode sheet surface by using the
"SurfaceTriangulation" (see
Fig. [1.28](#fig:electrode_4){reference-type="ref"
reference="fig:electrode_4"}). The steps are as follows:

1.  Select the "SurfaceTriangulation" module.

2.  Select the "Input Model", which is the electrode sheet surface
    model.

3.  Select the "Number of clusters".

4.  Hit "Apply", to get a uniform surface triangulation of the electrode
    sheet with clusters of your choice.

![\"NodeSelector\" module for selecting nodes on undeformed brain
surface under electrode sheet model within 3D Slicer.
](./figs/electrode_5.png){#fig:electrode_5 width="\\textwidth"}

After constructing a triangulated electrode sheet model, we use it to
select the underlying brain cells and then from there we select the
corresponding brain nodes (loaded nodes). The steps are as follows:

1.  Select the "NodeSelector" module (see
    Fig. [1.29](#fig:electrode_5){reference-type="ref"
    reference="fig:electrode_5"}).

2.  Select the "Input model to select Nodes", which is the reference
    model to select the brain surface nodes i.e; electrode sheet model.

3.  Select the "Input Brain Model", the brain model on which the loaded
    nodes are selected.

4.  Select "Output Displaced Nodes", which is the .txt file of the
    selected nodes under electrode sheet model.

5.  Select "Output Cell Numbers (triangles)", which is the .txt file of
    the selected brain cells under electrode sheet model.

6.  Hit "Apply", gives you the corresponding brain nodes with fiducials
    placed at each selected brain node (see
    Fig. [1.29](#fig:electrode_5){reference-type="ref"
    reference="fig:electrode_5"}).

![\"Scattered Transform\" module for generating a B-Spline transform
using original electrode positions and projected electrode positions
within 3D Slicer. Red dots represents the transformed brain nodes.
Yellow lines represents electrode sheet surface on a deformed and
undeformed brain geometry. ](./figs/electrode_6.png){#fig:electrode_6
width="\\textwidth"}

![Displacement loading calculation based on undeformed and deformed
brain surface nodes (see
Fig. [\[fig:electrodes_8\]](#fig:electrodes_8){reference-type="ref"
reference="fig:electrodes_8"})
](./figs/electrode_7.png){#fig:electrode_7 width="\\textwidth"}

We then used the original electrode locations and projected electrode
locations to calculate a transform using scattered transform. We use
this transform and apply it on the selected brain nodes (loaded nodes)
on the brain surface to get the brain nodes on the deformed brain
surface. The steps to calculate the B-spline transform using the
scattered transform are as follows:

1.  Select the "Scattered Transform" module.

2.  Select the "File with initial point positions", which is the
    locations of the original electrode positions.

3.  Select the "File with displaced point positions", which is the
    locations of the projected electrode positions.

4.  Select "Slicer B-spline transform".

5.  Leave all other settings remain unchanged and hit "Apply", the
    result is a transform.

6.  Use the transform module to apply on the brain nodes (loaded nodes)
    to get the corresponding brain nodes locations on the deformed brain
    geometry (see Fig. [1.30](#fig:electrode_6){reference-type="ref"
    reference="fig:electrode_6"} and
    [1.31](#fig:electrode_7){reference-type="ref"
    reference="fig:electrode_7"}).

We then do load calculation using the displacement loading in
\"MeshNodesToFiducials\" module (see
Fig. [1.31](#fig:electrode_7){reference-type="ref"
reference="fig:electrode_7"} and
[1.32](#fig:electrode_8){reference-type="ref"
reference="fig:electrode_8"}).

![Undeformed brain surface nodes (blue) and deformed brain surface nodes
(red) after applying the scattered transform.
](./figs/electrode_8.png){#fig:electrode_8 width="\\textwidth"}

In case of non-rectangular electrode grid, the selection of displaced
nodes is done using the \"BrainMeshSurfaceCellsSelection\" (see
Fig. [1.33](#fig:brainCells){reference-type="ref"
reference="fig:brainCells"} and
[1.34](#fig:neighbourCells){reference-type="ref"
reference="fig:neighbourCells"})
\"BrainSurfaceNeighbouringCellsSelection\" modules.

![\"BrainMeshSurfaceCellsSelection\" module within 3D Slicer.
](./figs/brainCells.png){#fig:brainCells width="\\textwidth"}

![\"BrainSurfaceNeighbouringCellsSelection\" module within 3D Slicer.
](./figs/neighbourCells.png){#fig:neighbourCells width="\\textwidth"}

Case Study: Tumour resection-induced brain shift

The steps are as follows:

1\) Select "General Registration (BRAINS)" to register the pre-operative
to intra-operative MRI image. 2) Define the gravity direction units. 3)
Select the "TetrahedralMeshGenerator", which is used to construct the
patient-specific geometry conforming tetrahedral integration grid. 4)
Select "FuzzyClassification", which is used to classify the tissues into
different classes (brain parenchyma, ventricles, tumour) for assigning
material properties. 5) Select "MTLEDSimulator" to generate the
integration points. 6) Select "MaterialProperties" to assign material
properties to integration points using Ogden model. 7) Select
"MTLEDSimulator" to compute the reaction forces between tumour and
surrounding tissues. 8) Generate the loading file from results of step
5. 9) Reconstruct brain model with tumour cavity and generate a new
biomechanical model file for "MTLEDSimulator" 10) Repeat step 5 and 6 to
generate integration points with tumour cavity and assign material
properties. 11) Select "MTLEDSimulator" to compute brain displacement
after tumour resection. 12) Extract undeformed and deformed nodal
coordinates from the results of step 11. 13) Select "Scattered
Transform" to generate B-Spline transform for warping the pre-operative
MRI.
