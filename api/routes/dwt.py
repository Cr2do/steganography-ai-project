from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse
import cv2
import numpy as np
import io
from ..stego_dwt_svd import DWTSVDSteganography

router = APIRouter()
dwt_stego = DWTSVDSteganography()

@router.post("/sign")
async def sign_dwt(text: str = Form(...), file: UploadFile = File(...)):
    try:
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            raise HTTPException(status_code=400, detail="Invalid image file")
            
        signed_img = dwt_stego.embed(img, text)
        
        _, encoded_img = cv2.imencode('.png', signed_img)
        return StreamingResponse(io.BytesIO(encoded_img.tobytes()), media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/extract")
async def extract_dwt(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            raise HTTPException(status_code=400, detail="Invalid image file")
            
        message = dwt_stego.extract(img)
        return {"message": message}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
