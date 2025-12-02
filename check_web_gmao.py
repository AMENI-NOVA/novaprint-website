"""
Script de vérification de la table WEB_GMAO pour le Projet 16
"""
from db import get_db_cursor

print("=" * 60)
print("VÉRIFICATION DE LA TABLE WEB_GMAO - PROJET 16")
print("=" * 60)
print()

try:
    with get_db_cursor() as cursor:
        # 1. Vérifier si la table existe
        print("1. Vérification de l'existence de la table WEB_GMAO...")
        cursor.execute("""
            SELECT COUNT(*) as table_exists
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_NAME = 'WEB_GMAO'
        """)
        result = cursor.fetchone()
        
        if result.table_exists == 0:
            print("   ❌ La table WEB_GMAO n'existe PAS dans la base de données!")
            print()
            print("   Pour créer la table, exécutez le script SQL:")
            print("   C:\\Apps\\create_web_gmao.sql")
        else:
            print("   ✅ La table WEB_GMAO existe!")
            print()
            
            # 2. Vérifier la structure
            print("2. Structure de la table WEB_GMAO:")
            cursor.execute("""
                SELECT 
                    COLUMN_NAME,
                    DATA_TYPE,
                    CHARACTER_MAXIMUM_LENGTH,
                    IS_NULLABLE
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_NAME = 'WEB_GMAO'
                ORDER BY ORDINAL_POSITION
            """)
            
            columns = cursor.fetchall()
            print(f"   Nombre de colonnes: {len(columns)}")
            print()
            print("   Colonnes:")
            for col in columns:
                length = f"({col.CHARACTER_MAXIMUM_LENGTH})" if col.CHARACTER_MAXIMUM_LENGTH else ""
                nullable = "NULL" if col.IS_NULLABLE == "YES" else "NOT NULL"
                print(f"   - {col.COLUMN_NAME:<25} {col.DATA_TYPE}{length:<15} {nullable}")
            print()
            
            # 3. Compter les enregistrements
            print("3. Nombre d'enregistrements dans WEB_GMAO:")
            cursor.execute("SELECT COUNT(*) as total FROM WEB_GMAO")
            total = cursor.fetchone().total
            print(f"   Total: {total} enregistrement(s)")
            print()
            
            # 4. Afficher les derniers enregistrements
            if total > 0:
                print("4. Derniers enregistrements (max 5):")
                cursor.execute("""
                    SELECT TOP 5
                        ID,
                        Code,
                        DteRec,
                        OperRec,
                        PostesReel,
                        Reclamation,
                        DateCreation
                    FROM WEB_GMAO
                    ORDER BY DateCreation DESC
                """)
                
                records = cursor.fetchall()
                for rec in records:
                    print(f"   ID: {rec.ID}")
                    print(f"   Code: {rec.Code}")
                    print(f"   Date Réclamation: {rec.DteRec}")
                    print(f"   Opérateur: {rec.OperRec}")
                    print(f"   Machine: {rec.PostesReel}")
                    print(f"   Description: {rec.Reclamation[:50] if rec.Reclamation else 'N/A'}")
                    print(f"   Créé le: {rec.DateCreation}")
                    print("   " + "-" * 50)
            print()
            
            # 5. Vérifier les tables liées
            print("5. Vérification des tables liées:")
            
            # Table personel
            try:
                cursor.execute("SELECT COUNT(*) as total FROM personel")
                total_personel = cursor.fetchone().total
                print(f"   ✅ Table 'personel': {total_personel} enregistrement(s)")
            except Exception as e:
                print(f"   ❌ Table 'personel': Erreur - {e}")
            
            # Table GP_POSTES
            try:
                cursor.execute("SELECT COUNT(*) as total FROM GP_POSTES")
                total_postes = cursor.fetchone().total
                print(f"   ✅ Table 'GP_POSTES': {total_postes} enregistrement(s)")
            except Exception as e:
                print(f"   ❌ Table 'GP_POSTES': Erreur - {e}")
            
            # Table GS_ARTICLES
            try:
                cursor.execute("SELECT COUNT(*) as total FROM GS_ARTICLES")
                total_articles = cursor.fetchone().total
                print(f"   ✅ Table 'GS_ARTICLES': {total_articles} enregistrement(s)")
            except Exception as e:
                print(f"   ❌ Table 'GS_ARTICLES': Erreur - {e}")

except Exception as e:
    print(f"❌ ERREUR: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 60)
print("FIN DE LA VÉRIFICATION")
print("=" * 60)

