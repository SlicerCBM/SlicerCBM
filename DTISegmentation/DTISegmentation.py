#!/usr/bin/env python3

import nrrd
import numpy as np
from tqdm import tqdm           # progress bar
import os
import sys
import time
import argparse

try:
    import slicer
    SLICER = True
except:
    SLICER = False

if SLICER:
    # https://discourse.slicer.org/t/install-python-library-with-extension/10110/2
    import slicer.util
    try:
        import skfuzzy
    except:
        slicer.util.pip_install('scikit-fuzzy')
        import skfuzzy
else:
    import skfuzzy

print(sys.argv[0])
if SLICER: sys.stdout.flush()

TIC = time.time()               # Timer for total time elapsed

# ------------------------------------------------------------------------------
# Parameters

parser = argparse.ArgumentParser()

# dti input file
parser.add_argument('--dti', required=True,
                    help='Diffusion tensor image (DTI) input file.')

# mask input file
parser.add_argument('--mask', required=True,
                    help='Mask input file definind the brain region.')

# output directory
parser.add_argument('--outdir', required=True,
                    help='Output directory for output files.')

args = parser.parse_args()
print(args)
if SLICER: sys.stdout.flush()

dti_ifile = args.dti
mask_ifile = args.mask
outdir = args.outdir

# ------------------------------------------------------------------------------

dti, header_dti = nrrd.read(dti_ifile)
mask, header_mask = nrrd.read(mask_ifile)

img = np.zeros(dti.shape[1:], dtype=np.float32)[mask > 0]
if header_dti['sizes'][0] == 6:
    # "3D-symmetric-matrix" 6 Unique components of a 3D symmetric matrix: Mxx Mxy Mxz Myy Myz Mzz
    c00 = dti[0][mask > 0]
    c01 = dti[1][mask > 0]
    c02 = dti[2][mask > 0]
    c11 = dti[3][mask > 0]
    c12 = dti[4][mask > 0]
    c22 = dti[5][mask > 0]
elif header_dti['sizes'][0] == 9:
    # "3D-matrix" 9 Components of 3D matrix: Mxx Mxy Mxz Myx Myy Myz Mzx Mzy Mzz
    c00 = dti[0][mask > 0]
    c01 = dti[1][mask > 0]
    c02 = dti[2][mask > 0]
    c10 = dti[3][mask > 0]
    c11 = dti[4][mask > 0]
    c12 = dti[5][mask > 0]
    c20 = dti[6][mask > 0]
    c21 = dti[7][mask > 0]
    c22 = dti[8][mask > 0]
else:
    raise RuntimeError("Incorrect size of DTI data")

tr = c00 + c11 + c22

root_half = np.sqrt(1/2)
md = np.zeros(c00.shape)
fa = np.zeros(c00.shape)
vr = np.zeros(c00.shape)
ev = np.zeros((3, c00.shape[0]))

msg = "Computing diffusion tensor scalar maps"
print(msg + "...")
if SLICER:
    print(fa.shape[0])
    print(f"<filter-start><filter-name>DTISegmentation</filter-name><filter-comment>{msg}</filter-comment></filter-start>".format())
    print("<filter-progress>{}</filter-progress>".format(0.0))
    sys.stdout.flush()

