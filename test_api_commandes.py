#!/usr/bin/env python3
"""
Script de test pour vérifier l'API des commandes
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from logic.projet1 import bp
from flask import Flask
import json

def test_api_commandes():
    """Test de l'API des commandes"""
    print("🧪 Test de l'API des commandes")
    print("=" * 40)
    
    # Créer une app Flask temporaire pour tester
    app = Flask(__name__)
    app.register_blueprint(bp)
    
    with app.test_client() as client:
        # Tester l'API des commandes
        response = client.get('/projet1/api/commandes')
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.get_json()
            print(f"Nombre de commandes: {len(data)}")
            
            if data:
                print("Première commande:")
                print(json.dumps(data[0], indent=2, ensure_ascii=False))
                
                # Vérifier le format FullCalendar
                first_event = data[0]
                required_fields = ['id', 'title', 'start']
                missing_fields = [field for field in required_fields if field not in first_event]
                
                if missing_fields:
                    print(f"❌ Champs manquants pour FullCalendar: {missing_fields}")
                else:
                    print("✅ Format compatible avec FullCalendar")
            else:
                print("❌ Aucune commande trouvée")
        else:
            print(f"❌ Erreur API: {response.status_code}")
            print(response.get_data(as_text=True))

if __name__ == "__main__":
    test_api_commandes()

