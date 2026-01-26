from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import pandas as pd
import numpy as np
import os

app = Flask(__name__)
CORS(app)  # Autorise toutes les origines (pour le développement)

# Charger le modèle
MODEL_PATH = "agro_ia.joblib"
model = joblib.load(MODEL_PATH)
print("✅ Modèle chargé avec succès!")
print(f"📊 Classes disponibles: {model.classes_}")

@app.route('/')
def home():
    return jsonify({
        "message": "API Agriculture IA - Flask",
        "status": "en ligne",
        "endpoints": {
            "GET /health": "Vérifier l'état de l'API",
            "POST /predict": "Obtenir des recommandations"
        }
    })

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy",
        "model_loaded": True,
        "model_name": "Crop Recommendation Model",
        "classes": [str(c) for c in model.classes_]
    })

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Récupérer les données JSON
        data = request.json
        
        # Valider les données requises
        required_fields = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    "success": False,
                    "error": f"Champ manquant: {field}"
                }), 400
        
        # Préparer les données pour le modèle
        input_df = pd.DataFrame([[
            data['N'],
            data['P'],
            data['K'],
            data['temperature'],
            data['humidity'],
            data['ph'],
            data['rainfall']
        ]], columns=['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall'])
        
        # Faire la prédiction
        probabilities = model.predict_proba(input_df)[0]
        
        # Préparer les recommandations
        recommendations = []
        for i, prob in enumerate(probabilities):
            if prob >= 0.6:  # Seuil à 60%
                recommendations.append({
                    "crop": str(model.classes_[i]),
                    "confidence": float(prob),
                    "percentage": float(prob * 100)
                })
        
        # Si moins de recommandations, prendre le top 3
        if len(recommendations) < 3:
            all_results = []
            for i, prob in enumerate(probabilities):
                all_results.append({
                    "crop": str(model.classes_[i]),
                    "confidence": float(prob),
                    "percentage": float(prob * 100)
                })
            all_results.sort(key=lambda x: x["confidence"], reverse=True)
            recommendations = all_results[:3]
        else:
            # Trier par confiance
            recommendations.sort(key=lambda x: x["confidence"], reverse=True)
        
        return jsonify({
            "success": True,
            "recommendations": recommendations,
            "top_recommendation": recommendations[0] if recommendations else None
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)