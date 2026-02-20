import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim

def calculate_psnr(original: np.ndarray, stego: np.ndarray) -> float:
    """
    Calculate Peak Signal-to-Noise Ratio (PSNR).
    Higher is better. Typical values for steganography: 30-50 dB.
    """
    mse = np.mean((original - stego) ** 2)
    if mse == 0:
        return 100.0  # Images are identical
    max_pixel = 255.0
    psnr = 20 * np.log10(max_pixel / np.sqrt(mse))
    return float(psnr)

def calculate_ssim(original: np.ndarray, stego: np.ndarray) -> float:
    """
    Calculate Structural Similarity Index (SSIM).
    Range: [-1, 1]. 1 means identical.
    """
    # Convert to grayscale for SSIM calculation as it's perceptual
    gray_original = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)
    gray_stego = cv2.cvtColor(stego, cv2.COLOR_BGR2GRAY)
    
    score, _ = ssim(gray_original, gray_stego, full=True)
    return float(score)

def calculate_mse(original: np.ndarray, stego: np.ndarray) -> float:
    """
    Calculate Mean Squared Error (MSE).
    Lower is better. 0 means identical.
    """
    mse = np.mean((original - stego) ** 2)
    return float(mse)
