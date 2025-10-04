#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pyodbc
import json
from datetime import datetime

def backup_controle_qualite():
    """Sauvegarde les tables de contrôle qualité dans un fichier JSON"""
    
    # Configuration de la base de données
    db_config = {
        "DRIVER": "{SQL Server}",
        "SERVER": "LAPTOP-LATIFA",
        "DATABASE": "novaprint",
        "Trusted_Connection": "yes",
        "TrustServerCertificate": "yes"
    }
    
    print("=== Sauvegarde des tables de controle qualite ===")
    
    try:
        # Connexion à la base de données
        connection_string = f"DRIVER={db_config['DRIVER']};SERVER={db_config['SERVER']};DATABASE={db_config['DATABASE']};Trusted_Connection={db_config['Trusted_Connection']};TrustServerCertificate={db_config['TrustServerCertificate']}"
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        print("Connexion a la base de donnees reussie")
        
        # Sauvegarde de CONTROLES_QUALITE
        print("\nSauvegarde de CONTROLES_QUALITE...")
        cursor.execute("SELECT * FROM CONTROLES_QUALITE")
        controles_rows = cursor.fetchall()
        
        # Récupérer les noms des colonnes
        cursor.execute("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'CONTROLES_QUALITE'
            ORDER BY ORDINAL_POSITION
        """)
        controles_columns = [row[0] for row in cursor.fetchall()]
        
        controles_data = []
        for row in controles_rows:
            controles_data.append(dict(zip(controles_columns, row)))
        
        print(f"  {len(controles_data)} enregistrements sauvegardes")
        
        # Sauvegarde de TOLERANCES_CONTROLE
        print("Sauvegarde de TOLERANCES_CONTROLE...")
        cursor.execute("SELECT * FROM TOLERANCES_CONTROLE")
        tolerances_rows = cursor.fetchall()
        
        # Récupérer les noms des colonnes
        cursor.execute("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'TOLERANCES_CONTROLE'
            ORDER BY ORDINAL_POSITION
        """)
        tolerances_columns = [row[0] for row in cursor.fetchall()]
        
        tolerances_data = []
        for row in tolerances_rows:
            tolerances_data.append(dict(zip(tolerances_columns, row)))
        
        print(f"  {len(tolerances_data)} enregistrements sauvegardes")
        
        # Créer le fichier de sauvegarde
        backup_data = {
            "timestamp": datetime.now().isoformat(),
            "database": db_config['DATABASE'],
            "server": db_config['SERVER'],
            "tables": {
                "CONTROLES_QUALITE": {
                    "columns": controles_columns,
                    "data": controles_data
                },
                "TOLERANCES_CONTROLE": {
                    "columns": tolerances_columns,
                    "data": tolerances_data
                }
            }
        }
        
        # Sauvegarder dans un fichier JSON
        backup_filename = f"backup_controle_qualite_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(backup_filename, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"\nSauvegarde creee: {backup_filename}")
        print(f"Total: {len(controles_data)} controles et {len(tolerances_data)} tolérances")
        
        return backup_filename
        
    except Exception as e:
        print(f"Erreur lors de la sauvegarde: {e}")
        return None
    finally:
        if 'conn' in locals():
            conn.close()
            print("Connexion fermee")

def restore_controle_qualite(backup_filename):
    """Restaure les tables de contrôle qualité depuis un fichier JSON"""
    
    print(f"=== Restauration depuis {backup_filename} ===")
    
    try:
        # Lire le fichier de sauvegarde
        with open(backup_filename, 'r', encoding='utf-8') as f:
            backup_data = json.load(f)
        
        print(f"Fichier de sauvegarde du: {backup_data['timestamp']}")
        print(f"Base source: {backup_data['database']} sur {backup_data['server']}")
        
        # Configuration de la base de destination
        db_config = {
            "DRIVER": "{SQL Server}",
            "SERVER": "LAPTOP-LATIFA",
            "DATABASE": "novaprint",  # À modifier selon votre nouvelle base
            "Trusted_Connection": "yes",
            "TrustServerCertificate": "yes"
        }
        
        # Connexion à la base de destination
        connection_string = f"DRIVER={db_config['DRIVER']};SERVER={db_config['SERVER']};DATABASE={db_config['DATABASE']};Trusted_Connection={db_config['Trusted_Connection']};TrustServerCertificate={db_config['TrustServerCertificate']}"
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        print("Connexion a la base de destination reussie")
        
        # Vérifier si les tables existent
        cursor.execute("""
            SELECT TABLE_NAME 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_NAME IN ('CONTROLES_QUALITE', 'TOLERANCES_CONTROLE')
        """)
        existing_tables = [row[0] for row in cursor.fetchall()]
        
        if 'CONTROLES_QUALITE' not in existing_tables:
            print("Creation de la table CONTROLES_QUALITE...")
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
            print("Table CONTROLES_QUALITE creee")
        
        if 'TOLERANCES_CONTROLE' not in existing_tables:
            print("Creation de la table TOLERANCES_CONTROLE...")
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
            print("Table TOLERANCES_CONTROLE creee")
        
        # Restaurer les données
        controles_data = backup_data['tables']['CONTROLES_QUALITE']['data']
        tolerances_data = backup_data['tables']['TOLERANCES_CONTROLE']['data']
        
        print(f"\nRestauration de {len(controles_data)} controles...")
        for controle in controles_data:
            # Exclure l'ID pour permettre la régénération automatique
            controle_copy = controle.copy()
            if 'id' in controle_copy:
                del controle_copy['id']
            
            columns = list(controle_copy.keys())
            values = list(controle_copy.values())
            placeholders = ', '.join(['?' for _ in columns])
            
            insert_sql = f"INSERT INTO CONTROLES_QUALITE ({', '.join(columns)}) VALUES ({placeholders})"
            cursor.execute(insert_sql, values)
        
        print(f"Restauration de {len(tolerances_data)} tolérances...")
        for tolerance in tolerances_data:
            # Exclure l'ID pour permettre la régénération automatique
            tolerance_copy = tolerance.copy()
            if 'id' in tolerance_copy:
                del tolerance_copy['id']
            
            columns = list(tolerance_copy.keys())
            values = list(tolerance_copy.values())
            placeholders = ', '.join(['?' for _ in columns])
            
            insert_sql = f"INSERT INTO TOLERANCES_CONTROLE ({', '.join(columns)}) VALUES ({placeholders})"
            cursor.execute(insert_sql, values)
        
        # Valider les modifications
        conn.commit()
        print("\nRestauration terminee avec succes!")
        
    except Exception as e:
        print(f"Erreur lors de la restauration: {e}")
        if 'conn' in locals():
            conn.rollback()
        return False
    finally:
        if 'conn' in locals():
            conn.close()
            print("Connexion fermee")
    
    return True

if __name__ == "__main__":
    print("Script de sauvegarde/restauration controle qualite")
    print("=" * 60)
    
    choice = input("""
Choisissez une option:
1. Creer une sauvegarde
2. Restaurer depuis une sauvegarde
3. Annuler

Votre choix (1-3): """)
    
    if choice == "1":
        backup_controle_qualite()
    elif choice == "2":
        backup_filename = input("Nom du fichier de sauvegarde: ").strip()
        if backup_filename:
            restore_controle_qualite(backup_filename)
        else:
            print("Nom de fichier invalide")
    else:
        print("Operation annulee")
