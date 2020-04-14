#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import click
import itk
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from matplotlib.colors import LinearSegmentedColormap
from matplotlib import cm
from ctvi_helpers import *

# --------------------------------------------------------------------------
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])
@click.command(context_settings=CONTEXT_SETTINGS)
@click.option('--input', '-i')
@click.option('--ct')
@click.option('--mask', '-m')
@click.option('--axis', '-a', default=1)
@click.option('--slice_start', '-s', default=-1)
@click.option('--slice_step', default=1)
@click.option('--slice_stop', default=-1, help='-1 for start+1, -2 for max')
@click.option('--output', '-o')
def ctvi_slice_nbr_click(input, ct, mask, axis, slice_start, slice_step, slice_stop, output):
    '''
    Doc todo
    '''

    # read images 
    ctvi_itk = itk.imread(input)
    ct = itk.imread(ct)
    mask = itk.imread(mask)
    ctvi = itk.array_from_image(ctvi_itk)
    ct = itk.array_from_image(ct)
    mask = itk.array_from_image(mask)
    print(ctvi.shape, ct.shape, mask.shape)

    # images MUST be the same size
    # spacing MUST be isotropic

    # slice
    if slice_start == -1:
        slice_start = int(ctvi.shape[1]/2)
    if slice_stop == -1:
        slice_stop = slice_start+1
    elif slice_stop == -2:
        slice_stop = ctvi.shape[axis]-1
    print(slice_start, slice_step, slice_stop)        

    # normalisation ? 90% percentile like in Kipritidis2019 ?
    print('min max', np.min(ctvi), np.max(ctvi))
    t = np.quantile(ctvi[ctvi>0], 0.9)
    print('Q90%', t)
    ctvi = ctvi/t

    # get colormap
    cmap, cmap_ct, norm = get_colormap1()

    # loop for slice
    s = slice_start
    while s < slice_stop:
        f = f'{output}_{s:03d}.png'
        ctvi_s = get_slice(ctvi, axis, s)
        ct_s = get_slice(ct, axis, s)
        mask_s = get_slice(mask, axis, s)
        save_img(f, ctvi_s, ct_s, mask_s, cmap, cmap_ct, norm)
        s = s + slice_step


# --------------------------------------------------------------------------
if __name__ == '__main__':
    ctvi_slice_nbr_click()
