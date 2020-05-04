#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import click
from ctvi_helpers import *
import itk

# --------------------------------------------------------------------------
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])
@click.command(context_settings=CONTEXT_SETTINGS)
@click.option('--image', '-i', required=True)
@click.option('--mask', '-m', required=True)
def ctvi_stats(image, mask):
    '''
    Doc todo
    '''

    img = itk.imread(image)
    mask = itk.imread(mask)

    check_same_geometry(img, mask)

    s = lung_mass_and_volume(img, mask)
    print(f'{s.volume_L:.2f} L  {s.mass_g:.2f} g  '
          f' {s.pixels_count} pixels  {s.pixel_volume_mm3:.2f} mm3')

# --------------------------------------------------------------------------
if __name__ == '__main__':
    ctvi_stats()
