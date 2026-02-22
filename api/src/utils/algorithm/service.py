import cv2
import numpy as np
from typing import Optional, Tuple, Dict, List
from .signal_processing.stego_dct import DCTSteganography
from .signal_processing.stego_dwt_svd import DWTSVDSteganography
from .computer_vision.fiducial import FiducialMarker
from ...metrics.image_quality import calculate_psnr, calculate_ssim, calculate_mse
from .signal_processing.attacks import ImageAttacks

class SteganographyService:
    def __init__(self):
        self.dct = DCTSteganography()
        self.dwt = DWTSVDSteganography()
        self.fiducial = FiducialMarker()

    def _decode_image(self, image_bytes: bytes) -> np.ndarray:
        """Helper to decode image bytes to numpy array."""
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError("Could not decode image. Ensure it is a valid image file.")
        return img

    def _encode_image(self, img: np.ndarray) -> bytes:
        """Helper to encode numpy array to PNG bytes."""
        success, encoded_img = cv2.imencode('.png', img)
        if not success:
            raise ValueError("Could not encode output image.")
        return encoded_img.tobytes()

    def sign_image(self, image_bytes: bytes, text: str, algo_type: str = "dct") -> Tuple[bytes, Dict[str, float]]:
        """
        Signs an image with the given text using the specified algorithm.
        
        :param image_bytes: Input image bytes
        :param text: Text to embed
        :param algo_type: 'dct' or 'dwt' (default: 'dct')
        :return: Tuple (Signed image bytes, Metrics dictionary)
        """
        img = self._decode_image(image_bytes)
        original_img = img.copy()

        # 1. Add Fiducial Markers (for geometric robustness)
        img_marked = self.fiducial.add_markers(img)
        
        # 2. Embed Text
        if algo_type and algo_type.lower() == "dwt":
            stego_img = self.dwt.embed(img_marked, text)
        else:
            stego_img = self.dct.embed(img_marked, text)
            
        # 3. Calculate Metrics
        # Resize original if needed (DWT resizes image)
        if stego_img.shape != original_img.shape:
             original_img = cv2.resize(original_img, (stego_img.shape[1], stego_img.shape[0]))

        metrics = {
            "psnr": calculate_psnr(original_img, stego_img),
            "ssim": calculate_ssim(original_img, stego_img),
            "mse": calculate_mse(original_img, stego_img)
        }

        return self._encode_image(stego_img), metrics

    def read_image(self, image_bytes: bytes, algo_type: Optional[str] = None) -> Tuple[Optional[str], Optional[str]]:
        """
        Reads a signed image and extracts the text.
        If algo_type is not provided, it tries both.
        
        :param image_bytes: Input image bytes
        :param algo_type: 'dct', 'dwt', or None (auto-detect)
        :return: Tuple (Extracted text, Algorithm used) or (None, None)
        """
        img = self._decode_image(image_bytes)
            
        # 1. Rectify Image (Geometric Correction)
        img_rectified = self.fiducial.detect_and_rectify(img)
        
        # If rectification fails, try with original image (maybe no geometric distortion)
        target_images = [img_rectified, img] if img_rectified is not None else [img]
        
        for current_img in target_images:
            if current_img is None: continue
            
            # Try specified algorithm
            if algo_type:
                algo = algo_type.lower()
                if algo == "dwt":
                    result = self.dwt.extract(current_img)
                else:
                    result = self.dct.extract(current_img)
                
                if result: return result, algo
            
            # Auto-detect: Try both
            else:
                # Try DCT first
                result = self.dct.extract(current_img)
                if result: return result, "dct"
                
                # Try DWT
                result = self.dwt.extract(current_img)
                if result: return result, "dwt"
                
        return None, None

    def evaluate_robustness(self, image_bytes: bytes, text: str, algo_type: str = "dct") -> Dict:
        """
        Runs a full robustness evaluation pipeline.
        1. Embeds message.
        2. Applies attacks (JPEG, Noise, Crop, Resize).
        3. Attempts extraction.
        4. Calculates metrics.
        """
        img = self._decode_image(image_bytes)
        
        # 1. Embed
        img_marked = self.fiducial.add_markers(img)
        if algo_type.lower() == "dwt":
            stego_img = self.dwt.embed(img_marked, text)
        else:
            stego_img = self.dct.embed(img_marked, text)
            
        # 2. Define Attacks
        attacks = [
            ("No Attack", lambda x: x),
            ("JPEG 90", lambda x: ImageAttacks.jpeg_compression(x, 90)),
            ("JPEG 70", lambda x: ImageAttacks.jpeg_compression(x, 70)),
            ("Gaussian Noise", lambda x: ImageAttacks.gaussian_noise(x, var=0.005)),
            ("Resize 50%", lambda x: ImageAttacks.resize(x, 0.5)),
            ("Crop 10%", lambda x: ImageAttacks.crop(x, 0.1))
        ]
        
        results = []
        success_count = 0
        
        for name, func in attacks:
            # Apply attack
            attacked_img = func(stego_img)
            
            # Calculate quality metrics (vs original stego)
            # Resize if needed for metrics comparison
            metric_ref = stego_img
            if attacked_img.shape != stego_img.shape:
                metric_ref = cv2.resize(stego_img, (attacked_img.shape[1], attacked_img.shape[0]))
                
            psnr = calculate_psnr(metric_ref, attacked_img)
            ssim = calculate_ssim(metric_ref, attacked_img)
            
            # Attempt extraction
            # We need to encode back to bytes to reuse read_image logic (which handles rectification)
            success, encoded_attacked = cv2.imencode('.png', attacked_img)
            if not success: continue
            
            # We must pass the specific algo_type to test its robustness specifically
            recovered_text, _ = self.read_image(encoded_attacked.tobytes(), algo_type)
            
            is_success = (recovered_text == text)
            if is_success: success_count += 1
            
            results.append({
                "attack_name": name,
                "psnr": psnr,
                "ssim": ssim,
                "message_recovered": is_success,
                "recovered_text": recovered_text
            })
            
        robustness_score = success_count / len(attacks) if attacks else 0.0
        
        return {
            "algorithm": algo_type,
            "original_message": text,
            "results": results,
            "robustness_score": robustness_score
        }
