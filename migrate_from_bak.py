#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pyodbc
import os
from datetime import datetime

def migrate_from_bak_file():
    """Migre depuis un fichier .BAK en préservant les nouvelles tables de contrôle qualité"""
    
    print("=== Migration depuis fichier .BAK ===")
    print("Ce script va:")
    print("1. Sauvegarder les nouvelles tables de controle qualite")
    print("2. Restaurer le fichier .BAK")
    print("3. Recréer les nouvelles tables")
    print("4. Restaurer les données sauvegardées")
    print()
    
    # Configuration de la base actuelle
    current_db_config = {
        "DRIVER": "{SQL Server}",
        "SERVER": "LAPTOP-LATIFA",
        "DATABASE": "novaprint",
        "Trusted_Connection": "yes",
        "TrustServerCertificate": "yes"
    }
    
    # Demander le chemin du fichier .BAK
    bak_file_path = input("Chemin complet du fichier .BAK: ").strip()
    if not bak_file_path:
        print("Erreur: Chemin du fichier .BAK requis")
        return False
    
    if not os.path.exists(bak_file_path):
        print(f"Erreur: Fichier {bak_file_path} introuvable")
        return False
    
    if not bak_file_path.lower().endswith('.bak'):
        print("Erreur: Le fichier doit avoir l'extension .BAK")
        return False
    
    # Demander le nom de la nouvelle base de données
    new_database_name = input("Nom de la nouvelle base de données (ex: novaprint_new): ").strip()
    if not new_database_name:
        print("Erreur: Nom de base de données requis")
        return False
    
    try:
        # Étape 1: Sauvegarder les nouvelles tables
        print("\n=== Étape 1: Sauvegarde des nouvelles tables ===")
        backup_data = backup_new_tables(current_db_config)
        if not backup_data:
            print("Erreur lors de la sauvegarde")
            return False
        
        # Étape 2: Restaurer le fichier .BAK
        print("\n=== Étape 2: Restauration du fichier .BAK ===")
        if not restore_bak_file(bak_file_path, new_database_name):
            print("Erreur lors de la restauration")
            return False
        
        # Étape 3: Recréer les nouvelles tables
        print("\n=== Étape 3: Recréation des nouvelles tables ===")
        new_db_config = {
            "DRIVER": "{SQL Server}",
            "SERVER": "LAPTOP-LATIFA",
            "DATABASE": new_database_name,
            "Trusted_Connection": "yes",
            "TrustServerCertificate": "yes"
        }
        
        if not create_new_tables(new_db_config):
            print("Erreur lors de la création des tables")
            return False
        
        # Étape 4: Restaurer les données sauvegardées
        print("\n=== Étape 4: Restauration des données ===")
        if not restore_backup_data(new_db_config, backup_data):
            print("Erreur lors de la restauration des données")
            return False
        
        # Étape 5: Mettre à jour la configuration
        print("\n=== Étape 5: Mise à jour de la configuration ===")
        update_db_config_file(new_database_name)
        
        print("\n=== Migration terminée avec succès! ===")
        print(f"Nouvelle base de données: {new_database_name}")
        print("Les nouvelles tables de contrôle qualité ont été préservées")
        
        return True
        
    except Exception as e:
        print(f"Erreur lors de la migration: {e}")
        return False

