# Fuzzy Classification

## Overview

This module performs fuzzy tissue classification of a scalar image volume.

See the following references for more details:

- Li M, Wittek A, Joldes GR, Miller K. (2016). Fuzzy Tissue Classification for Non-Linear Patient-Specific Biomechanical Models for Whole-Body Image Registration. In: Joldes G, Doyle B, Wittek A, Nielsen P, Miller K (eds) Computational Biomechanics for Medicine. Springer, Cham. doi: 10.1007/978-3-319-28329-6_8.

- Li M, Miller K, Joldes GR, Doyle B, Garlapati RR, Kikinis R, Wittek A. Patient-specific biomechanical model as whole-body CT image registration tool. Med Image Anal. 2015 May;22(1):22-34. doi: 10.1016/j.media.2014.12.008.

### Panels and their use

## Inputs

- **Input volume:** Brain MRI scalar volume to be clustered.

- **Mask volume:** Used to mask the input volume to include only the region of interest.

- **Input tumor mask:** Optional mask for tumor segment.

- **Number of classes:** Desired number of clusters or classes to use in fuzzy c-means clustering. Default is 2 for brain tissue and CSF. Use 3 classes when including the tumor segment.

## Outputs

- Scalar volumes for each cluster membership (i.e., u: Final fuzzy c-partitioned matrix in skfuzzy).
  The user should rename these volumes as e.g. "Membership Parenchyma" and "Membership CSF" by visual inspection (the algorithm cannot determine automatically which cluster is brain tissue or CSF).

See [skfuzzy documentation](https://pythonhosted.org/scikit-fuzzy/api/skfuzzy.html#cmeans) for more details.
