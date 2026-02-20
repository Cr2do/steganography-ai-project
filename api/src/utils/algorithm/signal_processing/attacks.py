import cv2
import numpy as np

class ImageAttacks:
    """
    Simulates various attacks on images to test steganography robustness.
    """

    @staticmethod
    def jpeg_compression(image: np.ndarray, quality: int = 80) -> np.ndarray:
        """
        Simulates JPEG compression.
        :param quality: 0-100 (lower is more compression)
        """
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
        result, encimg = cv2.imencode('.jpg', image, encode_param)
        decimg = cv2.imdecode(encimg, 1)
        return decimg

    @staticmethod
    def gaussian_noise(image: np.ndarray, mean: float = 0, var: float = 0.01) -> np.ndarray:
        """
        Adds Gaussian noise.
        """
        row, col, ch = image.shape
        sigma = var ** 0.5
        gauss = np.random.normal(mean, sigma, (row, col, ch))
        gauss = gauss.reshape(row, col, ch)
        noisy = image.astype(np.float32) / 255.0 + gauss
        noisy = np.clip(noisy, 0, 1)
        return (noisy * 255).astype(np.uint8)

    @staticmethod
    def crop(image: np.ndarray, percentage: float = 0.1) -> np.ndarray:
        """
        Crops the image border by a percentage.
        Note: This changes image dimensions, which might break some stego algos 
        unless they are robust to resizing/cropping or if we pad it back.
        For this pipeline, we will pad it back to original size with black borders 
        to simulate "loss of data" but keep dimensions for the algo.
        """
        h, w = image.shape[:2]
        crop_h = int(h * percentage)
        crop_w = int(w * percentage)
        
        # Crop center
        cropped = image[crop_h:h-crop_h, crop_w:w-crop_w]
        
        # Pad back to original size (simulating data loss at borders)
        top = crop_h
        bottom = h - (crop_h + cropped.shape[0])
        left = crop_w
        right = w - (crop_w + cropped.shape[1])
        
        padded = cv2.copyMakeBorder(cropped, top, bottom, left, right, cv2.BORDER_CONSTANT, value=[0, 0, 0])
        # Ensure exact original size (sometimes rounding errors occur)
        return cv2.resize(padded, (w, h))

    @staticmethod
    def resize(image: np.ndarray, scale: float = 0.5) -> np.ndarray:
        """
        Resizes image down and then back up.
        """
        h, w = image.shape[:2]
        new_h, new_w = int(h * scale), int(w * scale)
        resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
        back_scaled = cv2.resize(resized, (w, h), interpolation=cv2.INTER_LINEAR)
        return back_scaled