def backup_new_tables(db_config):
    """Sauvegarde les nouvelles tables de contrôle qualité"""
    
    try:
        connection_string = f"DRIVER={db_config['DRIVER']};SERVER={db_config['SERVER']};DATABASE={db_config['DATABASE']};Trusted_Connection={db_config['Trusted_Connection']};TrustServerCertificate={db_config['TrustServerCertificate']}"
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        
        backup_data = {}
        
        # Vérifier si les tables existent
        cursor.execute("""
            SELECT TABLE_NAME 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_NAME IN ('CONTROLES_QUALITE', 'TOLERANCES_CONTROLE')
        """)
        existing_tables = [row[0] for row in cursor.fetchall()]
        
        if not existing_tables:
            print("Aucune table de contrôle qualité à sauvegarder")
            return {}
        
        # Sauvegarder CONTROLES_QUALITE
        if 'CONTROLES_QUALITE' in existing_tables:
            print("Sauvegarde de CONTROLES_QUALITE...")
            cursor.execute("SELECT * FROM CONTROLES_QUALITE")
            rows = cursor.fetchall()
            
            cursor.execute("""
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'CONTROLES_QUALITE'
                ORDER BY ORDINAL_POSITION
            """)
            columns = [row[0] for row in cursor.fetchall()]
            
            backup_data['CONTROLES_QUALITE'] = {
                'columns': columns,
                'data': [dict(zip(columns, row)) for row in rows]
            }
            print(f"  {len(rows)} enregistrements sauvegardés")
        
        # Sauvegarder TOLERANCES_CONTROLE
        if 'TOLERANCES_CONTROLE' in existing_tables:
            print("Sauvegarde de TOLERANCES_CONTROLE...")
            cursor.execute("SELECT * FROM TOLERANCES_CONTROLE")
            rows = cursor.fetchall()
            
            cursor.execute("""
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'TOLERANCES_CONTROLE'
                ORDER BY ORDINAL_POSITION
            """)
            columns = [row[0] for row in cursor.fetchall()]
            
            backup_data['TOLERANCES_CONTROLE'] = {
                'columns': columns,
                'data': [dict(zip(columns, row)) for row in rows]
            }
            print(f"  {len(rows)} enregistrements sauvegardés")
        
        conn.close()
        return backup_data
        
    except Exception as e:
        print(f"Erreur lors de la sauvegarde: {e}")
        return None

def restore_bak_file(bak_file_path, new_database_name):
    """Restaure un fichier .BAK vers une nouvelle base de données"""
    
    try:
        # Connexion au serveur SQL (sans base spécifique)
        master_conn_string = f"DRIVER={{SQL Server}};SERVER=LAPTOP-LATIFA;DATABASE=master;Trusted_Connection=yes;TrustServerCertificate=yes"
        conn = pyodbc.connect(master_conn_string)
        cursor = conn.cursor()
        
        print(f"Restauration de {bak_file_path} vers {new_database_name}...")
        
        # Vérifier si la base existe déjà
        cursor.execute(f"SELECT name FROM sys.databases WHERE name = '{new_database_name}'")
        if cursor.fetchone():
            print(f"La base {new_database_name} existe déjà. Suppression...")
            cursor.execute(f"DROP DATABASE [{new_database_name}]")
        
        # Restaurer la base de données
        restore_sql = f"""
        RESTORE DATABASE [{new_database_name}]
        FROM DISK = '{bak_file_path}'
        WITH 
            MOVE 'novaprint' TO 'C:\\Program Files\\Microsoft SQL Server\\MSSQL15.MSSQLSERVER\\MSSQL\\DATA\\{new_database_name}.mdf',
            MOVE 'novaprint_log' TO 'C:\\Program Files\\Microsoft SQL Server\\MSSQL15.MSSQLSERVER\\MSSQL\\DATA\\{new_database_name}_log.ldf',
            REPLACE
        """
        
        cursor.execute(restore_sql)
        conn.commit()
        
        print(f"Base de données {new_database_name} restaurée avec succès")
        conn.close()
        return True
        
    except Exception as e:
        print(f"Erreur lors de la restauration: {e}")
        print("Note: Vérifiez que le chemin du fichier .BAK est accessible par SQL Server")
        return False

