#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import click
import itk
from ctvi_helpers import *

# --------------------------------------------------------------------------
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])
@click.command(context_settings=CONTEXT_SETTINGS)
@click.option('--input', '-i')
@click.option('--output', '-o')
def dilat(input, output):
    '''
    Doc todo
    '''

    print(input)
    ctvi = itk.imread(input)

    ImageType = type(ctvi)
    Dimension = ctvi.GetImageDimension()

    radiusValue = 1
    StructuringElementType = itk.FlatStructuringElement[Dimension]
    structuringElement = StructuringElementType.Ball(radiusValue)

    grayscaleFilter = itk.GrayscaleDilateImageFilter[
        ImageType, ImageType, StructuringElementType].New()
    grayscaleFilter.SetInput(ctvi)
    grayscaleFilter.SetKernel(structuringElement)
    grayscaleFilter.Update()

    o = grayscaleFilter.GetOutput()

    o = itk.array_from_image(o)
    c = itk.array_from_image(ctvi)
    o[c>0.0] = 0
    o = c+o

    o = itk.image_from_array(o)
    o.CopyInformation(ctvi)
    itk.imwrite(o, output)

# --------------------------------------------------------------------------
if __name__ == '__main__':
    dilat()
