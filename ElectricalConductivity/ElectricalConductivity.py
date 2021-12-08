#!/usr/bin/env python3

import nrrd
import numpy as np
import time
import os
from tqdm import tqdm           # progress bar
import argparse
from pprint import pprint
import sys
from numpy.random import default_rng

print(sys.argv[0])

TIC = time.time()               # Timer for total time elapsed

# ------------------------------------------------------------------------------
# Parameters

parser = argparse.ArgumentParser()

# labelmap input file
parser.add_argument('--labelmap', required=True,
                    help='Labelmap input file containing tissue type labels.')

# dti input file
parser.add_argument('--dti', required=True,
                    help='Diffusion tensor image (DTI) input file.')

# output file
parser.add_argument('--output', required=True,
                    help='Output file containing conductivity.')

# Tuch WM
parser.add_argument('--tuch-wm', default=False, action='store_true',
                    help='Use Tuch method for white matter.')
parser.add_argument('--no-tuch-wm', dest='tuch_wm', action='store_false')

# Tuch GM
parser.add_argument('--tuch-gm', default=False, action='store_true',
                    help='Use Tuch method for gray matter.')
parser.add_argument('--no-tuch-gm', dest='tuch_gm', action='store_false')

# Tuch CSF
parser.add_argument('--tuch-csf', default=False, action='store_true',
                    help='Use Tuch method for cerebrospinal fluid.')
parser.add_argument('--no-tuch-csf', dest='tuch_csf', action='store_false')

args = parser.parse_args()
print(args)

units = "S/mm"                  # "S/m" or "S/mm"

# Segmentation/labelmap
seg_ifile = args.labelmap

# Diffusion tensors
dti_ifile = args.dti

# Conductivity output file
con_ofile = args.output

# TODO: make this an option
method = 'fractional'  # 'fractional' or 'linear'

# Replace negative eigenvalues with this value
# (must be greater than zero to avoid roundoff error in eigenvectors)
minimum_eigenvalue = 1e-6
# minimum_eigenvalue = 2 * np.finfo(np.float64).eps

# Paramaters of anisotropic conductivity using Tuch's method
k = 0.844                       # S.s/mm^3 - TODO: is this consistent with other units?
De = None
Di = 0.117                      # micrometers^2/millisecond
Se = 1.52                       # S/m

if De is None:
    if method == 'fractional':
        De = 2.04               # micrometers^2/millisecond
    elif method == 'linear':
        De = 0.124              # micrometers^2/millisecond
    else:
        raise RuntimeError

# ------------------------------------------------------------------------------
# Read segmentation label map, color table and DTI

seg_data, seg_header = nrrd.read(seg_ifile)
dti_data, dti_header = nrrd.read(dti_ifile)

mask = seg_data

# Segment labels
# TODO: read from slicer color table?
scalp_label = 1
skull_label = 2
gm_label    = 4
csf_label   = 5
wm_label    = 7
sheet_label = 10

# Binary masks of segments
skull = seg_data[mask > 0] == skull_label
scalp = seg_data[mask > 0] == scalp_label
csf   = seg_data[mask > 0] == csf_label
sheet = seg_data[mask > 0] == sheet_label
gm    = seg_data[mask > 0] == gm_label
wm    = seg_data[mask > 0] == wm_label

# Conductivity (S/m)
# NOTE: units are converted after computing conductivity to avoid roundoff errors
# TODO: read from a table?
con_scalp = 0.33
con_skull = 0.012
con_gm    = 0.33
con_csf   = 1.79
con_wm    = 0.33            # only used if isotropic WM
con_sheet = 1e-6            # use small number but not 0 if insulating

# ------------------------------------------------------------------------------
# Processing

if dti_header['sizes'][0] == 6:
    # "3D-symmetric-matrix" 6 Unique components of a 3D symmetric matrix: Mxx Mxy Mxz Myy Myz Mzz
    D00 = dti_data[0][mask > 0]
    D01 = dti_data[1][mask > 0]
    D02 = dti_data[2][mask > 0]
    D11 = dti_data[3][mask > 0]
    D12 = dti_data[4][mask > 0]
    D22 = dti_data[5][mask > 0]
