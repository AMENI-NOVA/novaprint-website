#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pyodbc
import json
from datetime import datetime

def backup_qualite_tables():
    """Sauvegarde les tables de contrôle qualité vers un fichier JSON"""
    
    # Configuration de la base actuelle
    db_config = {
        "DRIVER": "{SQL Server}",
        "SERVER": "LAPTOP-LATIFA",
        "DATABASE": "novaprint",
        "Trusted_Connection": "yes",
        "TrustServerCertificate": "yes"
    }
    
    try:
        connection_string = f"DRIVER={db_config['DRIVER']};SERVER={db_config['SERVER']};DATABASE={db_config['DATABASE']};Trusted_Connection={db_config['Trusted_Connection']};TrustServerCertificate={db_config['TrustServerCertificate']}"
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        
        backup_data = {
            "timestamp": datetime.now().isoformat(),
            "tables": {}
        }
        
        # Vérifier si les tables existent
        cursor.execute("""
            SELECT TABLE_NAME 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_NAME IN ('CONTROLES_QUALITE', 'TOLERANCES_CONTROLE')
        """)
        existing_tables = [row[0] for row in cursor.fetchall()]
        
        if not existing_tables:
            print("Aucune table de contrôle qualité trouvée")
            return None
        
        print(f"Tables trouvées: {existing_tables}")
        
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
            
            # Convertir les données en format JSON-serializable
            data = []
            for row in rows:
                row_dict = {}
                for i, value in enumerate(row):
                    if value is None:
                        row_dict[columns[i]] = None
                    elif isinstance(value, datetime):
                        row_dict[columns[i]] = value.isoformat()
                    else:
                        row_dict[columns[i]] = str(value)
                data.append(row_dict)
            
            backup_data["tables"]["CONTROLES_QUALITE"] = {
                "columns": columns,
                "data": data
            }
            print(f"  {len(data)} enregistrements sauvegardés")
        
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
            
            # Convertir les données en format JSON-serializable
            data = []
            for row in rows:
                row_dict = {}
                for i, value in enumerate(row):
                    if value is None:
                        row_dict[columns[i]] = None
                    elif isinstance(value, datetime):
                        row_dict[columns[i]] = value.isoformat()
                    else:
                        row_dict[columns[i]] = str(value)
                data.append(row_dict)
            
            backup_data["tables"]["TOLERANCES_CONTROLE"] = {
                "columns": columns,
                "data": data
            }
            print(f"  {len(data)} enregistrements sauvegardés")
        
        conn.close()
        
        # Sauvegarder vers fichier JSON
        backup_filename = f"backup_qualite_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(backup_filename, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, indent=2, ensure_ascii=False)
        
        print(f"Sauvegarde terminée: {backup_filename}")
        return backup_filename
        
    except Exception as e:
        print(f"Erreur lors de la sauvegarde: {e}")
        return None

if __name__ == "__main__":
    print("=== Sauvegarde des tables de contrôle qualité ===")
    print()
    
    backup_file = backup_qualite_tables()
    
    if backup_file:
        print(f"\nSauvegarde réussie: {backup_file}")
        print("Vous pouvez maintenant restaurer la base via SSMS")
        print("Nom de la base à créer: novaprint_restored")
    else:
        print("\nErreur lors de la sauvegarde")
