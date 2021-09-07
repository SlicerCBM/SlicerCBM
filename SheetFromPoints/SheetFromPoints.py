#!/usr/bin/env python3

import argparse
import numpy as np
import os
import pyvista as pv


def main(ifile, ofile, thickness):

    # Load points from file
    print(f"ifile: {ifile}")
    _, iext = os.path.splitext(ifile)
    if iext in ['.csv', '.txt']:
        # list of points (x,y,z)
        points = np.loadtxt(ifile, delimiter=',')
    elif iext == '.fcsv':
        # slicer fiducial points file
        points = np.loadtxt(ifile, delimiter=',', comments='#', usecols=(1,2,3))

    cloud = pv.wrap(points)

    surf1 = cloud.delaunay_2d()
    # surf1.plot(show_edges=True)

    surf1.compute_normals(cell_normals=True, point_normals=True, inplace=True)

    normal = np.array(np.mean(surf1.point_normals, axis=0))
    normal /= np.linalg.norm(normal) # normalize
    extrude = thickness * normal

    # surf2 = surf1.subdivide(2, "linear")
    # surf2 = surf1.subdivide(1, "loop")
    surf2 = surf1.subdivide(2, "butterfly")
    # surf2.plot(show_edges=True)

    mesh = surf2.extrude(extrude)
    # mesh.plot()

    # Save sheet mesh to file
    print(f"ofile: {ofile}")
    mesh.save(f"{ofile}", binary=False)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    # input file
    parser.add_argument('-i', '--input', required=True,
                        help='Input file containing coordinates of points.')

    # output file
    parser.add_argument('-o', '--output', required=True,
                        help='Output file containing sheet model geometry.')

    # thickness
    parser.add_argument('-t', '--thickness', required=True, type=float,
                        help='Thickness of sheet (use negative thickness to change direction).')

    import sys
    print('sys.argv:')
    print(sys.argv)

    args = parser.parse_args()
    print('args:')
    print(args)

    main(args.input, args.output, args.thickness)
