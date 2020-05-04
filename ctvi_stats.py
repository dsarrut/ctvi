#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import click
from ctvi_helpers import *
import itk
import matplotlib.pyplot as plt


# --------------------------------------------------------------------------
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])
@click.command(context_settings=CONTEXT_SETTINGS)
@click.option('--ctvi', '-i', required=True)
@click.option('--mask', '-m', required=True)
@click.option('--histo', help='histogram binning', default=0)
def ctvi_stats(ctvi, mask, histo):
    '''
    Doc todo
    '''

    ctvi = itk.imread(ctvi)
    mask = itk.imread(mask)

    check_same_geometry(ctvi, mask)

    data = itk.array_view_from_image(ctvi)
    mask = itk.array_view_from_image(mask)
    mask[mask != 0] = 1

    s = basics_stats(data, mask)

    print(f'Min/Max {s.min:.2f} {s.max:.2f}  Mean/Std {s.mean:.2f} {s.std:.2f}  '
          f' {s.pixels_count} pixels  Q10/Q90 {s.q10:.2f}  {s.q90:.2f} ')

    if histo == 0:
        exit(0)

    fig = plt.figure()
    m = mask.ravel()
    d = data.ravel()[m != 0]
    d = d[d!=0] # there are  a lot of almost zeros values
    q1 = np.quantile(d, 0.9)
    plt.hist(d, bins=histo, range=(0,q1))
    plt.show()


# --------------------------------------------------------------------------
if __name__ == '__main__':
    ctvi_stats()
