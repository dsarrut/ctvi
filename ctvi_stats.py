#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import click
from ctvi_helpers import *
import itk

# --------------------------------------------------------------------------
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])
@click.command(context_settings=CONTEXT_SETTINGS)
@click.option('--exhale', '-e')
@click.option('--inhale', '-i')
@click.option('--inh2exh', '-t', help='Inhale transformed to exhale')
@click.option('--ctvi')
@click.option('--lung_mask_exh')
@click.option('--lung_mask_inh')
def ctvi_stats(exhale, inhale, inh2exh, ctvi, lung_mask_exh, lung_mask_inh):
    '''
    Doc todo
    '''

    exhale_img = itk.imread(exhale)
    inhale_img = itk.imread(inhale)
    inh2exh_img = itk.imread(inh2exh)
    lung_exh_img = itk.imread(lung_mask_exh)
    lung_inh_img = itk.imread(lung_mask_inh)
    ctvi_img = itk.imread(ctvi)

    exh = itk.array_from_image(exhale_img)
    inh = itk.array_from_image(inhale_img)
    inh2exh = itk.array_from_image(inh2exh_img)
    ctvi = itk.array_from_image(ctvi_img)
    lung_exh = itk.array_from_image(lung_exh_img)
    lung_inh = itk.array_from_image(lung_inh_img)

    # exhale image 
    exh_pixel_vol = pix_vol(exhale_img)
    mask_exh = lung_exh>0   # initial lung mask
    mask_ctvi = ctvi>0   # final CTVI lung mask (after erosion etc)
    exh_lung_vol = exh_pixel_vol*len(exh[mask_exh])*1e-6
    exh_ctvi_lung_vol = exh_pixel_vol*len(exh[mask_ctvi])*1e-6
    exh_lung_mass = approx_mass(exh_pixel_vol, exh, mask_exh)
    exh_ctvi_lung_mass = approx_mass(exh_pixel_vol, exh, mask_ctvi)

    # inhale image 
    inh_pixel_vol = pix_vol(inhale_img)
    mask_inh = lung_inh>0   # initial lung mask
    inh_lung_vol = inh_pixel_vol*len(inh[mask_inh])*1e-6
    inh_lung_mass = approx_mass(inh_pixel_vol, inh, mask_inh)

    # transformed inhale image 
    inh2exh_pixel_vol = pix_vol(inh2exh_img)
    inh2exh_lung_vol = inh2exh_pixel_vol*len(inh[mask_exh])*1e-6
    inh2exh_ctvi_lung_vol = inh_pixel_vol*len(inh[mask_ctvi])*1e-6
    inh2exh_lung_mass = approx_mass(inh2exh_pixel_vol, inh2exh, mask_exh)
    inh2exh_ctvi_lung_mass = approx_mass(inh2exh_pixel_vol, inh2exh, mask_ctvi)

    print(f'Volume exhale CT initial {exh_lung_vol:.3f} L')
    print(f'Volume exhale CT final {exh_ctvi_lung_vol:.3f} L')
    print(f'Volume inhale CT initial {inh_lung_vol:.3f} L')
    #print(f'Volume inh2exh CT initial {inh2exh_lung_vol:.3f} L') # <- check like exh

    print(f'Approx mass exhale CT initial {exh_lung_mass:.3f} g')
    print(f'Approx mass exhale CT final {exh_ctvi_lung_mass:.3f} g')
    print(f'Approx mass inhale CT initial {inh_lung_mass:.3f} g')
    #print(f'Approx mass inhale_2_exhale CT initial {inh2exh_lung_mass:.3f} g')
    #print(f'Approx mass inhale_2_exhale CT final {inh2exh_ctvi_lung_mass:.3f} g')

    

# --------------------------------------------------------------------------
if __name__ == '__main__':
    ctvi_stats()
