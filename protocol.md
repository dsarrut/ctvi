

# image conversion, pre-treatment, database

- Use inhale/exhale both mediastinal/parenchyma reconstructions
- warning spacing not the same bw inhale, exhale
- how to organise the database ?
  - 1 folder per patient
  - subfolders : 'dicom' 'mhd'
  - copy dicom + initial mhd 
  - on a computer at CLB ? (everyone an then copy to do his own tests)


```
clitkDicom2Image -o inhale_mediastinal.mhd img/Thorax_INSPI_2.0mm_MEDIASTIN/*dcm
clitkDicom2Image -o inhale_parenchyma.mhd img/Thorax_INSPI_1mm_PARENCHYME/*dcm

clitkDicom2Image -o exhale_mediastinal.mhd img/Thorax_EXPI_2.0mm_MEDIASTIN/*dcm
clitkDicom2Image -o exhale_parenchyma.mhd img/Thorax_EXPI_1mm_PARENCHYME/*dcm
```


# masks

- masks (ideally): patient bones lungs left_lung right_lung trachea motion_mask
  - maybe important to separate left and right lung
  - seed for trachea still manual
- need masks on both inhale and exhale
- better to extract masks on mediastinal images ? 
- resample final image/mask like inhale_parenchyma support/spacing 
- maybe useful to gather all masks into a single labels images and make a dicom ?


Simon's cmd lines: 
```
clitkExtractPatient -i inhale_mediastinal.mhd -o inhale_patient.mhd --noAutoCrop  -a inhale.afdb

clitkExtractLung -i inhale_mediastinal.mhd -o inhale_lung.mhd  -a inhale.afdb --noAutoCrop --type 0 --outputTrachea inhale_trachea.mha  --verboseRG --verboseStep -v --seed -8,-130,-117 --doNotCheckTracheaVolume --upperThresholdForTrachea -950 

clitkImageConvert inhale_mediastinal.mhd inhale_float.mha -t float

clitkExtractBones -i inhale_float.mha -o inhale_bones.mhd -a inhale.afdb --lower1 120 --upper1 2000 --lower2 80 --upper2 2000 --smooth --time 0.0625 --noAutoCrop

clitkMotionMask -i inhale_float.mha -o inhale_mm.mhd --featureLungs inhale_lung.mhd --featureBones inhale_bones.mhd --fillingLevel 94 --offset 0,-50,0 --pad --writeFeature inhale_feature.mhd --writeEllips=inhale_ellipse.mhd --writeDistMap=inhale_distmap.mhd --writeGrownEllips=inhale_GrownEllipsImage.mhd  -v --axes 100,30,250
```

```
clitkExtractPatient -i exhale_mediastinal.mhd -o exhale_patient.mhd --noAutoCrop  -a exhale.afdb

clitkExtractLung -i exhale_mediastinal.mhd -o exhale_lung.mhd  -a exhale.afdb --noAutoCrop --type 0 --outputTrachea exhale_trachea.mha  --verboseRG --verboseStep -v --seed -4,-151,-25 --doNotCheckTracheaVolume --upperThresholdForTrachea -950

clitkImageConvert exhale_mediastinal.mhd exhale_float.mha -t float

clitkExtractBones -i exhale_float.mha -o exhale_bones.mhd -a exhale.afdb --lower1 120 --upper1 2000 --lower2 80 --upper2 2000 --smooth --time 0.0625 --noAutoCrop

clitkMotionMask -i exhale_float.mha -o exhale_mm.mhd --featureLungs exhale_lung.mhd --featureBones exhale_bones.mhd --fillingLevel 94 --offset 0,-50,0 --pad --writeFeature exhale_feature.mhd --writeEllips=exhale_ellipse.mhd --writeDistMap=exhale_distmap.mhd --writeGrownEllips=exhale_GrownEllipsImage.mhd  -v --axes 100,30,250
```

The ctvi.py scripts need to have the mask with the exact same spacing/support for all images:

```
clitkAffineTransform -i exhale_lung.mhd -o exhale_lung_resampled.mhd --like exhale_parenchyma.mhd
```


# registration

- where is the elastix + plugin version ? 

- rigid parameters

```
./elastix -f exhale_parenchyma.mhd -m inhale_parenchyma.mhd -out output/output_rigid1 -p params/rigid_reg_params_elastix.txt -fMask exhale_patient.mhd
```


- deformable parameters
  - use inhale_parenchyma.mhd and exhale_parenchyma
  - not the same spacing: resample ? 
  - fixed=inhale ; moving=exhale (better that way ?)
    - in Eslick2018, inhale=moving, exhale=fixed
  - mask: inhale_mm + inhale_patient -> multi bspline
  - other params ? See file Par0016.multibsplines.lung.sliding.txt


```
./elastix -f exhale_parenchyma.mhd -m inhale_parenchyma.mhd -out output_nonrigid9 -p params/dir_bspline5.txt -t0 output_rigid1/TransformParameters.0.txt -fMask exhale_mm.mhd
```


- results
  - which reference image ? exhale or inhale ? -> exhale in most of the papers
  - need inhale image deformed to exhale -> need inverse of the DVF ? 
  - with same spacing/support than exhale
  - need Jacobian image 

```
clitkSetBackground -i output_nonrigid9/result.0.mhd -o output_nonrigid9/result.0_bg.mhd -m exhale_lung.mhd -p -1000
```

For use mediastinal instead of parenchyma:
```
./transformix -in exhale_mediastinal.mhd -tp output_nonrigid9/TransformParameters.0.txt -out output_nonrigid9_med
clitkAffineTransform -i output_nonrigid9_med/result.mhd -o output_nonrigid9_med/result_resampled.mhd --like exhale_mediastinal.mhd
clitkSetBackground -i output_nonrigid9_med/result_resampled.mhd -o output_nonrigid9_med/result_resampled_bg.mhd -m exhale_lung.mhd -p -1000
```

  
- is it possible to check/validate the results ? 


# ctvi

- input: inhale, exhale, exhale_deformed, inhale_lung, exhale_lung, [later: jacobian]

- method Esclick2018 (HU based)
  CTVI_delta_HU = (exh-inh) / (inh+1000) * rho
  rho = (ex+1000)/1000
  --> should we really use this rho scaling ? or stay in absolute air volume changes ? 
  
- post-processing: median filter, which radius ? 
  dilate value at boundaries before to avoid using value out of the masks
  
- normalisation ? 
  - in Kipritidis2019: 90th percentile
  - Maciej propose to normalise by lung air volume difference (bw exhale and inhale) 
  

Erode the mask before to avoid border effect
```
../ventil/erode_mask.py -i exhale_lung.mhd -o exhale_lung_eroded.mhd -r 1
../ventil/erode_mask.py -i exhale_lung_resampled.mhd -o exhale_lung_resampled_eroded.mhd -r 1
```

  
```
../ventil/ctvi.py -e exhale_mediastinal.mhd -i output_nonrigid9_med/result_resampled.mhd -m exhale_lung_eroded.mhd -r 2 -o output_ctvi/b_rho.mhd --rho_normalize

```

Choice: 
- erode lung mask before
- use Eslick2018 with rho scaling
- apply median filter r=2 with dilatation before
- reapply mask after this median filter
- remove 10% higher values (not representative, near vessels)
  

# ctvi regional index

todo


