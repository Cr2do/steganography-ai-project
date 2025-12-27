### Analyse des algorithmes


- LSB
  - Il devient pas utile quand on dégrade beaucoup l'image
- DCT
  - La premiere version de cet algo ne fonctionne pas bien car il utilise des nombre à virgule pour faire la tranformation en bit. \
  Or celà cause des pertes de bit
  - De plus l'application du **coeff % 2** affaiblit la conversion
  - Solution : utiliser QIM ( Quantization Index Modulation )