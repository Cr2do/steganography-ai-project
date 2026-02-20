from fastapi import APIRouter, UploadFile, File, HTTPException
import cv2
import numpy as np
from ..ai_detection.detector import AIDetector
from ..schemas.ai_detection import AIDetectionResponse

router = APIRouter()
detector = AIDetector()

@router.post("/detect", 
    summary="Detect if an image is AI-generated",
    description="Analyzes the image using frequency domain analysis (FFT) to detect artifacts common in AI-generated images.",
    response_model=AIDetectionResponse
)
async def detect_ai(
    file: UploadFile = File(..., description="The input image file (JPG/PNG)")
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    try:
        image_bytes = await file.read()
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            raise HTTPException(status_code=400, detail="Could not decode image")
            
        result = detector.detect(img)
        
        return AIDetectionResponse(
            is_ai=result["is_ai"],
            confidence=result["confidence"],
            spectral_slope=result["spectral_slope"],
            method=result["method"]
        )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
