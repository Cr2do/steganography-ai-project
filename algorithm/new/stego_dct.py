import cv2
import numpy as np
from utils import text_to_bin, bin_to_text

class DCTSteganography:
    """
    Implements DCT based steganography.
    Robustness: Moderate against JPEG compression.
    Technique: Embeds bits in mid-frequency coefficients of 8x8 DCT blocks.
    """
    def __init__(self):
        self.block_size = 8
        self.u1, self.v1 = 4, 5 
        self.u2, self.v2 = 5, 4

    def embed(self, image_path, text, output_path):
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Image not found: {image_path}")
            
        h, w = img.shape[:2]
        h = (h // 8) * 8
        w = (w // 8) * 8
        img = img[:h, :w]
        
        ycrcb = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb)
        y, cr, cb = cv2.split(ycrcb)
        y_float = np.float32(y)
        
        binary_text = text_to_bin(text)
        terminator = '1111111111111110'
        full_msg = binary_text + terminator
        
        max_bits = (h // 8) * (w // 8)
        
        if len(full_msg) > max_bits:
             full_msg = full_msg[:max_bits]
        else:
             repeats = max_bits // len(full_msg)
             full_msg = full_msg * repeats + full_msg[:max_bits % len(full_msg)]

        idx = 0
        for i in range(0, h, 8):
            for j in range(0, w, 8):
                if idx < len(full_msg):
                    block = y_float[i:i+8, j:j+8]
                    dct_block = cv2.dct(block)
                    
                    c1 = dct_block[self.u1, self.v1]
                    c2 = dct_block[self.u2, self.v2]
                    
                    bit = int(full_msg[idx])
                    P = 25 
                    
                    if bit == 0:
                        if c1 <= c2 + P:
                            diff = (c2 + P - c1) / 2.0
                            c1 += diff + 1
                            c2 -= diff + 1
                    else: 
                        if c1 + P >= c2:
                            diff = (c1 + P - c2) / 2.0
                            c2 += diff + 1
                            c1 -= diff + 1
                            
                    dct_block[self.u1, self.v1] = c1
                    dct_block[self.u2, self.v2] = c2
                    
                    y_float[i:i+8, j:j+8] = cv2.idct(dct_block)
                    idx += 1
        
        y_new = np.clip(y_float, 0, 255).astype(np.uint8)
        ycrcb_new = cv2.merge([y_new, cr, cb])
        img_new = cv2.cvtColor(ycrcb_new, cv2.COLOR_YCrCb2BGR)
        
        cv2.imwrite(output_path, img_new)
        print(f"Saved DCT stego image to {output_path}")

    def extract(self, image_path):
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Image not found: {image_path}")
            
        h, w = img.shape[:2]
        h = (h // 8) * 8
        w = (w // 8) * 8
        img = img[:h, :w]
        
        ycrcb = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb)
        y, cr, cb = cv2.split(ycrcb)
        y_float = np.float32(y)
        
        binary_text = ""
        
        for i in range(0, h, 8):
            for j in range(0, w, 8):
                block = y_float[i:i+8, j:j+8]
                dct_block = cv2.dct(block)
                
                c1 = dct_block[self.u1, self.v1]
                c2 = dct_block[self.u2, self.v2]
                
                if c1 > c2:
                    binary_text += "0"
                else:
                    binary_text += "1"
                    
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
