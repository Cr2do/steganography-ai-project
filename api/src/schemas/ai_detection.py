from pydantic import BaseModel, Field
from typing import Optional

class AIDetectionResponse(BaseModel):
    is_ai: bool = Field(..., description="Whether the image is detected as AI-generated")
    confidence: float = Field(..., description="Confidence score (0.0 to 1.0)")
    spectral_slope: Optional[float] = Field(None, description="Spectral slope from FFT analysis")
    method: str = Field(..., description="Method used for detection")
