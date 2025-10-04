#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pyodbc
from datetime import datetime

def migrate_database():
    """Migre la base de données en préservant les nouvelles tables de contrôle qualité"""
    
    # Configuration de la base actuelle (NOVAPRINT)
    current_db_config = {
        "DRIVER": "{SQL Server}",
        "SERVER": "LAPTOP-LATIFA",
        "DATABASE": "novaprint",
        "Trusted_Connection": "yes",
        "TrustServerCertificate": "yes"
    }
    
    # Configuration de la nouvelle base (à définir)
    new_db_config = {
        "DRIVER": "{SQL Server}",
        "SERVER": "LAPTOP-LATIFA",  # À modifier selon votre nouvelle base
        "DATABASE": "novaprint_new",  # À modifier selon votre nouvelle base
        "Trusted_Connection": "yes",
        "TrustServerCertificate": "yes"
    }
    
    print("=== Migration de la base de donnees ===")
    print(f"Source: {current_db_config['DATABASE']}")
    print(f"Destination: {new_db_config['DATABASE']}")
    print()
    
    try:
        # Connexion à la base actuelle
        current_conn_string = f"DRIVER={current_db_config['DRIVER']};SERVER={current_db_config['SERVER']};DATABASE={current_db_config['DATABASE']};Trusted_Connection={current_db_config['Trusted_Connection']};TrustServerCertificate={current_db_config['TrustServerCertificate']}"
        current_conn = pyodbc.connect(current_conn_string)
        current_cursor = current_conn.cursor()
        print("Connexion a la base source reussie")
        
        # Connexion à la nouvelle base
        new_conn_string = f"DRIVER={new_db_config['DRIVER']};SERVER={new_db_config['SERVER']};DATABASE={new_db_config['DATABASE']};Trusted_Connection={new_db_config['Trusted_Connection']};TrustServerCertificate={new_db_config['TrustServerCertificate']}"
        new_conn = pyodbc.connect(new_conn_string)
        new_cursor = new_conn.cursor()
        print("Connexion a la base destination reussie")
        
        # 1. Lister toutes les tables de la base source
        current_cursor.execute("""
            SELECT TABLE_NAME 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_TYPE = 'BASE TABLE'
            ORDER BY TABLE_NAME
        """)
        source_tables = [row[0] for row in current_cursor.fetchall()]
        print(f"\nTables trouvees dans la base source: {len(source_tables)}")
        for table in source_tables:
            print(f"  - {table}")
        
        # 2. Lister les tables de la base destination
        new_cursor.execute("""
            SELECT TABLE_NAME 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_TYPE = 'BASE TABLE'
            ORDER BY TABLE_NAME
        """)
        dest_tables = [row[0] for row in new_cursor.fetchall()]
        print(f"\nTables trouvees dans la base destination: {len(dest_tables)}")
        for table in dest_tables:
            print(f"  - {table}")
        
        # 3. Identifier les nouvelles tables (contrôle qualité)
        new_tables = ['CONTROLES_QUALITE', 'TOLERANCES_CONTROLE']
        existing_tables = [table for table in source_tables if table not in new_tables]
        
        print(f"\nNouvelles tables a preserver: {new_tables}")
        print(f"Tables existantes a migrer: {len(existing_tables)}")
        
        # 4. Créer les nouvelles tables dans la base destination si elles n'existent pas
        for table_name in new_tables:
            if table_name not in dest_tables:
                print(f"\nCreation de la table {table_name}...")
                
                if table_name == 'CONTROLES_QUALITE':
                    new_cursor.execute("""
                        CREATE TABLE CONTROLES_QUALITE (
                            id INT IDENTITY(1,1) PRIMARY KEY,
                            date_controle DATE NOT NULL,
                            numero_dossier NVARCHAR(50) NOT NULL,
                            operateur NVARCHAR(100) NOT NULL,
                            machine_impression NVARCHAR(100),
                            operateur_machine_impression NVARCHAR(500),
                            machine_decoupe NVARCHAR(100),
                            operateur_machine_decoupe NVARCHAR(500),
                            rebus INT DEFAULT 0,
                            validation_chef NVARCHAR(100),
                            date_creation DATETIME DEFAULT GETDATE()
                        )
                    """)
                    print(f"Table {table_name} creee")
                    
                elif table_name == 'TOLERANCES_CONTROLE':
                    new_cursor.execute("""
                        CREATE TABLE TOLERANCES_CONTROLE (
                            id INT IDENTITY(1,1) PRIMARY KEY,
                            controle_id INT NOT NULL,
                            tolerance NVARCHAR(200),
                            quantite_conforme INT DEFAULT 0,
                            quantite_non_conforme INT DEFAULT 0,
                            FOREIGN KEY (controle_id) REFERENCES CONTROLES_QUALITE(id) ON DELETE CASCADE
                        )
                    """)
                    print(f"Table {table_name} creee")
            else:
                print(f"Table {table_name} existe deja dans la destination")
        
        # 5. Migrer les données des nouvelles tables
        for table_name in new_tables:
            if table_name in source_tables:
                print(f"\nMigration des donnees de {table_name}...")
                
                # Compter les enregistrements
                current_cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = current_cursor.fetchone()[0]
                print(f"  Enregistrements a migrer: {count}")
                
                if count > 0:
                    # Récupérer les données
                    current_cursor.execute(f"SELECT * FROM {table_name}")
                    rows = current_cursor.fetchall()
                    
                    # Récupérer les noms des colonnes
                    current_cursor.execute(f"""
                        SELECT COLUMN_NAME 
                        FROM INFORMATION_SCHEMA.COLUMNS 
                        WHERE TABLE_NAME = '{table_name}' 
                        ORDER BY ORDINAL_POSITION
                    """)
                    columns = [row[0] for row in current_cursor.fetchall()]
                    
                    # Insérer les données
                    for row in rows:
                        placeholders = ', '.join(['?' for _ in columns])
                        insert_sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
                        new_cursor.execute(insert_sql, row)
                    
                    print(f"{count} enregistrements migres vers {table_name}")
                else:
                    print(f"Aucune donnee a migrer pour {table_name}")
        
        # 6. Valider les modifications
        new_conn.commit()
        print("\nMigration terminee avec succes!")
        
        # 7. Vérification finale
        print("\nVerification finale:")
        new_cursor.execute("""
            SELECT TABLE_NAME 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_TYPE = 'BASE TABLE'
            ORDER BY TABLE_NAME
        """)
        final_tables = [row[0] for row in new_cursor.fetchall()]
        
        print(f"Tables dans la base destination: {len(final_tables)}")
        for table in final_tables:
            print(f"  - {table}")
        
        # Compter les données dans les nouvelles tables
        for table_name in new_tables:
            if table_name in final_tables:
                new_cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = new_cursor.fetchone()[0]
                print(f"  {table_name}: {count} enregistrements")
        
    except Exception as e:
        print(f"Erreur lors de la migration: {e}")
        if 'new_conn' in locals():
            new_conn.rollback()
        return False
    finally:
        if 'current_conn' in locals():
            current_conn.close()
        if 'new_conn' in locals():
            new_conn.close()
        print("\nConnexions fermees")
    
    return True

def update_db_config():
    """Met à jour la configuration de db.py pour pointer vers la nouvelle base"""
    
    print("\n=== Mise a jour de la configuration ===")
    print("ATTENTION: Cette fonction va modifier db.py")
    print("Assurez-vous d'avoir fait une sauvegarde avant de continuer.")
    
    response = input("Voulez-vous continuer? (oui/non): ")
    if response.lower() != 'oui':
        print("Mise a jour annulee")
        return
    
    # Nouvelle configuration (à adapter selon vos besoins)
    new_server = input("Nouveau serveur (actuel: LAPTOP-LATIFA): ").strip() or "LAPTOP-LATIFA"
    new_database = input("Nouvelle base de données (actuel: novaprint): ").strip() or "novaprint"
    
    # Lire le fichier db.py
    with open('db.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remplacer la configuration
    new_config = f'''DB_CONFIG = {{
    "DRIVER": "{{SQL Server}}",
    "SERVER": "{new_server}",
    "DATABASE": "{new_database}",
    "Trusted_Connection": "yes",
    "TrustServerCertificate": "yes"
}}'''
    
    # Trouver et remplacer l'ancienne configuration
    import re
    pattern = r'DB_CONFIG = \{[^}]+\}'
    new_content = re.sub(pattern, new_config, content, flags=re.DOTALL)
    
    # Sauvegarder
    with open('db.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"Configuration mise a jour:")
    print(f"   Serveur: {new_server}")
    print(f"   Base de donnees: {new_database}")

if __name__ == "__main__":
    print("Script de migration de base de donnees")
    print("=" * 50)
    
    choice = input("""
Choisissez une option:
1. Migrer les donnees (preserver les nouvelles tables)
2. Mettre a jour la configuration db.py
3. Les deux
4. Annuler

Votre choix (1-4): """)
    
    if choice == "1":
        migrate_database()
    elif choice == "2":
        update_db_config()
    elif choice == "3":
        if migrate_database():
            update_db_config()
    else:
        print("Operation annulee")
