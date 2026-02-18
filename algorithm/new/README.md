# Robust Steganography Algorithms

This folder contains implementations of robust steganography algorithms using DCT (Discrete Cosine Transform) and DWT-SVD (Discrete Wavelet Transform - Singular Value Decomposition).

## 1. DCT Steganography (`stego_dct.py`)

### Description
This algorithm uses the Discrete Cosine Transform (DCT) to embed data into the frequency domain of the image. It operates on 8x8 blocks of the image.

### Technique
- **Transformation**: The image is converted to YCrCb color space, and the Y channel (luminance) is divided into 8x8 blocks.
- **Embedding**: We use a differential encoding scheme on two mid-frequency coefficients ($C_1$ and $C_2$) of each block.
  - To embed '0': We modify coefficients so that $C_1 > C_2 + P$.
  - To embed '1': We modify coefficients so that $C_2 > C_1 + P$.
  - $P$ is a persistence/threshold value that determines robustness vs. invisibility.

### Robustness
- **JPEG Compression**: Moderate. Since we modify mid-frequency coefficients which are preserved better than high-frequency ones during compression.
- **Scaling/Cropping**: Low. This specific implementation relies on the 8x8 grid alignment. If the image is cropped or resized without restoring the original grid, extraction will fail.

### Source / Reference
- *Koch, E., & Zhao, J. (1995). Towards robust and hidden image copyright labeling. Proceedings of 1995 IEEE Workshop on Nonlinear Signal and Image Processing.*

---

## 2. DWT-SVD Steganography (`stego_dwt_svd.py`)

### Description
This algorithm combines Discrete Wavelet Transform (DWT) and Singular Value Decomposition (SVD). It is known for high robustness against various attacks.

### Technique
- **Transformation**: The image (Y channel) is decomposed using DWT (Haar wavelet) into four sub-bands: LL, LH, HL, HH.
- **Block Processing**: The HL sub-band (vertical details) is divided into 4x4 blocks.
- **SVD**: SVD is applied to each 4x4 block ($A = U \Sigma V^T$).
- **Embedding**: The largest singular value ($\sigma_1$ in $\Sigma$) is quantized using Quantization Index Modulation (QIM).
  - We quantize $\sigma_1$ to the nearest even or odd multiple of a step size $Q$, depending on the bit to be embedded.
- **Reconstruction**: The block is reconstructed with the modified singular value, and Inverse DWT is applied.

### Robustness
- **JPEG Compression**: High.
- **Noise**: High.
- **Scaling**: Good (if resized back to original dimensions or if the watermark is extracted in a scale-invariant domain).
- **Cropping**: Moderate (depends on synchronization).

### Source / Reference
- *Ganic, E., & Eskicioglu, A. M. (2004). Robust DWT-SVD domain image watermarking: embedding data in all frequencies. Proceedings of the 2004 multimedia and security workshop on Multimedia and security.*

## Usage

See `main.py` for example usage.

```python
from stego_dwt_svd import DWTSVDSteganography

# Embed
algo = DWTSVDSteganography()
algo.embed("input.jpg", "Secret Text", "output.png")

# Extract
text = algo.extract("output.png")
print(text)
```
