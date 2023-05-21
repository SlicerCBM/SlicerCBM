# Craniotomy-induced brain shift

*Authors: Saima Safdar*

For craniotomy-induced brain shift, we need a craniotomy region to
select the nodes under the craniotomy area on the brain surface. For
this we created a module to automatically construct that craniotomy
region (see Fig. [1.19](#fig:cran){reference-type="ref"
reference="fig:cran"}). The steps are as follows:

1.  Select the "CranCreator" module.

2.  Select the "Input volume" to create a head mask for pre-operative
    MRI.

3.  Hit "Apply" to generate the preoperative head mask.

4.  Select the "Input volume" to create a head mask using
    intra-operative MRI.

5.  Hit "Apply" to generate the intraoperative head mask.

6.  Select the "Select preoperative segment", which is the head segment
    generated in step 3.

7.  Select the "Select intraoperative segment", which is the head
    segment generated in step 5.

8.  Hit "Apply" to get the craniotomy region.

![Patient-specific craniotomy region model
triangulation.](./figs/cran_2dmodel.png){#fig:cran_2dmodel
width="\\textwidth"}

Generate the surface model for this craniotomy region using "Model
Maker" module of 3D Slicer. After generating a craniotomy surface model,
generate a uniform triangulation of the craniotomy surface model using
the "SurfaceTriangulation" module (see
Fig. [1.20](#fig:cran_2dmodel){reference-type="ref"
reference="fig:cran_2dmodel"}).

![NodeSelector module within 3D Slicer along with patient-specific brain
model and craniotomy reference geometry for selecting nodes under
craniotomy on brain surface.](./figs/cran_2dmodel_2.png){#fig:node_sel
width="\\textwidth"}

![Patient-specific brain model with selected loaded nodes under
craniotomy.](./figs/load_node.png){#fig:node_sel2 width="\\textwidth"}

![Patient-specific brain model with selected nodes under craniotomy
(highlighted red region) in 3D window along with showing nodes (red
dots) in axial, sagittal and coronal view. Yellow outline around brain
in axial, sagittal and coronal view shows the boundary of the resulting
3D patient-specific brain
geometry.](./figs/load_node2.png){#fig:node_sel3 width="\\textwidth"}

![NodeSelector module outcome along with 3D brain model and 3D
craniotomy model in 3D window within 3D Slicer.
](./figs/load_node3.png){#fig:node_sel4 width="\\textwidth"}

Use the "NodeSelector" to select the brain surface nodes under
craniotomy region (see Fig. [1.21](#fig:node_sel){reference-type="ref"
reference="fig:node_sel"}). The steps are as follows:

1.  Select the "NodeSelector" module.

2.  Select the "Input Model to select Nodes", which is the craniotomy
    region model.

3.  Select the "Input Brain Model", which is the patient-specific brain
    surface triangulated model.

4.  Select the "Output Displaced Nodes", which is the txt file to save
    the loaded nodes ids.

5.  Select the "Output Cell Numbers (Triangles)", which is the txt file
    containing cell numbers.

6.  Hit "Apply" to get the selected brain nodes (loaded nodes), on which
    displacements will be applied.

The result for the "NodeSelector" are in
Fig. [1.22](#fig:node_sel2){reference-type="ref"
reference="fig:node_sel2"}.

![ElectrodesToMarkups module for selecting electrodes within 3D Slicer.
](./figs/electrode.png){#fig:electrode width="\\textwidth"}

