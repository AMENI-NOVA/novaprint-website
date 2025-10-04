#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pyodbc

def check_bak_file_contents():
    """Vérifie le contenu du fichier .BAK pour identifier les noms de fichiers logiques"""
    
    bak_file_path = r"C:\Apps\newbd"
    
    try:
        # Connexion au serveur SQL
        master_conn_string = f"DRIVER={{SQL Server}};SERVER=LAPTOP-LATIFA;DATABASE=master;Trusted_Connection=yes;TrustServerCertificate=yes"
        conn = pyodbc.connect(master_conn_string, autocommit=True)
        cursor = conn.cursor()
        
        print(f"Vérification du contenu du fichier: {bak_file_path}")
        print("=" * 60)
        
        # Obtenir la liste des fichiers dans le backup
        filelist_sql = f"RESTORE FILELISTONLY FROM DISK = '{bak_file_path}'"
        cursor.execute(filelist_sql)
        
        print("Fichiers logiques trouvés:")
        print("-" * 60)
        
        rows = cursor.fetchall()
        for i, row in enumerate(rows):
            print(f"Ligne {i+1}:")
            for j, col in enumerate(row):
                print(f"  Colonne {j}: {col}")
            print()
        
        print("-" * 60)
        
        # Obtenir les informations du backup
        header_sql = f"RESTORE HEADERONLY FROM DISK = '{bak_file_path}'"
        cursor.execute(header_sql)
        
        print("\nInformations du backup:")
        print("-" * 60)
        
        for row in cursor.fetchall():
            print(f"Nom de la base: {row[2]}")
            print(f"Date de backup: {row[3]}")
            print(f"Type de backup: {row[4]}")
            print(f"Taille: {row[6] / 1024 / 1024:.2f} MB")
            break
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"Erreur: {e}")
        return False

if __name__ == "__main__":
    check_bak_file_contents()
