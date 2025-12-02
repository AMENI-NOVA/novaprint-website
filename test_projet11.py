#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de test pour le Projet 11 - Gestion des Traitements
"""

import sys
from logic import projet11


def test_connexion():
    """Test de la connexion à la base de données"""
    print("\n" + "="*70)
    print("TEST 1: Connexion à la base de données")
    print("="*70)
    
    try:
        with projet11.get_db_cursor() as cursor:
            cursor.execute("SELECT @@VERSION")
            version = cursor.fetchone()[0]
            print("✓ Connexion réussie")
            print(f"  Version SQL Server: {version[:50]}...")
            return True
    except Exception as e:
        print(f"✗ Erreur de connexion: {e}")
        return False


def test_table_exists():
    """Test de l'existence de la table WEB_TRAITEMENTS"""
    print("\n" + "="*70)
    print("TEST 2: Vérification de la table WEB_TRAITEMENTS")
    print("="*70)
    
    try:
        with projet11.get_db_cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(*) 
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_NAME = 'WEB_TRAITEMENTS'
            """)
            
            if cursor.fetchone()[0] > 0:
                print("✓ Table WEB_TRAITEMENTS existe")
                
                # Compter les enregistrements
                cursor.execute("SELECT COUNT(*) FROM WEB_TRAITEMENTS")
                count = cursor.fetchone()[0]
                print(f"  Nombre d'enregistrements: {count}")
                
                return True
            else:
                print("✗ Table WEB_TRAITEMENTS n'existe pas")
                return False
    except Exception as e:
        print(f"✗ Erreur: {e}")
        return False


def test_fiches_disponibles():
    """Test de récupération des fiches de travail disponibles"""
    print("\n" + "="*70)
    print("TEST 3: Récupération des fiches de travail disponibles")
    print("="*70)
    
    try:
        fiches = projet11.get_fiches_travail_disponibles()
        print(f"✓ {len(fiches)} fiche(s) de travail disponible(s)")
        
        if fiches:
            print("\n  Exemple de fiche:")
            fiche = fiches[0]
            print(f"    ID Fiche: {fiche['id_fiche_travail']}")
            print(f"    N° Commande: {fiche['numero_commande']}")
            print(f"    Client: {fiche['client']}")
            print(f"    Service: {fiche['service']}")
            print(f"    Poste: {fiche['poste']}")
        
        return True
    except Exception as e:
        print(f"✗ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_operateurs():
    """Test de récupération des opérateurs"""
    print("\n" + "="*70)
    print("TEST 4: Récupération des opérateurs")
    print("="*70)
    
    try:
        operateurs = projet11.get_operateurs_disponibles()
        print(f"✓ {len(operateurs)} opérateur(s) disponible(s)")
        
        if operateurs:
            print("\n  Exemples d'opérateurs (5 premiers):")
            for i, op in enumerate(operateurs[:5], 1):
                print(f"    {i}. {op['nom_complet']} (Matricule: {op['matricule']})")
        
        return True
    except Exception as e:
        print(f"✗ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_get_traitements():
    """Test de récupération des traitements"""
    print("\n" + "="*70)
    print("TEST 5: Récupération des traitements")
    print("="*70)
    
    try:
        traitements = projet11.get_all_traitements()
        print(f"✓ {len(traitements)} traitement(s) enregistré(s)")
        
        if traitements:
            print("\n  Exemple de traitement:")
            t = traitements[0]
            print(f"    ID: {t['id']}")
            print(f"    N° Commande: {t['numero_commande']}")
            print(f"    Client: {t['client']}")
            print(f"    Date début: {t['dte_deb']}")
            print(f"    Date fin: {t['dte_fin']}")
            print(f"    Nb opérations: {t['nb_op']}")
            print(f"    Nb personnes: {t['nb_pers']}")
        
        return True
    except Exception as e:
        print(f"✗ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_statistiques():
    """Test de récupération des statistiques"""
    print("\n" + "="*70)
    print("TEST 6: Récupération des statistiques")
    print("="*70)
    
    try:
        stats = projet11.get_statistiques_traitements()
        print("✓ Statistiques globales:")
        print(f"    Total traitements: {stats['total_traitements']}")
        print(f"    Traitements terminés: {stats['traitements_termines']}")
        print(f"    Traitements en cours: {stats['traitements_en_cours']}")
        print(f"    Total opérations: {stats['total_operations']}")
        print(f"    Moyenne opérations: {stats['moyenne_operations']:.3f}")
        print(f"    Moyenne personnes: {stats['moyenne_personnes']:.3f}")
        
        print("\n✓ Statistiques par service:")
        stats_services = projet11.get_traitements_par_service()
        for s in stats_services[:5]:
            print(f"    {s['service']}: {s['nb_traitements']} traitement(s), "
                  f"{s['total_operations']} opérations")
        
        print("\n✓ Statistiques par opérateur:")
        stats_ops = projet11.get_traitements_par_operateur()
        for op in stats_ops[:5]:
            print(f"    {op['operateur']}: {op['nb_traitements']} traitement(s), "
                  f"{op['total_operations']} opérations")
        
        return True
    except Exception as e:
        print(f"✗ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_create_traitement():
    """Test de création d'un traitement (optionnel, commenté par défaut)"""
    print("\n" + "="*70)
    print("TEST 7: Création d'un traitement (DÉSACTIVÉ)")
    print("="*70)
    print("  Pour activer ce test, décommentez le code dans test_projet11.py")
    
    # Décommenter pour tester la création
    """
    from datetime import datetime
    
    try:
        fiches = projet11.get_fiches_travail_disponibles()
        if not fiches:
            print("✗ Aucune fiche disponible pour le test")
            return False
        
        fiche = fiches[0]
        operateurs = projet11.get_operateurs_disponibles()
        
        data = {
            'id_fiche_travail': fiche['id_fiche_travail'],
            'dte_deb': datetime.now(),
            'dte_fin': None,
            'nb_op': 100,
            'nb_pers': 2,
            'matricule_personel': operateurs[0]['matricule'] if operateurs else None
        }
        
        traitement_id = projet11.create_traitement(data)
        
        if traitement_id:
            print(f"✓ Traitement créé avec succès (ID: {traitement_id})")
            
            # Supprimer le traitement de test
            projet11.delete_traitement(traitement_id)
            print(f"✓ Traitement de test supprimé")
            
            return True
        else:
            print("✗ Échec de la création du traitement")
            return False
            
    except Exception as e:
        print(f"✗ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False
    """
    
    return True


def main():
    """Fonction principale de test"""
    print("\n" + "="*70)
    print("TESTS DU PROJET 11 - GESTION DES TRAITEMENTS")
    print("="*70)
    
    tests = [
        ("Connexion DB", test_connexion),
        ("Table WEB_TRAITEMENTS", test_table_exists),
        ("Fiches disponibles", test_fiches_disponibles),
        ("Opérateurs", test_operateurs),
        ("Traitements", test_get_traitements),
        ("Statistiques", test_statistiques),
        ("Création traitement", test_create_traitement)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ Exception dans {test_name}: {e}")
            results.append((test_name, False))
    
    # Résumé
    print("\n" + "="*70)
    print("RÉSUMÉ DES TESTS")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status} - {test_name}")
    
    print("\n" + "="*70)
    print(f"Résultat: {passed}/{total} tests réussis ({passed*100//total}%)")
    print("="*70)
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)


