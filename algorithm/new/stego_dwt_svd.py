import cv2
import numpy as np
import pywt
from utils import text_to_bin, bin_to_text

class DWTSVDSteganography:
    """
    Implements DWT-SVD based steganography.
    Robustness: High against compression, noise, scaling.
    Technique: Embeds bits in the singular values of DWT sub-band blocks using QIM.
    """
    def __init__(self, block_size=4, q_step=20):
        self.block_size = block_size
        self.q_step = q_step

    def embed(self, image_path, text, output_path):
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Image not found: {image_path}")
        
        # Resize to be multiple of block_size * 2
        h, w = img.shape[:2]
        h_new = (h // (self.block_size * 2)) * (self.block_size * 2)
        w_new = (w // (self.block_size * 2)) * (self.block_size * 2)
        img = cv2.resize(img, (w_new, h_new))
        
        ycrcb = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb)
        y, cr, cb = cv2.split(ycrcb)
        
        coeffs = pywt.dwt2(np.float32(y), 'haar')
        LL, (LH, HL, HH) = coeffs
        
        # Embed in HL sub-band
        sub_h, sub_w = HL.shape
        max_bits = (sub_h // self.block_size) * (sub_w // self.block_size)
        
        binary_text = text_to_bin(text)
        terminator = '1111111111111110'
        full_msg = binary_text + terminator
        
        if len(full_msg) > max_bits:
            print(f"Warning: Text too long. Truncating. Max bits: {max_bits}")
            full_msg = full_msg[:max_bits]
        else:
            repeats = max_bits // len(full_msg)
            full_msg = full_msg * repeats + full_msg[:max_bits % len(full_msg)]
            
        idx = 0
        HL_new = HL.copy()
        
        for i in range(0, sub_h, self.block_size):
            for j in range(0, sub_w, self.block_size):
                if idx < len(full_msg):
                    block = HL[i:i+self.block_size, j:j+self.block_size]
                    
                    u, s, vt = np.linalg.svd(block)
                    val = s[0]
                    bit = int(full_msg[idx])
                    
                    # QIM
                    k = round(val / self.q_step)
                    if k % 2 != bit:
                        k += 1
                        
                    s[0] = k * self.q_step
                    
                    block_new = u @ np.diag(s) @ vt
                    HL_new[i:i+self.block_size, j:j+self.block_size] = block_new
                    
                    idx += 1
        
        coeffs_new = LL, (LH, HL_new, HH)
        y_new = pywt.idwt2(coeffs_new, 'haar')
        
        y_new = np.clip(y_new, 0, 255).astype(np.uint8)
        ycrcb_new = cv2.merge([y_new, cr, cb])
        img_new = cv2.cvtColor(ycrcb_new, cv2.COLOR_YCrCb2BGR)
        
        cv2.imwrite(output_path, img_new)
        print(f"Saved DWT-SVD stego image to {output_path}")

    def extract(self, image_path):
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Image not found: {image_path}")
            
        ycrcb = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb)
        y, cr, cb = cv2.split(ycrcb)
        
        coeffs = pywt.dwt2(np.float32(y), 'haar')
        LL, (LH, HL, HH) = coeffs
        
        sub_h, sub_w = HL.shape
        binary_text = ""
        
        for i in range(0, sub_h, self.block_size):
            for j in range(0, sub_w, self.block_size):
                block = HL[i:i+self.block_size, j:j+self.block_size]
                
                u, s, vt = np.linalg.svd(block)
                val = s[0]
                
                k = round(val / self.q_step)
                bit = k % 2
                binary_text += str(bit)
        
        terminator = '1111111111111110'
        
        candidates = binary_text.split(terminator)
        for cand in candidates:
            if len(cand) > 0:
                try:
                    if len(cand) % 8 == 0:
                        txt = bin_to_text(cand)
                        if len(txt) > 0:
                            return txt
                except:
                    pass
            
        idx = binary_text.find(terminator)
        if idx != -1:
            return bin_to_text(binary_text[:idx])
            
        return "No message found"
