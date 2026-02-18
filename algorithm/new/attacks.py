import cv2
import numpy as np

def attack_jpeg_compression(image_path, output_path, quality=50):
    """Simulates JPEG compression."""
    img = cv2.imread(image_path)
    if img is None:
        return False
    cv2.imwrite(output_path, img, [cv2.IMWRITE_JPEG_QUALITY, quality])
    return True

def attack_resize(image_path, output_path, scale=0.5):
    """Simulates resizing (scaling down)."""
    img = cv2.imread(image_path)
    if img is None:
        return False
    h, w = img.shape[:2]
    new_dim = (int(w * scale), int(h * scale))
    resized = cv2.resize(img, new_dim, interpolation=cv2.INTER_LINEAR)
    cv2.imwrite(output_path, resized)
    return True

def attack_crop(image_path, output_path, crop_percent=0.1):
    """Simulates cropping from the center."""
    img = cv2.imread(image_path)
    if img is None:
        return False
    h, w = img.shape[:2]
    
    # Crop 10% from each side
    h_crop = int(h * crop_percent)
    w_crop = int(w * crop_percent)
    
    cropped = img[h_crop:h-h_crop, w_crop:w-w_crop]
    cv2.imwrite(output_path, cropped)
    return True

def attack_noise(image_path, output_path, mean=0, var=0.01):
    """Adds Gaussian noise."""
    img = cv2.imread(image_path)
    if img is None:
        return False
    img = img.astype(np.float32) / 255.0
    noise = np.random.normal(mean, var ** 0.5, img.shape)
    noisy_img = img + noise
    noisy_img = np.clip(noisy_img, 0, 1)
    noisy_img = (noisy_img * 255).astype(np.uint8)
    cv2.imwrite(output_path, noisy_img)
    return True
