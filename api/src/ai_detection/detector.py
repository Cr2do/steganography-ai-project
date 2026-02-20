import cv2
import numpy as np
from typing import Dict, Any

class AIDetector:
    """
    Detects if an image is AI-generated using frequency analysis (FFT).
    AI images often exhibit specific artifacts in the frequency domain.
    """
    
    def detect(self, image: np.ndarray) -> Dict[str, Any]:
        """
        Analyze the image to determine if it's likely AI-generated.
        
        :param image: Input image (BGR numpy array)
        :return: Dictionary with detection results
        """
        if image is None:
            raise ValueError("Image is None")
            
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 1. Frequency Analysis (FFT)
        f = np.fft.fft2(gray)
        fshift = np.fft.fftshift(f)
        magnitude_spectrum = 20 * np.log(np.abs(fshift) + 1e-8)
        
        # Calculate azimuthal average of the power spectrum
        # AI images often have different spectral decay characteristics
        h, w = gray.shape
        center_y, center_x = h // 2, w // 2
        
        y, x = np.ogrid[:h, :w]
        r = np.sqrt((x - center_x)**2 + (y - center_y)**2)
        r = r.astype(int)
        
        # Bin the magnitude spectrum by radius
        tbin = np.bincount(r.ravel(), magnitude_spectrum.ravel())
        nr = np.bincount(r.ravel())
        radial_profile = tbin / (nr + 1e-8)
        
        # Simple heuristic: Check for high-frequency anomalies
        # Real photos tend to have a smooth 1/f^alpha decay
        # AI images might have spikes or unusual drops
        
        # Calculate slope of log-log plot (Beta)
        # We look at the middle frequencies
        start_r = 10
        end_r = min(h, w) // 4
        
        if end_r <= start_r:
            return {"is_ai": False, "confidence": 0.0, "reason": "Image too small", "spectral_slope": 0.0, "method": "Frequency Analysis (FFT)"}
            
        log_r = np.log(np.arange(start_r, end_r))
        log_val = np.log(radial_profile[start_r:end_r] + 1e-8)
        
        # Linear regression
        slope, intercept = np.polyfit(log_r, log_val, 1)
        
        # Heuristic threshold (needs calibration with dataset)
        # Real images typically have slope around -2.0 to -1.0
        # AI images might deviate significantly
        
        is_ai = False
        confidence = 0.0
        
        # This is a simplified placeholder logic. 
        # A real implementation would use a trained classifier (SVM/CNN) on these features.
        if slope > -1.5: # Too flat (too much high freq noise)
            is_ai = True
            confidence = min(1.0, abs(slope + 1.5) * 2)
        elif slope < -3.0: # Too steep (too smooth/blurry)
            is_ai = True
            confidence = min(1.0, abs(slope + 3.0) * 2)
            
        return {
            "is_ai": is_ai,
            "confidence": float(confidence),
            "spectral_slope": float(slope),
            "method": "Frequency Analysis (FFT)"
        }
