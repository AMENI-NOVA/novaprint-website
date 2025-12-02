"""
Script pour ajouter la colonne RefFich à la table WEB_PdtNC_RecClt
et générer les références existantes
"""
from db import get_db_connection

def ajouter_colonne_reffich():
    """Ajoute la colonne RefFich à la table WEB_PdtNC_RecClt"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Vérifier si la colonne existe déjà
        cursor.execute("""
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'WEB_PdtNC_RecClt' 
            AND COLUMN_NAME = 'RefFich'
        """)
        
        if cursor.fetchone()[0] == 0:
            print("Ajout de la colonne RefFich...")
            cursor.execute("""
                ALTER TABLE WEB_PdtNC_RecClt
                ADD RefFich NVARCHAR(20) NULL
            """)
            conn.commit()
            print("✓ Colonne RefFich ajoutée avec succès")
        else:
            print("ℹ La colonne RefFich existe déjà")
        
        # Générer les références pour les enregistrements existants
        print("\nGénération des références pour les enregistrements existants...")
        
        # Pour les réclamations clients (REC)
        cursor.execute("""
            SELECT ID 
            FROM WEB_PdtNC_RecClt 
            WHERE TYPE = 'REC' AND (RefFich IS NULL OR RefFich = '')
            ORDER BY ID
        """)
        rec_ids = [row[0] for row in cursor.fetchall()]
        
        for i, rec_id in enumerate(rec_ids, start=1):
            ref = f"RCL {i:02d}"
            cursor.execute("""
                UPDATE WEB_PdtNC_RecClt 
                SET RefFich = ? 
                WHERE ID = ?
            """, (ref, rec_id))
            print(f"  REC ID {rec_id} → {ref}")
        
        # Pour les produits non conformes (NC)
        cursor.execute("""
            SELECT ID 
            FROM WEB_PdtNC_RecClt 
            WHERE TYPE = 'NC' AND (RefFich IS NULL OR RefFich = '')
            ORDER BY ID
        """)
        nc_ids = [row[0] for row in cursor.fetchall()]
        
        for i, nc_id in enumerate(nc_ids, start=1):
            ref = f"NCP {i:02d}"
            cursor.execute("""
                UPDATE WEB_PdtNC_RecClt 
                SET RefFich = ? 
                WHERE ID = ?
            """, (ref, nc_id))
            print(f"  NC ID {nc_id} → {ref}")
        
        conn.commit()
        print(f"\n✓ {len(rec_ids)} réclamations client et {len(nc_ids)} produits NC mis à jour")
        
    except Exception as e:
        print(f"❌ Erreur : {e}")
        conn.rollback()
        import traceback
        traceback.print_exc()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print("=" * 60)
    print("Ajout de la colonne RefFich pour le Projet 12")
    print("=" * 60)
    ajouter_colonne_reffich()
    print("\n✓ Terminé")


















