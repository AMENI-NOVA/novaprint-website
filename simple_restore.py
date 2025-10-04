#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pyodbc

def simple_restore():
    """Restauration simple du fichier .BAK"""
    
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
        
        # Restauration simple sans MOVE
        restore_sql = f"""
        RESTORE DATABASE [{new_database_name}]
        FROM DISK = '{bak_file_path}'
        WITH REPLACE
        """
        
        print("Exécution de la restauration...")
        cursor.execute(restore_sql)
        
        print(f"Base de données {new_database_name} restaurée avec succès")
        
        # Vérifier que la base existe
        cursor.execute(f"SELECT name FROM sys.databases WHERE name = '{new_database_name}'")
        if cursor.fetchone():
            print("Vérification: Base restaurée avec succès")
        else:
            print("Erreur: Base non trouvée après restauration")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"Erreur lors de la restauration: {e}")
        return False

if __name__ == "__main__":
    simple_restore()
