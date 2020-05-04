
Goal: compute ventilation image (CTVI) from two breath holds exhale/inhale CT

* CT acquisition 

- two CTs
- Breath Hold (BH) at approx. 80% inhalation and 80% exhalation
- in Elick2018: 120 kVp, 120 mAs, 0.8 pitch
- BH time of approx. 10 sec
- FOV approx 50 cm from pharynx to stomach
- reconstruction param: 'parenchymal' and/or 'mediastinal'

* Step1: compute the DVF from exhale to inhale

- extract patient, bones and lung masks
- extract motion mask
- perform DIR like for midp (elastix, Bspline)
- use the DVF to transform the inhale image on the exhale support


* Step2: compute the CTVI

- several methods exists, see Kipritidis2019
- method1: deltaHU according to HU difference between exhale and inhale_transformed
- method2: deltaVol according to Jacobien of the DVF 

Scaling factors
- converted to an "absolute" ventilation in units proportional to mL/voxel
- eventually, apply a tissue density scaling factor

Post-processing
- almost all authors smooth final CTVI image with median filter


* Step3: visualisation and colorscale

We need a way to present the result with a meaningful colorscale. 

Convert final image to DICOM 