def create_new_tables(db_config):
    """Crée les nouvelles tables de contrôle qualité dans la base restaurée"""
    
    try:
        connection_string = f"DRIVER={db_config['DRIVER']};SERVER={db_config['SERVER']};DATABASE={db_config['DATABASE']};Trusted_Connection={db_config['Trusted_Connection']};TrustServerCertificate={db_config['TrustServerCertificate']}"
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        
        # Vérifier si les tables existent déjà
        cursor.execute("""
            SELECT TABLE_NAME 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_NAME IN ('CONTROLES_QUALITE', 'TOLERANCES_CONTROLE')
        """)
        existing_tables = [row[0] for row in cursor.fetchall()]
        
        # Créer CONTROLES_QUALITE si elle n'existe pas
        if 'CONTROLES_QUALITE' not in existing_tables:
            print("Création de la table CONTROLES_QUALITE...")
            cursor.execute("""
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
            print("Table CONTROLES_QUALITE créée")
        else:
            print("Table CONTROLES_QUALITE existe déjà")
        
        # Créer TOLERANCES_CONTROLE si elle n'existe pas
        if 'TOLERANCES_CONTROLE' not in existing_tables:
            print("Création de la table TOLERANCES_CONTROLE...")
            cursor.execute("""
                CREATE TABLE TOLERANCES_CONTROLE (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    controle_id INT NOT NULL,
                    tolerance NVARCHAR(200),
                    quantite_conforme INT DEFAULT 0,
                    quantite_non_conforme INT DEFAULT 0,
                    FOREIGN KEY (controle_id) REFERENCES CONTROLES_QUALITE(id) ON DELETE CASCADE
                )
            """)
            print("Table TOLERANCES_CONTROLE créée")
        else:
            print("Table TOLERANCES_CONTROLE existe déjà")
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"Erreur lors de la création des tables: {e}")
        return False

def restore_backup_data(db_config, backup_data):
    """Restaure les données sauvegardées dans les nouvelles tables"""
    
    try:
        connection_string = f"DRIVER={db_config['DRIVER']};SERVER={db_config['SERVER']};DATABASE={db_config['DATABASE']};Trusted_Connection={db_config['Trusted_Connection']};TrustServerCertificate={db_config['TrustServerCertificate']}"
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        
        # Restaurer CONTROLES_QUALITE
        if 'CONTROLES_QUALITE' in backup_data:
            print("Restauration des données CONTROLES_QUALITE...")
            data = backup_data['CONTROLES_QUALITE']['data']
            
            for row in data:
                # Exclure l'ID pour permettre la régénération automatique
                row_copy = row.copy()
                if 'id' in row_copy:
                    del row_copy['id']
                
                columns = list(row_copy.keys())
                values = list(row_copy.values())
                placeholders = ', '.join(['?' for _ in columns])
                
                insert_sql = f"INSERT INTO CONTROLES_QUALITE ({', '.join(columns)}) VALUES ({placeholders})"
                cursor.execute(insert_sql, values)
            
            print(f"  {len(data)} enregistrements restaurés")
        
        # Restaurer TOLERANCES_CONTROLE
        if 'TOLERANCES_CONTROLE' in backup_data:
            print("Restauration des données TOLERANCES_CONTROLE...")
            data = backup_data['TOLERANCES_CONTROLE']['data']
            
            for row in data:
                # Exclure l'ID pour permettre la régénération automatique
                row_copy = row.copy()
                if 'id' in row_copy:
                    del row_copy['id']
                
                columns = list(row_copy.keys())
                values = list(row_copy.values())
                placeholders = ', '.join(['?' for _ in columns])
                
                insert_sql = f"INSERT INTO TOLERANCES_CONTROLE ({', '.join(columns)}) VALUES ({placeholders})"
                cursor.execute(insert_sql, values)
            
            print(f"  {len(data)} enregistrements restaurés")
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"Erreur lors de la restauration des données: {e}")
        return False

def update_db_config_file(new_database_name):
    """Met à jour le fichier db.py pour pointer vers la nouvelle base"""
    
    try:
        # Lire le fichier db.py
        with open('db.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Nouvelle configuration
        new_config = f'''DB_CONFIG = {{
    "DRIVER": "{{SQL Server}}",
    "SERVER": "LAPTOP-LATIFA",
    "DATABASE": "{new_database_name}",
    "Trusted_Connection": "yes",
    "TrustServerCertificate": "yes"
}}'''
        
        # Remplacer l'ancienne configuration
        import re
        pattern = r'DB_CONFIG = \{[^}]+\}'
        new_content = re.sub(pattern, new_config, content, flags=re.DOTALL)
        
        # Sauvegarder
        with open('db.py', 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"Configuration db.py mise à jour vers: {new_database_name}")
        return True
        
    except Exception as e:
        print(f"Erreur lors de la mise à jour de db.py: {e}")
        return False

if __name__ == "__main__":
    print("Script de migration depuis fichier .BAK")
    print("=" * 50)
    
    print("ATTENTION: Ce script va:")
    print("- Sauvegarder les nouvelles tables de contrôle qualité")
    print("- Restaurer le fichier .BAK vers une nouvelle base")
    print("- Recréer les nouvelles tables")
    print("- Restaurer les données sauvegardées")
    print("- Mettre à jour la configuration db.py")
    print()
    
    response = input("Voulez-vous continuer? (oui/non): ")
    if response.lower() == 'oui':
        migrate_from_bak_file()
    else:
        print("Migration annulée")
