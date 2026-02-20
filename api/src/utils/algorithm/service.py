import cv2
import numpy as np
from .signal_processing.stego_dct import DCTSteganography
from .signal_processing.stego_dwt_svd import DWTSVDSteganography
from .computer_vision.fiducial import FiducialMarker

class SteganographyService:
    def __init__(self):
        self.dct = DCTSteganography()
        self.dwt = DWTSVDSteganography()
        self.fiducial = FiducialMarker()

    def sign_image(self, image_bytes, text, algo_type="dct"):
        """
        Signs an image with the given text using the specified algorithm.
        
        :param image_bytes: Input image bytes
        :param text: Text to embed
        :param algo_type: 'dct' or 'dwt' (default: 'dct')
        :return: Signed image bytes
        """
        # Convert bytes to numpy array
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            raise ValueError("Could not decode image")

        # 1. Add Fiducial Markers (for geometric robustness)
        img_marked = self.fiducial.add_markers(img)
        
        # 2. Embed Text
        if algo_type and algo_type.lower() == "dwt":
            stego_img = self.dwt.embed(img_marked, text)
        else:
            stego_img = self.dct.embed(img_marked, text)
            
        # Convert back to bytes
        success, encoded_img = cv2.imencode('.png', stego_img)
        if not success:
            raise ValueError("Could not encode output image")
            
        return encoded_img.tobytes()

    def read_image(self, image_bytes, algo_type=None):
        """
        Reads a signed image and extracts the text.
        If algo_type is not provided, it tries both.
        
        :param image_bytes: Input image bytes
        :param algo_type: 'dct', 'dwt', or None (auto-detect)
        :return: Extracted text or None if not found
        """
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            raise ValueError("Could not decode image")
            
        # 1. Rectify Image (Geometric Correction)
        img_rectified = self.fiducial.detect_and_rectify(img)
        
        # If rectification fails, try with original image (maybe no geometric distortion)
        target_images = [img_rectified, img] if img_rectified is not None else [img]
        
        for current_img in target_images:
            if current_img is None: continue
            
            # Try specified algorithm
            if algo_type:
                if algo_type.lower() == "dwt":
                    result = self.dwt.extract(current_img)
                else:
                    result = self.dct.extract(current_img)
                
                if result: return result
            
            # Auto-detect: Try both
            else:
                # Try DCT first
                result = self.dct.extract(current_img)
                if result: return result
                
                # Try DWT
                result = self.dwt.extract(current_img)
                if result: return result
                
        return None
