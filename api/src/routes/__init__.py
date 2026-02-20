from fastapi import APIRouter
from .steganography import router as steganography_router
from .ai_detection import router as ai_detection_router

router = APIRouter()
router.include_router(steganography_router, prefix="/steganography", tags=["Steganography"])
router.include_router(ai_detection_router, prefix="/ai-detection", tags=["AI Detection"])
