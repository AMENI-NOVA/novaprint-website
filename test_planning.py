#!/usr/bin/env python3
"""
Script de test pour vérifier le planning
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db import get_commandes
import json

def test_planning():
    """Test du planning"""
    print("🧪 Test du planning")
    print("=" * 30)
    
    try:
        # Récupérer les commandes
        commandes = get_commandes()
        print(f"Nombre de commandes récupérées: {len(commandes)}")
        
        if commandes:
            print("\nPremières 3 commandes:")
            for i, cmd in enumerate(commandes[:3]):
                print(f"{i+1}. {cmd['id']} - {cmd['client']} - {cmd['start']}")
            
            # Vérifier le format FullCalendar
            print("\nFormat FullCalendar:")
            print(json.dumps(commandes[0], indent=2, ensure_ascii=False))
            
            # Vérifier les dates
            print("\nVérification des dates:")
            for cmd in commandes[:5]:
                print(f"ID: {cmd['id']}, Date: {cmd['start']}, Client: {cmd['client']}")
        else:
            print("❌ Aucune commande trouvée")
            
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_planning()

