import cv2
import numpy as np
from stego_dct import DCTSteganography
from stego_dwt_svd import DWTSVDSteganography

class StegoManager:
    def __init__(self):
        self.dct = DCTSteganography()
        self.dwt_svd = DWTSVDSteganography()
        self.algos = {
            "dct": self.dct,
            "dwt_svd": self.dwt_svd
        }

    def analyze_image(self, img: np.ndarray) -> dict:
        """
        Analyzes the image to suggest the best steganography algorithm.
        Returns a dict with 'suggested_algo' and 'reason'.
        """
        h, w = img.shape[:2]
        size = h * w
        
        # Convert to grayscale for analysis
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Calculate entropy (measure of information/texture)
        hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
        hist_norm = hist.ravel() / hist.sum()
        entropy = -np.sum(hist_norm * np.log2(hist_norm + 1e-7))
        
        # Logic for suggestion
        if size < 64 * 64:
            return {
                "suggested_algo": "none",
                "reason": "Image too small for reliable steganography."
            }
        
        # DCT is generally better for JPEG compression resistance
        # DWT-SVD is often better for geometric transformations
        
        # Simple heuristic: High entropy (texture) hides noise better -> DWT-SVD might be good
        # Low entropy (smooth areas) -> DCT might be less visible
        
        if entropy > 7.0:
            return {
                "suggested_algo": "dwt_svd",
                "reason": "High texture complexity detected. DWT-SVD is recommended for better robustness in textured areas."
            }
        else:
            return {
                "suggested_algo": "dct",
                "reason": "Smoother image detected. DCT is recommended for better imperceptibility and JPEG resistance."
            }

    def sign(self, img: np.ndarray, text: str, algo: str = None) -> np.ndarray:
        """
        Signs the image using the specified algorithm or the suggested one.
        """
        if algo is None:
            analysis = self.analyze_image(img)
            algo = analysis["suggested_algo"]
            if algo == "none":
                raise ValueError("Image unsuitable for steganography")
        
        algo = algo.lower()
        if algo not in self.algos:
            raise ValueError(f"Unknown algorithm: {algo}. Available: {list(self.algos.keys())}")
            
        return self.algos[algo].embed(img, text)

    def extract(self, img: np.ndarray) -> dict:
        """
        Attempts to extract a message using all available algorithms.
        Returns the message and the algorithm that found it.
        """
        results = {}
        
        # Try DCT
        try:
            msg = self.dct.extract(img)
            if msg and "not found" not in msg.lower() and "corrupted" not in msg.lower():
                return {"algorithm": "dct", "message": msg}
            results["dct"] = msg
        except Exception as e:
            results["dct"] = str(e)
            
        # Try DWT-SVD
        try:
            msg = self.dwt_svd.extract(img)
            if msg and "not found" not in msg.lower() and "corrupted" not in msg.lower():
                return {"algorithm": "dwt_svd", "message": msg}
            results["dwt_svd"] = msg
            
        return {"algorithm": "unknown", "message": "Message not found in any supported format", "details": results}
