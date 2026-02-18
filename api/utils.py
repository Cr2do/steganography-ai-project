import numpy as np
import cv2

def text_to_bin(text):
    """Convert text to binary string."""
    return ''.join(format(ord(char), '08b') for char in text)

def bin_to_text(binary):
    """Convert binary string to text."""
    chars = [binary[i:i+8] for i in range(0, len(binary), 8)]
    return ''.join(chr(int(char, 2)) for char in chars if len(char) == 8)

def str_to_array(text):
    """Convert string to numpy array of 0s and 1s."""
    bin_str = text_to_bin(text)
    return np.array([int(b) for b in bin_str], dtype=int)

def array_to_str(arr):
    """Convert numpy array of 0s and 1s to string."""
    bin_str = ''.join(map(str, arr))
    return bin_to_text(bin_str)

async def read_image(file) -> np.ndarray:
    """Reads an UploadFile and converts it to an OpenCV image."""
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Could not decode image")
    return img
