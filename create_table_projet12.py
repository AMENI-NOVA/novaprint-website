"""
Script pour créer la table WEB_PdtNC_RecClt pour le Projet 12
Registre de suivi des Produits Non Conformes et des Réclamations Clients
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
    
    # Script SQL pour créer la table
    create_table_sql = """
    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='WEB_PdtNC_RecClt' AND xtype='U')
    CREATE TABLE WEB_PdtNC_RecClt (
        ID INT IDENTITY(1,1) PRIMARY KEY,
        Date DATETIME NULL,
        TYPE NVARCHAR(10) NULL,
        NC NVARCHAR(500) NULL,
        DesNC NVARCHAR(MAX) NULL,
        Cause NVARCHAR(MAX) NULL,
        Numero_COMMANDES NVARCHAR(100) NULL,
        Reference_COMMANDES NVARCHAR(200) NULL,
        RaiSocTri_SOCIETES NVARCHAR(200) NULL
    )
    """
    
    # Exécution du script
    cursor.execute(create_table_sql)
    conn.commit()
    
    print("✓ Table WEB_PdtNC_RecClt créée avec succès!")
    
    # Vérification
    cursor.execute("SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'WEB_PdtNC_RecClt'")
    count = cursor.fetchone()[0]
    
    if count == 1:
        print("✓ Vérification réussie : la table existe dans la base de données")
    else:
        print("✗ Erreur : la table n'a pas été créée correctement")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"✗ Erreur lors de la création de la table : {e}")