tic = time.time()
for i in tqdm(range(fa.shape[0])):
    c = np.array([[c00[i], c01[i], c02[i]],
                  [c01[i], c11[i], c12[i]],
                  [c02[i], c12[i], c22[i]]])
    w, v = np.linalg.eig(c)
    ev[0,i] = w[0]
    ev[1,i] = w[1]
    ev[2,i] = w[2]
    avg = np.mean(w)
    # Fractional anisotropy
    fa[i] = root_half * (np.sqrt((w[0]-w[1])**2 +
                                 (w[1]-w[2])**2 +
                                 (w[2]-w[0])**2) /
                         np.sqrt(w[0]**2 + w[1]**2 + w[2]**2))
    # Volume ratio
    vr[i] = np.product(w) / avg
    # Mean diffusivity
    md[i] = np.sum(w) / 3
    if SLICER and (not i % (fa.shape[0] // 100)):
        print("<filter-progress>{}</filter-progress>".format(i/fa.shape[0]))
        sys.stdout.flush()

if SLICER:
    toc = tic - time.time()
    print("<filter-end><filter-name>DTISegmentation</filter-name><filter-time>{}</filter-time></filter-end>".format(toc))
    sys.stdout.flush()

DATA = md.reshape(1, img.size)
nclasses = 2
m = 2 # fuzziness parameter
error = 0.005
maxiter = 1000
cntr, u, u0, d, jm, p, fpc = skfuzzy.cluster.cmeans(DATA, nclasses, m, error, maxiter, init=None, seed=None)

print("Min. total fuzz: ", u.sum(axis=0).min())
print("Max. total fuzz: ", u.sum(axis=0).max())
print("FPC:             ", fpc)
print("Iterations:      ", p)

# cluster membership
clusters1 = np.argmax(u, axis=0)
CLUSTERS1_PLUS1 = np.zeros(dti.shape[1:])
CLUSTERS1_PLUS1[mask > 0] = clusters1 + 1
nrrd.write(os.path.join(outdir, "clusters1_plus1.nrrd"), CLUSTERS1_PLUS1, header_mask)

if md[clusters1 == 0].max() > md[clusters1 == 1].max():
    csf_cluster = 0
else:
    csf_cluster = 1

csf = np.zeros(clusters1.shape, dtype=int)
csf[clusters1 == csf_cluster] = 1
CSF = np.zeros(dti.shape[1:])
CSF[mask > 0] = csf
nrrd.write(os.path.join(outdir, "csf.nrrd"), CSF, header_mask)

# WM
DATA = fa[clusters1 != csf_cluster].reshape(1, img[clusters1 != csf_cluster].size)
nclasses = 2
m = 2 # fuzziness parameter
error = 0.005
maxiter = 1000
cntr, u, u0, d, jm, p, fpc = skfuzzy.cluster.cmeans(DATA, nclasses, m, error, maxiter, init=None, seed=None)

print("Min. total fuzz: ", u.sum(axis=0).min())
print("Max. total fuzz: ", u.sum(axis=0).max())
print("FPC:             ", fpc)
print("Iterations:      ", p)

# cluster membership
clusters2 = np.argmax(u, axis=0)

# WM has higher FA
if fa[clusters1 != csf_cluster][clusters2 == 0].max() > fa[clusters1 != csf_cluster][clusters2 == 1].max():
    wm_cluster = 0
else:
    wm_cluster = 1

wm = np.zeros(clusters2.shape, dtype=int)
wm[clusters2 == wm_cluster] = 1
WM = np.zeros(dti.shape[1:])
WM[(mask > 0) & (CSF == 0)] = wm
nrrd.write(os.path.join(outdir, "wm.nrrd"), WM, header_mask)

SEG = np.zeros(dti.shape[1:])
SEG[(mask > 0) & (CSF == 1)] = 5             # CSF
SEG[(mask > 0) & (CSF == 0) & (WM != 1)] = 4 # GM
SEG[(mask > 0) & (CSF == 0) & (WM == 1)] = 7 # WM
nrrd.write(os.path.join(outdir, "seg.nrrd"), SEG, header_mask)

TR = np.zeros(dti.shape[1:])
TR[mask > 0] = tr
nrrd.write(os.path.join(outdir, "tr.nrrd"), TR, header_mask)

MD = np.zeros(dti.shape[1:])
MD[mask > 0] = md
nrrd.write(os.path.join(outdir, "md.nrrd"), MD, header_mask)

FA = np.zeros(dti.shape[1:])
FA[mask > 0] = fa
nrrd.write(os.path.join(outdir, "fa.nrrd"), FA, header_mask)

TOC = time.time()
print("Total time elapsed: ", TOC - TIC)
