# Fuzzy Classification

## Inputs

Input volume: Brain MRI scalar volume to be clustered.

Mask volume: Used to mask the input volume to include only the region of interest.

Input tumor mask: Optional mask for tumor segment.

Number of classes: Desired number of clusters or classes to use in fuzzy c-means clustering. Default is 2 for brain tissue and CSF. Use 3 classes when including the tumor segment.

## Outputs

Scalar volumes for each cluster membership (i.e., u: Final fuzzy c-partitioned matrix in skfuzzy).

See [skfuzzy documentation](https://pythonhosted.org/scikit-fuzzy/api/skfuzzy.html#cmeans) for more details.

The user should rename these volumes as e.g. "Membership Parenchyma" and "Membership CSF" by visual inspection (the algorithm cannot determine automatically which cluster is brain tissue or CSF).
