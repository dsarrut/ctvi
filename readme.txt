
First test

0.0.mhd = inhale
50.0.mhd = exhale
result_50.0_0.0.mhd = 0.0 inhale resampled like exhale

clitkAffineTransform -i 0.0.mhd -o 0.0_resampled.mhd --like result_50.0_0.0.mhd
clitkAffineTransform -i 50.0.mhd -o 50.0_resampled.mhd --like result_50.0_0.0.mhd
clitkAffineTransform -i lungs_50.0.mhd -o lungs_50.0_resampled.mhd --like result_50.0_0.0.mhd --interp=0

./ventil/ctvi.py -e PJ9/50.0_resampled.mhd -i PJ9/result_50.0_0.0.mhd -m PJ9/lungs_50.0_resampled.mhd -o output/a.mhd -s 2


