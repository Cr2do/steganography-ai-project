from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Response
from typing import Optional
from ..utils.algorithm.service import SteganographyService

router = APIRouter()
service = SteganographyService()

@router.post("/sign", 
    summary="Sign an image with a hidden message",
    description="Embeds a text message into an image using DCT or DWT-SVD steganography.",
    responses={
        200: {
            "content": {"image/png": {}},
            "description": "Returns the signed image as a PNG file."
        }
    }
)
async def sign_image(
    file: UploadFile = File(..., description="The input image file (JPG/PNG)"),
    text: str = Form(..., description="The secret message to embed (max 20 chars)"),
    algo: Optional[str] = Form("dct", description="Algorithm to use: 'dct' or 'dwt'")
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    if len(text) > 20:
        raise HTTPException(status_code=400, detail="Text too long (max 20 chars)")

    try:
        image_bytes = await file.read()
        signed_image_bytes = service.sign_image(image_bytes, text, algo)
        
        return Response(content=signed_image_bytes, media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/read", 
    summary="Read a hidden message from an image",
    description="Extracts a hidden text message from a signed image. Auto-detects algorithm if not specified.",
    responses={
        200: {
            "description": "Returns the extracted message.",
            "content": {
                "application/json": {
                    "example": {"message": "Secret123", "found": True}
                }
            }
        }
    }
)
async def read_image(
    file: UploadFile = File(..., description="The signed image file"),
    algo: Optional[str] = Form(None, description="Optional: 'dct' or 'dwt'. If omitted, tries both.")
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    try:
        image_bytes = await file.read()
        message = service.read_image(image_bytes, algo)
        
        if message:
            return {"message": message, "found": True}
        else:
            return {"message": "No hidden message found", "found": False}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
