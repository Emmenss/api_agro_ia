from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import joblib
import pandas as pd
import numpy as np
from pydantic import BaseModel
import os

app = FastAPI(title="CIA Agro API", version="1.0.0")

# Autoriser toutes les origines pour Flutter
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production, spécifiez votre domaine
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Charger le modèle
MODEL_PATH = os.getenv("MODEL_PATH", "crop_recommendation_model.joblib")
model = joblib.load(MODEL_PATH)

# Modèle de données
class SoilData(BaseModel):
    N: float          # Azote
    P: float          # Phosphore
    K: float          # Potassium
    temperature: float
    humidity: float
    ph: float
    rainfall: float

class PredictionRequest(BaseModel):
    soil_data: SoilData

@app.get("/")
async def root():
    return {
        "message": "API CIA Agro - Recommandation de cultures",
        "version": "1.0.0",
        "endpoints": {
            "/health": "Vérifier l'état de l'API",
            "/predict": "Obtenir des recommandations de cultures"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "model_name": "Crop Recommendation Model",
        "classes": list(model.classes_)
    }

@app.post("/predict")
async def predict(request: PredictionRequest):
    try:
        # Convertir les données en DataFrame
        input_data = pd.DataFrame([[
            request.soil_data.N,
            request.soil_data.P,
            request.soil_data.K,
            request.soil_data.temperature,
            request.soil_data.humidity,
            request.soil_data.ph,
            request.soil_data.rainfall
        ]], columns=['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall'])
        
        # Faire la prédiction
        probabilities = model.predict_proba(input_data)[0]
        
        # Préparer les résultats
        recommendations = []
        for i, prob in enumerate(probabilities):
            if prob >= 0.6:  # Seuil de 60%
                recommendations.append({
                    "crop": str(model.classes_[i]),
                    "confidence": float(prob),
                    "percentage": float(prob * 100)
                })
        
        # Si aucune recommandation n'atteint 60%, prendre le top 3
        if not recommendations:
            top_indices = np.argsort(probabilities)[-3:][::-1]
            for idx in top_indices:
                recommendations.append({
                    "crop": str(model.classes_[idx]),
                    "confidence": float(probabilities[idx]),
                    "percentage": float(probabilities[idx] * 100)
                })
        
        # Trier par confiance
        recommendations.sort(key=lambda x: x["confidence"], reverse=True)
        
        return {
            "success": True,
            "recommendations": recommendations,
            "top_recommendation": recommendations[0] if recommendations else None
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)