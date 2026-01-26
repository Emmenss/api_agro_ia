from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class SoilData(BaseModel):
    """Données du sol pour la prédiction"""
    N: float = Field(..., ge=0, le=140, description="Azote (N) en ppm")
    P: float = Field(..., ge=0, le=145, description="Phosphore (P) en ppm")
    K: float = Field(..., ge=0, le=205, description="Potassium (K) en ppm")
    temperature: float = Field(..., ge=0, le=50, description="Température en °C")
    humidity: float = Field(..., ge=0, le=100, description="Humidité relative en %")
    ph: float = Field(..., ge=0, le=14, description="pH du sol")
    rainfall: float = Field(..., ge=0, le=300, description="Précipitations en mm")
    
    # Données optionnelles pour l'agriculture précise
    soil_type: Optional[str] = None
    crop_season: Optional[str] = None
    location: Optional[str] = None

class PredictionRequest(BaseModel):
    """Requête de prédiction"""
    soil_data: SoilData

class CropRecommendation(BaseModel):
    """Recommandation de culture"""
    crop: str
    confidence: float = Field(..., ge=0, le=1)
    probability: float = Field(..., ge=0, le=100)
    
    # Informations supplémentaires sur la culture
    description: Optional[str] = None
    water_requirement: Optional[str] = None
    season: Optional[str] = None
    suitability_score: Optional[int] = None

class PredictionResponse(BaseModel):
    """Réponse de prédiction"""
    success: bool
    timestamp: datetime
    request_id: str
    recommendations: List[CropRecommendation]
    top_recommendation: CropRecommendation
    message: Optional[str] = None
    warning: Optional[str] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class BatchPredictionRequest(BaseModel):
    """Requête de prédiction par lot"""
    soil_data_list: List[SoilData]

class BatchPredictionResponse(BaseModel):
    """Réponse de prédiction par lot"""
    success: bool
    timestamp: datetime
    predictions: List[PredictionResponse]
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class HealthResponse(BaseModel):
    """Réponse de santé de l'API"""
    status: str
    timestamp: datetime
    model_loaded: bool
    model_name: str
    version: str
    uptime: float
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }