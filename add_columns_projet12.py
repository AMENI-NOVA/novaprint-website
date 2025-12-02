"""
Script pour ajouter les colonnes QteComm_COMMANDES et QteNC à la table WEB_PdtNC_RecClt
"""
import pyodbc

# Configuration de connexion (même que db.py)
DB_CONFIG = {
    "DRIVER": "{SQL Server}",
    "SERVER": "LAPTOP-LATIFA",
    "DATABASE": "novaprint_restored",
    "Trusted_Connection": "yes",
    "TrustServerCertificate": "yes"
}

# Chaîne de connexion
conn_str = ";".join(f"{k}={v}" for k, v in DB_CONFIG.items())

try:
    # Connexion à la base de données
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    
    print("Ajout des colonnes QteComm_COMMANDES et QteNC...")
    
    # Ajouter la colonne QteComm_COMMANDES
    try:
        cursor.execute("""
            ALTER TABLE WEB_PdtNC_RecClt
            ADD QteComm_COMMANDES INT NULL
        """)
        print("✓ Colonne QteComm_COMMANDES ajoutée")
    except Exception as e:
        if "already exists" in str(e) or "existe déjà" in str(e):
            print("→ Colonne QteComm_COMMANDES existe déjà")
        else:
            print(f"✗ Erreur pour QteComm_COMMANDES: {e}")
    
    # Ajouter la colonne QteNC
    try:
        cursor.execute("""
            ALTER TABLE WEB_PdtNC_RecClt
            ADD QteNC INT NULL
        """)
        print("✓ Colonne QteNC ajoutée")
    except Exception as e:
        if "already exists" in str(e) or "existe déjà" in str(e):
            print("→ Colonne QteNC existe déjà")
        else:
            print(f"✗ Erreur pour QteNC: {e}")
    
    conn.commit()
    
    # Vérification
    cursor.execute("""
        SELECT COLUMN_NAME 
        FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_NAME = 'WEB_PdtNC_RecClt'
        ORDER BY ORDINAL_POSITION
    """)
    
    print("\n✓ Colonnes de la table WEB_PdtNC_RecClt :")
    for row in cursor.fetchall():
        print(f"  - {row.COLUMN_NAME}")
    
    cursor.close()
    conn.close()
    
    print("\n✓ Modifications terminées avec succès!")
    
except Exception as e:
    print(f"✗ Erreur lors de la modification de la table : {e}")




















