from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Response
from typing import Optional
import json
from ..utils.algorithm.service import SteganographyService
from ..schemas.steganography import SignResponse, ReadResponse, ErrorResponse
from ..schemas.evaluation import EvaluationResponse

router = APIRouter()
service = SteganographyService()

@router.post("/sign", 
    summary="Sign an image with a hidden message",
    description="Embeds a text message into an image using DCT or DWT-SVD steganography. Returns the image and quality metrics in headers.",
    responses={
        200: {
            "content": {"image/png": {}},
            "description": "Returns the signed image as a PNG file. Metrics (PSNR, SSIM) are in the 'X-Metrics' header."
        },
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
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
        signed_image_bytes, metrics = service.sign_image(image_bytes, text, algo)
        
        # We return the image as the body, but we attach metrics as headers
        # because we can't return both JSON and File easily in one response without multipart.
        headers = {
            "X-Metrics": json.dumps(metrics),
            "X-PSNR": str(metrics["psnr"]),
            "X-SSIM": str(metrics["ssim"])
        }
        
        return Response(content=signed_image_bytes, media_type="image/png", headers=headers)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/read", 
    summary="Read a hidden message from an image",
    description="Extracts a hidden text message from a signed image. Auto-detects algorithm if not specified.",
    response_model=ReadResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
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
        message, detected_algo = service.read_image(image_bytes, algo)
        
        if message:
            return ReadResponse(
                message=message,
                found=True,
                algorithm=detected_algo,
                confidence=1.0 # Placeholder for now, will be implemented later
            )
        else:
            return ReadResponse(
                message="No hidden message found",
                found=False,
                algorithm=None,
                confidence=0.0
            )
            
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/evaluate",
    summary="Evaluate robustness of steganography",
    description="Runs a full evaluation pipeline: Embeds message, applies attacks (JPEG, Noise, Crop), and attempts recovery.",
    response_model=EvaluationResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def evaluate_robustness(
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
        result = service.evaluate_robustness(image_bytes, text, algo)
        return EvaluationResponse(**result)
            
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
