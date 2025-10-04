#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pyodbc
import json
import os
from datetime import datetime

def restore_qualite_tables():
    """Crée les tables de contrôle qualité et restaure les données dans novaprint_restored"""
    
    # Configuration de la nouvelle base
    new_db_config = {
        "DRIVER": "{SQL Server}",
        "SERVER": "LAPTOP-LATIFA",
        "DATABASE": "novaprint_restored",
        "Trusted_Connection": "yes",
        "TrustServerCertificate": "yes"
    }
    
    try:
        # Trouver le fichier de sauvegarde le plus récent
        backup_files = [f for f in os.listdir('.') if f.startswith('backup_qualite_') and f.endswith('.json')]
        if not backup_files:
            print("Aucun fichier de sauvegarde trouvé")
            return False
        
        latest_backup = max(backup_files)
        print(f"Utilisation du fichier de sauvegarde: {latest_backup}")
        
        # Charger les données de sauvegarde
        with open(latest_backup, 'r', encoding='utf-8') as f:
            backup_data = json.load(f)
        
        # Connexion à la nouvelle base
        connection_string = f"DRIVER={new_db_config['DRIVER']};SERVER={new_db_config['SERVER']};DATABASE={new_db_config['DATABASE']};Trusted_Connection={new_db_config['Trusted_Connection']};TrustServerCertificate={new_db_config['TrustServerCertificate']}"
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        
        print("=== Création des tables de contrôle qualité ===")
        
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
        
        print("\n=== Nettoyage des données existantes ===")
        
        # Vider les tables existantes
        if 'TOLERANCES_CONTROLE' in existing_tables:
            cursor.execute("DELETE FROM TOLERANCES_CONTROLE")
            print("Table TOLERANCES_CONTROLE vidée")
        
        if 'CONTROLES_QUALITE' in existing_tables:
            cursor.execute("DELETE FROM CONTROLES_QUALITE")
            print("Table CONTROLES_QUALITE vidée")
        
        conn.commit()
        
        print("\n=== Restauration des données ===")
        
        # Restaurer les données CONTROLES_QUALITE
        if 'CONTROLES_QUALITE' in backup_data['tables']:
            print("Restauration des données CONTROLES_QUALITE...")
            data = backup_data['tables']['CONTROLES_QUALITE']['data']
            
            # Mapping des anciens ID vers les nouveaux ID
            id_mapping = {}
            
            for row in data:
                old_id = row.get('id')
                
                # Exclure l'ID pour permettre la régénération automatique
                row_copy = row.copy()
                if 'id' in row_copy:
                    del row_copy['id']
                
                columns = list(row_copy.keys())
                values = []
                
                # Convertir les valeurs
                for col in columns:
                    value = row_copy[col]
                    if value is None:
                        values.append(None)
                    elif col in ['date_controle', 'date_creation']:
                        # Convertir la date ISO en format SQL Server
                        if isinstance(value, str) and 'T' in value:
                            date_part = value.split('T')[0]
                            values.append(date_part)
                        else:
                            values.append(value)
                    else:
                        values.append(value)
                
                placeholders = ', '.join(['?' for _ in columns])
                insert_sql = f"INSERT INTO CONTROLES_QUALITE ({', '.join(columns)}) VALUES ({placeholders})"
                cursor.execute(insert_sql, values)
                
                # Récupérer le nouvel ID
                cursor.execute("SELECT @@IDENTITY")
                new_id = cursor.fetchone()[0]
                
                if old_id:
                    id_mapping[old_id] = new_id
            
            print(f"  {len(data)} enregistrements restaurés")
            print(f"  Mapping des ID: {id_mapping}")
        
        # Restaurer les données TOLERANCES_CONTROLE
        if 'TOLERANCES_CONTROLE' in backup_data['tables']:
            print("Restauration des données TOLERANCES_CONTROLE...")
            data = backup_data['tables']['TOLERANCES_CONTROLE']['data']
            
            for row in data:
                # Exclure l'ID pour permettre la régénération automatique
                row_copy = row.copy()
                if 'id' in row_copy:
                    del row_copy['id']
                
                # Mettre à jour controle_id avec le nouvel ID
                old_controle_id = row_copy.get('controle_id')
                if old_controle_id and old_controle_id in id_mapping:
                    row_copy['controle_id'] = id_mapping[old_controle_id]
                
                columns = list(row_copy.keys())
                values = []
                
                # Convertir les valeurs
                for col in columns:
                    value = row_copy[col]
                    if value is None:
                        values.append(None)
                    else:
                        values.append(value)
                
                placeholders = ', '.join(['?' for _ in columns])
                insert_sql = f"INSERT INTO TOLERANCES_CONTROLE ({', '.join(columns)}) VALUES ({placeholders})"
                cursor.execute(insert_sql, values)
            
            print(f"  {len(data)} enregistrements restaurés")
        
        conn.commit()
        
        print("\n=== Vérification ===")
        
        # Vérifier les données restaurées
        cursor.execute("SELECT COUNT(*) FROM CONTROLES_QUALITE")
        count_cq = cursor.fetchone()[0]
        print(f"CONTROLES_QUALITE: {count_cq} enregistrements")
        
        cursor.execute("SELECT COUNT(*) FROM TOLERANCES_CONTROLE")
        count_tc = cursor.fetchone()[0]
        print(f"TOLERANCES_CONTROLE: {count_tc} enregistrements")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"Erreur lors de la restauration: {e}")
        return False

def update_db_config():
    """Met à jour le fichier db.py pour pointer vers la nouvelle base"""
    
    try:
        # Lire le fichier db.py
        with open('db.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Nouvelle configuration
        new_config = '''DB_CONFIG = {
    "DRIVER": "{SQL Server}",
    "SERVER": "LAPTOP-LATIFA",
    "DATABASE": "novaprint_restored",
    "Trusted_Connection": "yes",
    "TrustServerCertificate": "yes"
}'''
        
        # Remplacer l'ancienne configuration
        import re
        pattern = r'DB_CONFIG = \{[^}]+\}'
        new_content = re.sub(pattern, new_config, content, flags=re.DOTALL)
        
        # Sauvegarder
        with open('db.py', 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("Configuration db.py mise à jour vers: novaprint_restored")
        return True
        
    except Exception as e:
        print(f"Erreur lors de la mise à jour de db.py: {e}")
        return False

if __name__ == "__main__":
    print("=== Restauration des tables de contrôle qualité ===")
    print("Base de données: novaprint_restored")
    print()
    
    # Étape 1: Créer les tables et restaurer les données
    success = restore_qualite_tables()
    
    if success:
        print("\n=== Mise à jour de la configuration ===")
        # Étape 2: Mettre à jour db.py
        update_db_config()
        
        print("\n=== Migration terminée avec succès! ===")
        print("La base novaprint_restored est maintenant prête")
        print("Les tables de contrôle qualité ont été préservées")
        print("La configuration db.py a été mise à jour")
        print("\nVous pouvez maintenant tester l'application")
    else:
        print("\nErreur lors de la migration")
