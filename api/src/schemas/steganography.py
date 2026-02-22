from pydantic import BaseModel, Field
from typing import Optional

class SignResponse(BaseModel):
    message: str = Field(..., description="Status message")
    algorithm: str = Field(..., description="Algorithm used")
    psnr: Optional[float] = Field(None, description="Peak Signal-to-Noise Ratio (dB)")
    ssim: Optional[float] = Field(None, description="Structural Similarity Index")
    mse: Optional[float] = Field(None, description="Mean Squared Error")
    
class ReadResponse(BaseModel):
    message: str = Field(..., description="Extracted hidden message")
    found: bool = Field(..., description="Whether a message was found")
    algorithm: Optional[str] = Field(None, description="Algorithm that detected the message")
    confidence: Optional[float] = Field(None, description="Confidence score if available")

class ErrorResponse(BaseModel):
    detail: str = Field(..., description="Error description")
