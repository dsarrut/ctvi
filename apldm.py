#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import click
import itk
from box import Box
#import gatetools as gt
from ctvi_metric import *

# --------------------------------------------------------------------------
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])
@click.command(context_settings=CONTEXT_SETTINGS)
@click.option('--exhale', '-e')
@click.option('--inhale', '-i')
@click.option('--lung_mask_exhale', '-m')
@click.option('--lung_mask_inhale', '-n')
@click.option('--output', '-o')
def apldm(exhale, inhale, lung_mask_exhale, lung_mask_inhale, output):
    '''
    Doc todo
    '''

    exhale = itk.imread(exhale)
    inhale = itk.imread(inhale)
    lung_mask_exhale = itk.imread(lung_mask_exhale)
    lung_mask_inhale = itk.imread(lung_mask_inhale)

    check_same_geometry(exhale, lung_mask_exhale)
    check_same_geometry(inhale, lung_mask_inhale)

    # loop slice by slice
    #lung_mask_exhale_crop = gt.image_auto_crop(lung_mask_exhale, bg=0)
    #lung_mask_inhale_crop = gt.image_auto_crop(lung_mask_inhale, bg=0)
    #print('crop ok')
    #n_exh = lung_mask_exhale_crop.GetLargestPossibleRegion().GetSize()[2]
    #n_inh = lung_mask_inhale_crop.GetLargestPossibleRegion().GetSize()[2]
    #print(n_exh, n_inh)

    # loop on exh slices, check mask sum, if not zero, compute mean mass, store
    exh_data = itk.array_view_from_image(exhale)
    exh_mask = itk.array_view_from_image(lung_mask_exhale)
    densities = []
    for i in range(0,len(exh_data)):
        exh_slice = exh_data[i]
        mask_slice = exh_mask[i]
        if mask_slice.sum() == 0:
            continue
        s = exh_slice[mask_slice != 0].mean()
        densities.append(s)
    print(len(densities))

    # loop on inh slices,
    inh_data = itk.array_view_from_image(inhale)
    inh_mask = itk.array_view_from_image(lung_mask_inhale)
    slice_index = []
    for i in range(0, len(inh_data)):
        mask_slice = inh_mask[i]
        if mask_slice.sum() == 0:
            continue
        slice_index.append(i)
    print(len(slice_index))

    alpha = len(densities)/len(slice_index)
    print('alpha', alpha)

    exh_idx = 0
    for idx in slice_index:
        inh_slice = inh_data[idx]
        mask_slice = inh_mask[idx]
        s = inh_slice[mask_slice != 0].mean()
        d = densities[int(exh_idx)]
        r = s/d
        inh_slice[mask_slice != 0] = inh_slice[mask_slice != 0]/r
        exh_idx = exh_idx+alpha

    inh = inh_data.astype(np.float32)
    img = itk.image_from_array(inh)
    img.CopyInformation(inhale)
    itk.imwrite(img, output)

# --------------------------------------------------------------------------
if __name__ == '__main__':
    apldm()
