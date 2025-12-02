#!/usr/bin/env python3
"""
Test du Projet 10 - Contrôle Qualité
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db import (
    get_numeros_commandes_disponibles,
    get_controles_qualite,
    get_statistiques_controle_qualite
)

def test_projet10():
    """Test du projet 10"""
    print("🧪 TEST DU PROJET 10 - CONTRÔLE QUALITÉ")
    print("=" * 50)
    
    try:
        # Test 1: Numéros de commandes disponibles
        print("\n1. 📋 NUMÉROS DE COMMANDES DISPONIBLES")
        numeros = get_numeros_commandes_disponibles()
        print(f"   ✅ {len(numeros)} numéros de commandes disponibles")
        
        if numeros:
            print(f"   📊 Premier numéro: {numeros[0]}")
            print(f"   📊 Dernier numéro: {numeros[-1]}")
        
        # Test 2: Contrôles qualité existants
        print("\n2. 🔍 CONTRÔLES QUALITÉ EXISTANTS")
        controles = get_controles_qualite()
        print(f"   ✅ {len(controles)} contrôles qualité trouvés")
        
        if controles:
            print(f"   📊 Premier contrôle: ID {controles[0]['id']} - {controles[0]['Numero_COMMANDES']}")
        
        # Test 3: Statistiques
        print("\n3. 📈 STATISTIQUES")
        stats = get_statistiques_controle_qualite()
        print(f"   ✅ Total contrôles: {stats['total_controles']}")
        print(f"   ✅ Contrôles validés: {stats['controles_valides']}")
        print(f"   ✅ Rebus moyen: {stats['rebus_moyen']}")
        print(f"   ✅ Total rebus: {stats['total_rebus']}")
        
        print("\n🎉 TOUS LES TESTS SONT PASSÉS AVEC SUCCÈS!")
        print("\n📋 FONCTIONNALITÉS DU PROJET 10:")
        print("   • Liste des contrôles qualité")
        print("   • Création de nouveaux contrôles")
        print("   • Sélection des numéros de commandes depuis la base")
        print("   • Gestion des tolérances")
        print("   • Statistiques de contrôle qualité")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERREUR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_projet10()
    
    if success:
        print("\n🚀 PROJET 10 PRÊT À L'UTILISATION!")
        print("   Accédez à: http://localhost:5000/projet10")
        print("   Fonctionnalités disponibles:")
        print("   • Onglet Contrôles: Liste des contrôles existants")
        print("   • Onglet Nouveau Contrôle: Création avec sélection de numéro")
        print("   • Onglet Statistiques: Indicateurs de performance")
    else:
        print("\n❌ Des erreurs ont été détectées")
        sys.exit(1)

