#!/usr/bin/env python3
"""
Script de migration pour ajouter les colonnes de suivi des délais
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db import get_db_cursor

def execute_migration():
    """Exécute la migration pour ajouter les colonnes nécessaires"""
    print("🔄 Démarrage de la migration pour le suivi des délais")
    print("=" * 60)
    
    try:
        with get_db_cursor() as cursor:
            # Vérifier la structure actuelle
            print("\n1. Vérification de la structure actuelle...")
            cursor.execute("""
                SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'COMMANDES'
                ORDER BY ORDINAL_POSITION
            """)
            
            colonnes = cursor.fetchall()
            print(f"   📋 {len(colonnes)} colonnes trouvées dans la table COMMANDES")
            
            # Vérifier si DteLivReelle existe
            dte_liv_reelle_exists = any(col[0] == 'DteLivReelle' for col in colonnes)
            print(f"   {'✅' if dte_liv_reelle_exists else '❌'} Colonne DteLivReelle: {'Existe' if dte_liv_reelle_exists else 'Manquante'}")
            
            # Ajouter DteLivReelle si elle n'existe pas
            if not dte_liv_reelle_exists:
                print("\n2. Ajout de la colonne DteLivReelle...")
                cursor.execute("ALTER TABLE COMMANDES ADD DteLivReelle DATE NULL")
                print("   ✅ Colonne DteLivReelle ajoutée")
            else:
                print("\n2. Colonne DteLivReelle existe déjà")
            
            # Vérifier la table HISTORIQUE_LIVRAISON
            print("\n3. Vérification de la table HISTORIQUE_LIVRAISON...")
            cursor.execute("""
                SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'HISTORIQUE_LIVRAISON'
                ORDER BY ORDINAL_POSITION
            """)
            
            hist_colonnes = cursor.fetchall()
            print(f"   📋 {len(hist_colonnes)} colonnes trouvées dans HISTORIQUE_LIVRAISON")
            
            # Vérifier si TypeModification existe
            type_mod_exists = any(col[0] == 'TypeModification' for col in hist_colonnes)
            print(f"   {'✅' if type_mod_exists else '❌'} Colonne TypeModification: {'Existe' if type_mod_exists else 'Manquante'}")
            
            # Ajouter TypeModification si elle n'existe pas
            if not type_mod_exists:
                print("\n4. Ajout de la colonne TypeModification...")
                cursor.execute("ALTER TABLE HISTORIQUE_LIVRAISON ADD TypeModification VARCHAR(50) NULL")
                print("   ✅ Colonne TypeModification ajoutée")
            else:
                print("\n4. Colonne TypeModification existe déjà")
            
            # Mettre à jour les valeurs par défaut
            print("\n5. Mise à jour des valeurs par défaut...")
            cursor.execute("""
                UPDATE HISTORIQUE_LIVRAISON 
                SET TypeModification = 'Modification Date' 
                WHERE TypeModification IS NULL
            """)
            print("   ✅ Valeurs par défaut mises à jour")
            
            # Afficher la structure finale
            print("\n6. Structure finale de la table COMMANDES:")
            cursor.execute("""
                SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'COMMANDES'
                ORDER BY ORDINAL_POSITION
            """)
            
            final_colonnes = cursor.fetchall()
            for col in final_colonnes:
                print(f"   • {col[0]} ({col[1]}) - {'NULL' if col[2] == 'YES' else 'NOT NULL'}")
            
            print("\n🎉 Migration terminée avec succès!")
            return True
            
    except Exception as e:
        print(f"\n❌ Erreur lors de la migration: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_after_migration():
    """Test des fonctions après migration"""
    print("\n🧪 Test des fonctions après migration...")
    
    try:
        from db import get_commandes_avec_suivi, get_statistiques_performance
        
        # Test des commandes avec suivi
        commandes = get_commandes_avec_suivi()
        print(f"   ✅ get_commandes_avec_suivi(): {len(commandes)} commandes")
        
        # Test des statistiques
        stats = get_statistiques_performance()
        print(f"   ✅ get_statistiques_performance(): {len(stats)} indicateurs")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erreur lors des tests: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Migration du module de suivi des délais")
    
    # Exécuter la migration
    success = execute_migration()
    
    if success:
        # Tester après migration
        test_success = test_after_migration()
        
        if test_success:
            print("\n✅ Migration et tests réussis!")
            print("\n🚀 Vous pouvez maintenant utiliser le module de suivi des délais:")
            print("   1. Lancez l'application: python app.py")
            print("   2. Accédez à: http://localhost:5000/projet1")
            print("   3. Testez les onglets Suivi et Performance")
        else:
            print("\n⚠️  Migration réussie mais tests échoués")
    else:
        print("\n❌ Migration échouée")
        sys.exit(1)

