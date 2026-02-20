import cv2
import numpy as np
import pywt
import hashlib
import hmac
from .utils import text_to_bin, bin_to_text

class DWTSVDSteganography:
    """
    Production-Grade DWT-SVD Steganography.
    Features:
    - Strict Chain Check.
    - Confidence Threshold (> 60%).
    - Zero False Positive Strategy.
    - HMAC Integrity Check.
    """
    def __init__(self, block_size=4, q_step=50):
        self.block_size = block_size
        self.q_step = q_step
        self.MAGIC = '0101001101010100' # "STGO"
        self.MAX_CHARS = 20
        self.SECRET_KEY = b'my_secret_key_123' # In production, load from env

    def _embed_bit(self, block, bit):
        u, s, vt = np.linalg.svd(block)
        val = s[0]
        k = round(val / self.q_step)
        if k % 2 != bit:
            k += 1
        s[0] = k * self.q_step
        return u @ np.diag(s) @ vt

    def _extract_bit(self, block):
        u, s, vt = np.linalg.svd(block)
        val = s[0]
        k = round(val / self.q_step)
        return k % 2

    def _calculate_hmac(self, text):
        """Calculates HMAC-SHA256 of the text (truncated to 16 bits for embedding space)."""
        h = hmac.new(self.SECRET_KEY, text.encode('utf-8'), hashlib.sha256)
        digest = h.hexdigest()
        return bin(int(digest[:4], 16))[2:].zfill(16)

    def embed(self, img, text):
        """
        Embeds text into the image using DWT-SVD.
        Payload Structure: MAGIC (16) + LEN (16) + HMAC (16) + MSG (N)
        """
        if len(text) > self.MAX_CHARS:
            raise ValueError(f"Text too long! Max {self.MAX_CHARS} chars allowed.")
            
        if img is None:
            raise ValueError("Image is None")
        
        h, w = img.shape[:2]
        h_new = (h // (self.block_size * 2)) * (self.block_size * 2)
        w_new = (w // (self.block_size * 2)) * (self.block_size * 2)
        img = cv2.resize(img, (w_new, h_new))
        
        ycrcb = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb)
        y, cr, cb = cv2.split(ycrcb)
        
        coeffs = pywt.dwt2(np.float32(y), 'haar')
        LL, (LH, HL, HH) = coeffs
        
        sub_h, sub_w = HL.shape
        max_bits = (sub_h // self.block_size) * (sub_w // self.block_size)
        
        msg_bits = text_to_bin(text)
        length_bits = format(len(msg_bits), '016b')
        hmac_bits = self._calculate_hmac(text)
        
        packet = self.MAGIC + length_bits + hmac_bits + msg_bits
        packet_len = len(packet)
        
        if packet_len > max_bits:
            raise ValueError(f"Text too long! Image can hold {max_bits} bits, needed {packet_len}.")
            
        full_stream = packet * (max_bits // packet_len)
        remainder = max_bits - len(full_stream)
        full_stream += packet[:remainder]
        
        idx = 0
        HL_new = HL.copy()
        
        for i in range(0, sub_h, self.block_size):
            for j in range(0, sub_w, self.block_size):
                if idx < len(full_stream):
                    block = HL[i:i+self.block_size, j:j+self.block_size]
                    bit = int(full_stream[idx])
                    block_new = self._embed_bit(block, bit)
                    HL_new[i:i+self.block_size, j:j+self.block_size] = block_new
                    idx += 1
        
        coeffs_new = LL, (LH, HL_new, HH)
        y_new = pywt.idwt2(coeffs_new, 'haar')
        y_new = np.clip(y_new, 0, 255).astype(np.uint8)
        ycrcb_new = cv2.merge([y_new, cr, cb])
        img_new = cv2.cvtColor(ycrcb_new, cv2.COLOR_YCrCb2BGR)
        
        return img_new

    def extract(self, img):
        """
        Extracts text from the image using DWT-SVD.
        Verifies HMAC integrity.
        """
        if img is None:
            raise ValueError("Image is None")
            
        h, w = img.shape[:2]
        print("Scanning for signal (DWT)...")
        
        for dy in range(4):
            for dx in range(4):
                if h - dy < 16 or w - dx < 16: continue
                
                img_crop = img[dy:h, dx:w]
                ycrcb = cv2.cvtColor(img_crop, cv2.COLOR_BGR2YCrCb)
                y, cr, cb = cv2.split(ycrcb)
                coeffs = pywt.dwt2(np.float32(y), 'haar')
                LL, (LH, HL, HH) = coeffs
                sub_h, sub_w = HL.shape
                
                all_bits = []
                count = 0
                limit = 50000
                
                for i in range(0, sub_h, self.block_size):
                    for j in range(0, sub_w, self.block_size):
                        if count >= limit: break
                        if i + self.block_size > sub_h or j + self.block_size > sub_w: continue
                        block = HL[i:i+self.block_size, j:j+self.block_size]
                        all_bits.append(self._extract_bit(block))
                        count += 1
                    if count >= limit: break
                
                if len(all_bits) < 64: continue
                
                bit_stream = "".join(map(str, all_bits))
                
                start_search = 0
                while True:
                    found_idx = bit_stream.find(self.MAGIC, start_search)
                    if found_idx == -1: break
                    
                    # Header is now 48 bits
                    if found_idx + 48 > len(bit_stream): break
                    
                    length_bin = bit_stream[found_idx+16 : found_idx+32]
                    hmac_bin = bit_stream[found_idx+32 : found_idx+48]
                    
                    try:
                        msg_len_bits = int(length_bin, 2)
                    except:
                        start_search = found_idx + 1
                        continue
                        
                    if msg_len_bits <= 0 or msg_len_bits > 160:
                        start_search = found_idx + 1
                        continue
                        
                    packet_len = 48 + msg_len_bits
                    
                    next_packet_idx = found_idx + packet_len
                    if next_packet_idx + 16 <= len(bit_stream):
                        next_magic = bit_stream[next_packet_idx : next_packet_idx + 16]
                        diff = sum(1 for a, b in zip(next_magic, self.MAGIC) if a != b)
                        if diff > 2:
                            start_search = found_idx + 1
                            continue
                    
                    full_bits = []
                    for i in range(0, sub_h, self.block_size):
                        for j in range(0, sub_w, self.block_size):
                            if i + self.block_size > sub_h or j + self.block_size > sub_w: continue
                            block = HL[i:i+self.block_size, j:j+self.block_size]
                            full_bits.append(self._extract_bit(block))
                    
                    aligned_bits = full_bits[found_idx:]
                    num_copies = len(aligned_bits) // packet_len
                    
                    if num_copies < 1:
                        start_search = found_idx + 1
                        continue
                    
                    bits_matrix = np.array(aligned_bits[:num_copies * packet_len])
                    bits_matrix = bits_matrix.reshape((num_copies, packet_len))
                    votes = np.mean(bits_matrix, axis=0)
                    final_bits = (votes > 0.5).astype(int)
                    confidence = np.mean(np.abs(votes - 0.5)) * 2
                    
                    # CONFIDENCE THRESHOLD
                    if confidence < 0.6:
                        start_search = found_idx + 1
                        continue
                    
                    payload_bits = final_bits[48:]
                    payload_str = "".join(map(str, payload_bits))
                    
                    try:
                        recovered_text = bin_to_text(payload_str)
                        if len(recovered_text) > 0:
                            # Verify HMAC
                            expected_hmac = self._calculate_hmac(recovered_text)
                            if expected_hmac == hmac_bin:
                                print(f"Signal found & Verified at Grid({dy},{dx}) Offset {found_idx}. Confidence: {confidence:.2f}")
                                return recovered_text
                            else:
                                print(f"Signal found but HMAC failed. Possible tampering.")
                    except:
                        pass
                    
                    start_search = found_idx + 1
                        
        return None
