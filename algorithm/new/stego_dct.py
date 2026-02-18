import cv2
import numpy as np
from utils import text_to_bin, bin_to_text

class DCTSteganography:
    """
    Production-Grade DCT Steganography.
    Features:
    - Strict Chain Check.
    - Confidence Threshold (> 60%).
    - Zero False Positive Strategy.
    """
    def __init__(self):
        self.block_size = 8
        self.u1, self.v1 = 3, 4 
        self.u2, self.v2 = 4, 3
        self.P = 50 
        self.MAGIC = '0101001101010100' # "STGO"
        self.MAX_CHARS = 20

    def _embed_bit(self, dct_block, bit):
        c1 = dct_block[self.u1, self.v1]
        c2 = dct_block[self.u2, self.v2]
        if bit == 0:
            if c1 <= c2 + self.P:
                diff = (c2 + self.P - c1) / 2.0
                c1 += diff + 1
                c2 -= diff + 1
        else: 
            if c1 + self.P >= c2:
                diff = (c1 + self.P - c2) / 2.0
                c2 += diff + 1
                c1 -= diff + 1
        dct_block[self.u1, self.v1] = c1
        dct_block[self.u2, self.v2] = c2
        return dct_block

    def _extract_bit(self, dct_block):
        c1 = dct_block[self.u1, self.v1]
        c2 = dct_block[self.u2, self.v2]
        return 0 if c1 > c2 else 1

    def embed(self, image_path, text, output_path):
        if len(text) > self.MAX_CHARS:
            raise ValueError(f"Text too long! Max {self.MAX_CHARS} chars allowed.")
            
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
        
        msg_bits = text_to_bin(text)
        length_bits = format(len(msg_bits), '016b')
        packet = self.MAGIC + length_bits + msg_bits
        packet_len = len(packet)
        
        total_blocks = (h // 8) * (w // 8)
        full_stream = packet * (total_blocks // packet_len)
        remainder = total_blocks - len(full_stream)
        full_stream += packet[:remainder]
        
        idx = 0
        for i in range(0, h, 8):
            for j in range(0, w, 8):
                if idx < len(full_stream):
                    block = y_float[i:i+8, j:j+8]
                    dct_block = cv2.dct(block)
                    bit = int(full_stream[idx])
                    dct_block = self._embed_bit(dct_block, bit)
                    y_float[i:i+8, j:j+8] = cv2.idct(dct_block)
                    idx += 1
        
        y_new = np.clip(y_float, 0, 255).astype(np.uint8)
        ycrcb_new = cv2.merge([y_new, cr, cb])
        img_new = cv2.cvtColor(ycrcb_new, cv2.COLOR_YCrCb2BGR)
        
        if output_path.lower().endswith(('.jpg', '.jpeg')):
            cv2.imwrite(output_path, img_new, [cv2.IMWRITE_JPEG_QUALITY, 95])
        else:
            cv2.imwrite(output_path, img_new)
        print(f"Saved Robust DCT stego image to {output_path}")

    def extract(self, image_path):
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Image not found: {image_path}")
            
        h, w = img.shape[:2]
        ycrcb = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb)
        y, cr, cb = cv2.split(ycrcb)
        y_float = np.float32(y)
        
        print("Scanning for signal...")
        
        for dy in range(8):
            for dx in range(8):
                all_bits = []
                count = 0
                limit = 50000 
                
                for i in range(dy, h - 7, 8):
                    for j in range(dx, w - 7, 8):
                        if count >= limit: break
                        block = y_float[i:i+8, j:j+8]
                        dct_block = cv2.dct(block)
                        all_bits.append(self._extract_bit(dct_block))
                        count += 1
                    if count >= limit: break
                
                if len(all_bits) < 64: continue
                
                bit_stream = "".join(map(str, all_bits))
                
                start_search = 0
                while True:
                    found_idx = bit_stream.find(self.MAGIC, start_search)
                    if found_idx == -1: break
                    
                    if found_idx + 32 > len(bit_stream): break
                    
                    length_bin = bit_stream[found_idx+16 : found_idx+32]
                    try:
                        msg_len_bits = int(length_bin, 2)
                    except:
                        start_search = found_idx + 1
                        continue
                        
                    if msg_len_bits <= 0 or msg_len_bits > 160:
                        start_search = found_idx + 1
                        continue
                        
                    packet_len = 32 + msg_len_bits
                    
                    next_packet_idx = found_idx + packet_len
                    if next_packet_idx + 16 <= len(bit_stream):
                        next_magic = bit_stream[next_packet_idx : next_packet_idx + 16]
                        diff = sum(1 for a, b in zip(next_magic, self.MAGIC) if a != b)
                        if diff > 2:
                            start_search = found_idx + 1
                            continue
                    
                    full_bits = []
                    for i in range(dy, h - 7, 8):
                        for j in range(dx, w - 7, 8):
                            block = y_float[i:i+8, j:j+8]
                            dct_block = cv2.dct(block)
                            full_bits.append(self._extract_bit(dct_block))
                    
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
                        # Signal too weak/noisy
                        start_search = found_idx + 1
                        continue

                    payload_bits = final_bits[32:]
                    payload_str = "".join(map(str, payload_bits))
                    
                    try:
                        recovered_text = bin_to_text(payload_str)
                        if len(recovered_text) > 0:
                             print(f"Signal found at Grid({dy},{dx}) Offset {found_idx}. Confidence: {confidence:.2f}")
                             return recovered_text
                    except:
                        pass
                    
                    return "Message corrupted"

        return "Message not found"
