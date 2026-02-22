from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class AttackResult(BaseModel):
    attack_name: str = Field(..., description="Name of the attack (e.g., JPEG 80)")
    psnr: float = Field(..., description="PSNR after attack")
    ssim: float = Field(..., description="SSIM after attack")
    message_recovered: bool = Field(..., description="Was the message recovered?")
    recovered_text: Optional[str] = Field(None, description="The text that was recovered")
    
class EvaluationResponse(BaseModel):
    algorithm: str = Field(..., description="Algorithm tested (dct/dwt)")
    original_message: str = Field(..., description="Message embedded")
    results: List[AttackResult] = Field(..., description="List of attack results")
    robustness_score: float = Field(..., description="Overall robustness score (0.0 - 1.0)")
