#!/usr/bin/env python3
# -----------------------------------------------------------------------------
#   Copyright (C): OpenGATE Collaboration
#   This software is distributed under the terms
#   of the GNU Lesser General  Public Licence (LGPL)
#   See LICENSE.md for further details
# -----------------------------------------------------------------------------

import itk
import click
import numpy as np
import pydicom
import os
import subprocess
import datetime

# -----------------------------------------------------------------------------
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])
@click.command(context_settings=CONTEXT_SETTINGS)

@click.option('--mhd', '-i', help='Input CTVI mhd filename', required=True,
                type=click.Path(dir_okay=False))
@click.option('--dicom', '-d', help='Input Dicom file example', required=True,
                type=click.Path(dir_okay=True))
@click.option('--output', '-o', default='outputDcm', help='Output dicom filename')

def createCTVIDicom_click(mhd, dicom, output):
    '''
    Open the CTVI mhd image (float image with value between 0 and 1.
    Take the dicom file as a model for the tags (usually dicom slice from a CT)
    Write the dicom volume as output
    '''

    ctvi = itk.imread(mhd)
    createCTVIDicom(ctvi, dicom, output)

# -----------------------------------------------------------------------------
def createCTVIDicom(ctvi, dicom, output="outputDcm"):

    dcmFiles = []
    #Load dicom files
    for root, dir, files in os.walk(dicom):
        for file in files:
            if file.endswith(".dcm"):
                dcmFiles.append(pydicom.read_file(os.path.join(root, file)))

    # skip files with no SliceLocation (eg scout views)
    slices = []
    skipcount = 0
    if len(dcmFiles) > 1:
        for f in dcmFiles:
            if hasattr(f, 'SliceLocation'):
                slices.append(f)
            else:
                skipcount = skipcount + 1

        if skipcount >0:
            print("skipped, no SliceLocation: {}".format(skipcount))

        # ensure they are in the correct order. Sort according Image Position along z
        slices = sorted(slices, key=lambda s: s[0x0020, 0x0032][2])

    if len(slices) == 0:
        print("no slice available")
        return

    #Find the studyInstanceUID and frameOfReferenceUID in order to copy back. Generate a new series instance uid
    studyInstanceUID = slices[2].StudyInstanceUID
    frameOfReferenceUID = slices[2].FrameOfReferenceUID
    newSeriesInstanceUID = pydicom.uid.generate_uid()

    #Create the output
    if not os.path.isdir(output):
        os.makedirs(output)

    # Scale the ctvi:
    ctviArray = itk.array_from_image(ctvi)
    doseScaling = np.amax(ctviArray)/(2**16-1)
    ctviArray = (ctviArray/doseScaling).astype(int)
    ctviArray = ctviArray.swapaxes(0, 2)
    ctviImage = itk.image_from_array(ctviArray.astype(float))
    ctviImage.CopyInformation(ctvi)
    itk.imwrite(ctviImage, "testctvi.mhd")

    # Compute the output dicom using clitkWrite DicomSerie
    now = datetime.datetime.now()
    bashCommand = "clitkWriteDicomSeries -i testctvi.mhd -d " + dicom + " -o " + output + " -p -e -k 0008|0060,0028|1052,0028|1053,0028|0101,0028|0102,0028|1054,0020|4000,0008|0023,0008|0033,0020|000d,0020|0052,0020|000e -t OT,0," + str(doseScaling) + ",16,15,unit,CTVI," + now.strftime("%Y%m%d") + "," + now.strftime("%H%M%S") + ".000000," + studyInstanceUID + "," + frameOfReferenceUID + "," + newSeriesInstanceUID
    #print(bashCommand)
    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()

# -----------------------------------------------------------------------------
if __name__ == '__main__':
    createCTVIDicom_click()


