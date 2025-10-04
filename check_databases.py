#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pyodbc

def check_databases():
    """Vérifie les bases de données existantes"""
    
    try:
        # Connexion au serveur SQL
        master_conn_string = f"DRIVER={{SQL Server}};SERVER=LAPTOP-LATIFA;DATABASE=master;Trusted_Connection=yes;TrustServerCertificate=yes"
        conn = pyodbc.connect(master_conn_string, autocommit=True)
        cursor = conn.cursor()
        
        print("Bases de données existantes:")
        print("=" * 40)
        
        cursor.execute("SELECT name FROM sys.databases ORDER BY name")
        databases = cursor.fetchall()
        
        for db in databases:
            print(f"- {db[0]}")
        
        print("=" * 40)
        
        # Vérifier spécifiquement novaprint_restored
        cursor.execute("SELECT name FROM sys.databases WHERE name = 'novaprint_restored'")
        if cursor.fetchone():
            print("La base 'novaprint_restored' existe déjà")
        else:
            print("La base 'novaprint_restored' n'existe pas")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"Erreur: {e}")
        return False

if __name__ == "__main__":
    check_databases()
