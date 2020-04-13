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
@click.option('--axe', '-a', default=1)
@click.option('--slice_nb', '-s', default=-1)
@click.option('--output', '-o')
def ctvi_slice_nbr_click(input, ct, mask, axe, slice_nb, output):
    '''
    Doc todo
    '''

    # read images 
    ctvi = itk.imread(input)
    ct = itk.imread(ct)
    mask = itk.imread(mask)
    ctvi = itk.array_from_image(ctvi)
    ct = itk.array_from_image(ct)
    mask = itk.array_from_image(mask)
    print(ctvi.shape, mask.shape)

    # slice
    if slice_nb == -1:
        slice_nb = int(ctvi.shape[1]/2)

    # normalisation ? 90% percentile like in Kipritidis2019 ?
    print('min max', np.min(ctvi), np.max(ctvi))
    t = np.quantile(ctvi[ctvi>0], 0.9)
    print('Q90%', t)
    ctvi = ctvi/t

    # get slice Y axis for the moment
    ctvi = ctvi[:, slice_nb, :]
    mask = mask[:, slice_nb, :]
    ct = ct[:, slice_nb, :]

    # upside down
    ctvi = np.flip(ctvi, 0)
    mask = np.flip(mask, 0)
    ct = np.flip(ct, 0)

    # color palette
    # https://matplotlib.org/tutorials/colors/colormaps.html
    cmap = plt.get_cmap('afmhot')
    cmap_ct = plt.get_cmap('gray')

    # build another palette with opacity 
    ncolors = 256
    #rg = np.max(ctvi)-np.min(ctvi)
    rg = 1.0
    s = int(-np.min(ctvi)/(rg/256))+1
    color_array = cmap(range(ncolors))
    color_array[0:s, -1] = 0
    color_array[s:, -1] = 0.8
    map_object = LinearSegmentedColormap.from_list(name='afmhot_alpha',colors=color_array)
    plt.register_cmap(cmap=map_object)
    cmap = plt.get_cmap('afmhot_alpha')

    # https://matplotlib.org/3.2.1/tutorials/colors/colormapnorms.html
    norm=colors.Normalize()
    #norm=colors.PowerNorm(gamma=2)
    #norm=colors.LogNorm()

    # images
    fig, ax1 = plt.subplots(nrows=1, figsize=(6, 5.4))
    im = ax1.imshow(ct, cmap=cmap_ct, alpha=1.0)
    im = ax1.imshow(ctvi, cmap=cmap, norm=norm, vmax=1.0)

    fig.colorbar(im)
    plt.show()

# --------------------------------------------------------------------------
if __name__ == '__main__':
    ctvi_slice_nbr_click()
