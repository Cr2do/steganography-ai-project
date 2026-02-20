from fastapi import APIRouter
from .steganography import router as steganography_router

router = APIRouter()
router.include_router(steganography_router, prefix="/steganography", tags=["Steganography"])