elif dti_header['sizes'][0] == 9:
    # NOTE: data is assumed to be symmetric
    # "3D-matrix" 9 Components of 3D matrix: Mxx Mxy Mxz Myx Myy Myz Mzx Mzy Mzz
    D00 = dti_data[0][mask > 0]
    D01 = dti_data[1][mask > 0]
    D02 = dti_data[2][mask > 0]
    # D10 = dti_data[3][mask > 0]
    D11 = dti_data[4][mask > 0]
    D12 = dti_data[5][mask > 0]
    # D20 = dti_data[6][mask > 0]
    # D21 = dti_data[7][mask > 0]
    D22 = dti_data[8][mask > 0]
else:
    raise RuntimeError("Incorrect size of DTI data")

# ------------------------------------------------------------------------------
# Initialize isotropic conductivity

# Background conductivity
C00 = np.zeros(D00.shape)
C01 = np.zeros(D01.shape)
C02 = np.zeros(D02.shape)
C11 = np.zeros(D11.shape)
C12 = np.zeros(D12.shape)
C22 = np.zeros(D22.shape)

# Isotropic conductivities
C00[scalp] = C11[scalp] = C22[scalp] = con_scalp
C00[skull] = C11[skull] = C22[skull] = con_skull
C00[gm]    = C11[gm]    = C22[gm]    = con_gm
C00[csf]   = C11[csf]   = C22[csf]   = con_csf
C00[wm]    = C11[wm]    = C22[wm]    = con_wm
C00[sheet] = C11[sheet] = C22[sheet] = con_sheet

# ------------------------------------------------------------------------------
# Anisotropic conductivity using Tuch's method

tuch_labels = []
if args.tuch_wm:
    tuch_labels.append(wm_label)
if args.tuch_gm:
    tuch_labels.append(gm_label)
if args.tuch_csf:
    tuch_labels.append(csf_label)

if len(tuch_labels) > 0:
    tic = time.time()
    voxels_with_negative_eigenvalues = []
    min_wm_mean_cond = np.inf
    max_wm_mean_cond = -np.inf
    avg_wm_mean_cond = 0
    avg_wm_max_eigenvalue = 0
    avg_wm_mid_eigenvalue = 0
    avg_wm_min_eigenvalue = 0
    num_wm_voxels = 0
    print("Compute anisotropic conductivity")
    D = np.zeros((3, 3))
    for i, label in enumerate(tqdm(seg_data[mask > 0])):
        if label in tuch_labels:
            # D = np.array([[D00[i], D01[i], D02[i]],
            #               [D01[i], D11[i], D12[i]],
            #               [D02[i], D12[i], D22[i]]], dtype=float)
            D[0,0] = D00[i]
            D[0,1] = D01[i]
            D[0,2] = D02[i]
            D[1,0] = D01[i]
            D[1,1] = D11[i]
            D[1,2] = D12[i]
            D[2,0] = D02[i]
            D[2,1] = D12[i]
            D[2,2] = D22[i]
            # Scale D units from m^2/s to micrometres^2/millisecond
            # as used in Tuch et al. 2001
            D *= 1000
            w, v = np.linalg.eig(D)
            # Diffusion tensor must be positive semi-definite
            # See:https://www.slicer.org/wiki/Documentation/4.10/Modules/ResampleDTIVolume
            if np.any(w < 0):
                raise RuntimeError(f"Diffusion not positive semi-definite at voxel {i}")
            if method == 'linear':
                wout = k*(w-De)
            elif method == 'fractional':
                BetaD = (Di-De)/(Di+2*De)
                Numer = 3*(w-De)*(BetaD+2)
                Denom = (w*(4*BetaD**3 - 5*BetaD - 2) +
                         De*(8*BetaD**3 - 7*BetaD + 2))
                wout = Se*(1 + Numer/Denom)
            else:
                raise RuntimeError
            # Ensure that eigenvalues are all positive (see Tuch et al. 2001, p. 11700)
            if np.any(wout < 0):
                voxels_with_negative_eigenvalues.append(i)
            wout = np.array([max(minimum_eigenvalue, w) for w in wout])
            C = v @ np.diag(wout) @ v.T
            if np.any(wout < 0):
                raise RuntimeError(f"One or more eigenvalue is negative at voxel {i}")
            # Store the upper triangle of C only
            C00[i] = C[0,0]
            C01[i] = C[0,1]
            C02[i] = C[0,2]
            C11[i] = C[1,1]
            C12[i] = C[1,2]
            C22[i] = C[2,2]
            # Ensure that conductivity is symmetric and positive semi-definite
            if np.any(np.abs(C-C.T) > np.finfo(np.float32).eps):
                raise RuntimeError(f"Conductivity not symmetric at voxel {i}")
            w, v = np.linalg.eig(C)
            if np.any(w < 0):
                raise RuntimeError(f"Conductivity not positive semi-definite at voxel {i}")
            # Sort eignenvalues and eigenvectors
            idx = w.argsort()[::-1]
            w = w[idx]
            v = v[:,idx]
            mc = np.sum(w) / 3.0 # mean conductivity
            if label == wm_label:
                num_wm_voxels += 1
                min_wm_mean_cond = min(min_wm_mean_cond, mc)
                max_wm_mean_cond = max(max_wm_mean_cond, mc)
                avg_wm_mean_cond += mc
                avg_wm_max_eigenvalue += w[0]
                avg_wm_mid_eigenvalue += w[1]
                avg_wm_min_eigenvalue += w[2]
    toc = time.time()
    avg_wm_mean_cond /= num_wm_voxels
    avg_wm_max_eigenvalue /= num_wm_voxels
    avg_wm_mid_eigenvalue /= num_wm_voxels
    avg_wm_min_eigenvalue /= num_wm_voxels
    print("Time elapsed: ", toc - tic)
    print(f"{num_wm_voxels} voxels are white matter.")
    print(f"{len(voxels_with_negative_eigenvalues)} voxels had negative eigenvalues",
          f"(these eigenvalues were corrected to {minimum_eigenvalue})")
    print("White matter conductivity (min, max): ({}, {})".format(
        min_wm_mean_cond, max_wm_mean_cond))
    print("White matter conductivity (avg, std): ({}, ???)".format(
        avg_wm_mean_cond))
    print("White matter conductivity average eigenvalues (max, mid, min): ({}, {}, {})".format(
        avg_wm_max_eigenvalue, avg_wm_mid_eigenvalue, avg_wm_min_eigenvalue, ))

