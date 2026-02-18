from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse
import cv2
import numpy as np
import io
from ..manager import StegoManager
from ..utils import read_image

router = APIRouter()
manager = StegoManager()

@router.post("/analyze")
async def analyze_image(file: UploadFile = File(...)):
    try:
        img = await read_image(file)
        analysis = manager.analyze_image(img)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sign")
async def sign_image(text: str = Form(...), algo: str = Form(None), file: UploadFile = File(...)):
    try:
        img = await read_image(file)
        
        # If no algo specified, use the suggested one
        if not algo:
            analysis = manager.analyze_image(img)
            algo = analysis["suggested_algo"]
            if algo == "none":
                raise HTTPException(status_code=400, detail="Image unsuitable for steganography")
        
        signed_img = manager.sign(img, text, algo)
        
        _, encoded_img = cv2.imencode('.png', signed_img)
        return StreamingResponse(io.BytesIO(encoded_img.tobytes()), media_type="image/png")
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/extract")
async def extract_message(file: UploadFile = File(...)):
    try:
        img = await read_image(file)
        result = manager.extract(img)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
