# Tumor resection induced brain shift

The steps are as follows:

1) Select "General Registration (BRAINS)" to register the pre-operative
to intra-operative MRI image. 

2) Define the gravity direction units. 

3) Select the "TetrahedralMeshGenerator", which is used to construct the
patient-specific geometry conforming tetrahedral integration grid. 

4) Select "FuzzyClassification", which is used to classify the tissues into
different classes (brain parenchyma, ventricles, tumour) for assigning
material properties. 

5) Select "MTLEDSimulator" to generate the
integration points. 

6) Select "MaterialProperties" to assign material
properties to integration points using Ogden model. 

7) Select
"MTLEDSimulator" to compute the reaction forces between tumour and
surrounding tissues. 

8) Generate the loading file from results of step 5. 

9) Reconstruct brain model with tumour cavity and generate a new
biomechanical model file for "MTLEDSimulator" 

10) Repeat step 5 and 6 to
generate integration points with tumour cavity and assign material
properties. 

11) Select "MTLEDSimulator" to compute brain displacement
after tumour resection. 

12) Extract undeformed and deformed nodal
coordinates from the results of step 11. 

13) Select "Scattered
Transform" to generate B-Spline transform for warping the pre-operative
MRI.