for C in [C00, C01, C02, C11, C12, C22]:
    # Convert units
    if units == "S/m":
        pass
    elif units == "S/mm":
            C /= 1000.
    else:
        raise NotImplementedError
    # Histograms
    # TODO
    # import matplotlib.pyplot as plt
    # plt.hist(mean conductivity)

# ------------------------------------------------------------------------------
# Write conductivity to file

con_data = np.zeros(dti_data.shape)
if dti_header['sizes'][0] == 6:
    # "3D-symmetric-matrix" 6 Unique components of a 3D symmetric matrix: Mxx Mxy Mxz Myy Myz Mzz
    con_data[0][mask > 0] = C00
    con_data[1][mask > 0] = C01
    con_data[2][mask > 0] = C02
    con_data[3][mask > 0] = C11
    con_data[4][mask > 0] = C12
    con_data[5][mask > 0] = C22
elif dti_header['sizes'][0] == 9:
    # NOTE: data is assumed to be symmetric
    # "3D-matrix" 9 Components of 3D matrix: Mxx Mxy Mxz Myx Myy Myz Mzx Mzy Mzz
    con_data[0][mask > 0] = C00
    con_data[1][mask > 0] = C01
    con_data[2][mask > 0] = C02
    con_data[3][mask > 0] = C01 # = C10
    con_data[4][mask > 0] = C11
    con_data[5][mask > 0] = C12
    con_data[6][mask > 0] = C02 # = C20
    con_data[7][mask > 0] = C12 # = C21
    con_data[8][mask > 0] = C22

con_header = dti_header.copy()
con_header['type'] = 'double'

print("Write conductivity to file: ", con_ofile)
tic = time.time()
nrrd.write(con_ofile, con_data, dti_header)
toc = time.time()
print("Time taken to write to file: ", toc - tic)

TOC = time.time()
print("Total time elapsed: ", TOC - TIC)
