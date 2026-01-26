from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import pandas as pd
import numpy as np
import os

app = Flask(__name__)
CORS(app)  # Autoriser les requêtes cross-origin

# Charger le modèle
model = joblib.load('crop_recommendation_model.joblib')

@app.route('/')
def home():
    return "API de recommandation de cultures - CIA Agro"

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Récupérer les données JSON de la requête
        data = request.json
        
        # Valider que nous avons toutes les features nécessaires
        required_features = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
        for feature in required_features:
            if feature not in data:
                return jsonify({'error': f'Feature manquante: {feature}'}), 400
        
        # Créer un DataFrame pour le modèle
        input_data = pd.DataFrame([[
            data['N'],
            data['P'],
            data['K'],
            data['temperature'],
            data['humidity'],
            data['ph'],
            data['rainfall']
        ]], columns=required_features)
        
        # Prédiction
        probabilities = model.predict_proba(input_data)[0]
        classes = model.classes_
        
        # Préparer les résultats avec un seuil de confiance de 75%
        recommendations = []
        for i, prob in enumerate(probabilities):
            if prob >= 0.75:
                recommendations.append({
                    "crop": str(classes[i]),
                    "confidence": float(prob),
                    "percentage": float(prob * 100)
                })
        
        # Si aucune recommandation n'atteint 75%, retourner les 3 meilleures
        if not recommendations:
            top_indices = np.argsort(probabilities)[-3:][::-1]
            for idx in top_indices:
                recommendations.append({
                    "crop": str(classes[idx]),
                    "confidence": float(probabilities[idx]),
                    "percentage": float(probabilities[idx] * 100)
                })
        
        return jsonify({
            "success": True,
            "recommendations": recommendations,
            "input_data": data
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "model_loaded": True})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)