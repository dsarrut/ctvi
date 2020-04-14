
First test

0.0.mhd = inhale
50.0.mhd = exhale
result_50.0_0.0.mhd = 0.0 inhale resampled like exhale

clitkAffineTransform -i 0.0.mhd -o 0.0_resampled.mhd --like result_50.0_0.0.mhd
clitkAffineTransform -i 50.0.mhd -o 50.0_resampled.mhd --like result_50.0_0.0.mhd
clitkAffineTransform -i lungs_50.0.mhd -o lungs_50.0_resampled.mhd --like result_50.0_0.0.mhd --interp=0

./ctvi_slicer.py -i ../output/b.mhd --ct ../CC10/exhale.mhd -m ../CC10/lung.mhd -s 0 -a 0 --slice_step 1 --slice_stop -2 -o ../png/axial
./ctvi_slicer.py -i ../output/b.mhd --ct ../CC10/exhale.mhd -m ../CC10/lung.mhd -s 0 -a 1 --slice_step 1 --slice_stop -2 -o ../png/sagittal
./ctvi_slicer.py -i ../output/b.mhd --ct ../CC10/exhale.mhd -m ../CC10/lung.mhd -s 0 -a 2 --slice_step 1 --slice_stop -2 -o ../png/coronal
