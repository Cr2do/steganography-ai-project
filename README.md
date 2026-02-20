# steganography-ai-project
TPI Project on Steganography applied with AI.

The Excel files contain the comparison between the algorithms and the attacks: https://docs.google.com/spreadsheets/d/1R2CHtjK39hvFnB3a3WBnKBfjhUNpplx9/edit?gid=1022831993#gid=1022831993






The concept of mixing DWT and SVD was popularized by Ganic and Eskicioglu. While their specific method differed slightly (they added watermark singular values to host singular values), they established the field.

Paper: Robust embedding of visual watermarks using discrete wavelet transform and singular value decomposition
Authors: E. Ganic and A. M. Eskicioglu
Year: 2004
Journal: Journal of Electronic Imaging



Paper: A robust image watermarking scheme based on singular value decomposition using genetic algorithm (and similar titles)
Authors: Lai, C. C., & Tsai, C. C.
Year: 2010
Context: They refined the block-based SVD approach to fix issues in the original Ganic paper.


Implementation SIFT ou correction d'homographie

=> Signal Processing

=> Computer Vision

=> Deep Learning



### Analyse des algorithmes


- LSB
    - Il devient pas utile quand on dégrade beaucoup l'image
- DCT
    - La premiere version de cet algo ne fonctionne pas bien car il utilise des nombre à virgule pour faire la tranformation en bit. \
      Or celà cause des pertes de bit
    - De plus l'application du **coeff % 2** affaiblit la conversion
    - Solution : utiliser QIM ( Quantization Index Modulation )