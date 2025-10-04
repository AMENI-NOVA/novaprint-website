#!/usr/bin/env python3
"""
Script de test pour le module de suivi des délais
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db import (
    get_commandes_avec_suivi, 
    get_statistiques_performance, 
    get_performance_par_client, 
    get_alertes_retard
)

def test_fonctions_suivi():
    """Test des nouvelles fonctions de suivi des délais"""
    print("🧪 Test du module de suivi des délais")
    print("=" * 50)
    
    try:
        # Test 1: Commandes avec suivi
        print("\n1. Test des commandes avec suivi...")
        commandes = get_commandes_avec_suivi()
        print(f"   ✅ {len(commandes)} commandes récupérées")
        
        if commandes:
            print(f"   📋 Exemple de commande: {commandes[0]}")
        
        # Test 2: Statistiques de performance
        print("\n2. Test des statistiques de performance...")
        stats = get_statistiques_performance()
        print(f"   ✅ Statistiques récupérées: {stats}")
        
        # Test 3: Performance par client
        print("\n3. Test de la performance par client...")
        clients = get_performance_par_client()
        print(f"   ✅ {len(clients)} clients analysés")
        
        if clients:
            print(f"   📊 Exemple de client: {clients[0]}")
        
        # Test 4: Alertes de retard
        print("\n4. Test des alertes de retard...")
        alertes = get_alertes_retard()
        print(f"   ✅ {len(alertes)} alertes de retard")
        
        if alertes:
            print(f"   ⚠️  Exemple d'alerte: {alertes[0]}")
        
        print("\n🎉 Tous les tests sont passés avec succès!")
        return True
        
    except Exception as e:
        print(f"\n❌ Erreur lors des tests: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def afficher_resume():
    """Affiche un résumé des fonctionnalités implémentées"""
    print("\n📋 RÉSUMÉ DES FONCTIONNALITÉS IMPLÉMENTÉES")
    print("=" * 60)
    
    print("\n🔧 Backend (db.py):")
    print("   • get_commandes_avec_suivi() - Récupère les commandes avec statut de délai")
    print("   • get_statistiques_performance() - Calcule les indicateurs globaux")
    print("   • get_performance_par_client() - Analyse la performance par client")
    print("   • get_alertes_retard() - Identifie les commandes en retard")
    print("   • marquer_livraison_reelle() - Marque une commande comme livrée")
    
    print("\n🌐 API (logic/projet1.py):")
    print("   • /api/commandes-avec-suivi - API pour les commandes avec suivi")
    print("   • /api/statistiques-performance - API pour les statistiques")
    print("   • /api/performance-par-client - API pour la performance par client")
    print("   • /api/alertes-retard - API pour les alertes")
    print("   • /api/marquer-livraison - API pour marquer une livraison")
    
    print("\n🎨 Frontend (templates/projet1.html):")
    print("   • Onglet Planning - Calendrier existant")
    print("   • Onglet Suivi des Délais - Tableau des commandes avec statuts")
    print("   • Onglet Performance - Indicateurs et tableaux de bord")
    print("   • Alertes visuelles pour les retards")
    print("   • Boutons d'action pour marquer les livraisons")
    
    print("\n📊 Indicateurs de Performance:")
    print("   • Taux de ponctualité (%)")
    print("   • Nombre de commandes livrées")
    print("   • Délai moyen de livraison")
    print("   • Nombre de commandes en retard")
    print("   • Performance par client")
    
    print("\n🚀 Pour tester l'interface web:")
    print("   1. Lancez l'application: python app.py")
    print("   2. Accédez à: http://localhost:5000/projet1")
    print("   3. Naviguez entre les onglets Planning, Suivi et Performance")

if __name__ == "__main__":
    print("🚀 Démarrage des tests du module de suivi des délais")
    
    # Exécuter les tests
    success = test_fonctions_suivi()
    
    # Afficher le résumé
    afficher_resume()
    
    if success:
        print("\n✅ Module de suivi des délais prêt à l'utilisation!")
        sys.exit(0)
    else:
        print("\n❌ Des erreurs ont été détectées. Vérifiez la configuration.")
        sys.exit(1)

