#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pyodbc
import os

def restore_with_move():
    """Restauration avec MOVE vers des chemins différents"""
    
    bak_file_path = r"C:\Apps\newbd"
    new_database_name = "novaprint_restored"
    
    try:
        # Connexion au serveur SQL
        master_conn_string = f"DRIVER={{SQL Server}};SERVER=LAPTOP-LATIFA;DATABASE=master;Trusted_Connection=yes;TrustServerCertificate=yes"
        conn = pyodbc.connect(master_conn_string, autocommit=True)
        cursor = conn.cursor()
        
        print(f"Restauration de {bak_file_path} vers {new_database_name}")
        
        # Vérifier si la base existe déjà
        cursor.execute(f"SELECT name FROM sys.databases WHERE name = '{new_database_name}'")
        if cursor.fetchone():
            print(f"Suppression de la base existante {new_database_name}...")
            cursor.execute(f"DROP DATABASE [{new_database_name}]")
        
        # Définir les chemins de destination
        data_file_path = f"C:\\Program Files\\Microsoft SQL Server\\MSSQL16.GRAPHISOFT\\MSSQL\\DATA\\{new_database_name}.mdf"
        log_file_path = f"C:\\Program Files\\Microsoft SQL Server\\MSSQL16.GRAPHISOFT\\MSSQL\\DATA\\{new_database_name}_log.ldf"
        
        # Vérifier que les répertoires existent
        data_dir = os.path.dirname(data_file_path)
        if not os.path.exists(data_dir):
            print(f"Erreur: Répertoire {data_dir} n'existe pas")
            return False
        
        print(f"Fichier de données: {data_file_path}")
        print(f"Fichier de log: {log_file_path}")
        
        # Restauration avec MOVE
        restore_sql = f"""
        RESTORE DATABASE [{new_database_name}]
        FROM DISK = '{bak_file_path}'
        WITH 
            MOVE 'NOVAPRINT11' TO '{data_file_path}',
            MOVE 'NOVAPRINT11_log' TO '{log_file_path}',
            REPLACE
        """
        
        print("Exécution de la restauration...")
        cursor.execute(restore_sql)
        
        print(f"Base de données {new_database_name} restaurée avec succès")
        
        # Vérifier que la base existe
        cursor.execute(f"SELECT name FROM sys.databases WHERE name = '{new_database_name}'")
        if cursor.fetchone():
            print("Vérification: Base restaurée avec succès")
            
            # Lister quelques tables pour vérifier
            cursor.execute(f"USE [{new_database_name}]")
            cursor.execute("SELECT TOP 5 TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'")
            tables = cursor.fetchall()
            print("Tables trouvées:")
            for table in tables:
                print(f"  - {table[0]}")
        else:
            print("Erreur: Base non trouvée après restauration")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"Erreur lors de la restauration: {e}")
        return False

if __name__ == "__main__":
    restore_with_move()
