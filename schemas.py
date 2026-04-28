from pydantic import BaseModel, Field
from typing import List

class MilestoneExtraction(BaseModel):
    """Model for extracting developmental milestones and safety context from an image or video."""
    
    age_estimate: str = Field(
        ..., 
        description="The estimated age range of the child (e.g., '6-9 months', '1-2 years')."
    )
    detected_activity: str = Field(
        ..., 
        description="The developmental activity the child is engaged in (e.g., 'crawling', 'standing with support')."
    )
    safety_hazards: List[str] = Field(
        ..., 
        description="A list of potential safety hazards detected in the environment."
    )

class ProductRecommendation(BaseModel):
    """Model for a recommended product based on the child's developmental stage and needs."""
    
    product_id: str = Field(
        ..., 
        description="The unique identifier of the recommended product."
    )
    reasoning_en: str = Field(
        ..., 
        description="The reasoning behind the recommendation, explained in English."
    )
    reasoning_ar: str = Field(
        ..., 
        description="The reasoning behind the recommendation, explained in Arabic."
    )
    safety_audit_status: str = Field(
        ..., 
        description="The safety audit status of the product (e.g., 'passed', 'pending review', 'flagged')."
    )
