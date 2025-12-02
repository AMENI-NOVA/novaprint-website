#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pyodbc
import os

def create_web_traitements_table():
    """Crée la table WEB_TRAITEMENTS dans la base novaprint_restored"""
    
    try:
        # Connexion à la base de données
        conn = pyodbc.connect(
            'DRIVER={SQL Server};'
            'SERVER=LAPTOP-LATIFA;'
            'DATABASE=novaprint_restored;'
            'Trusted_Connection=yes;'
            'TrustServerCertificate=yes'
        )
        cursor = conn.cursor()
        
        print("="*70)
        print("CRÉATION DE LA TABLE WEB_TRAITEMENTS - PROJET 11")
        print("="*70)
        
        # Lire le fichier SQL
        sql_file = 'create_web_traitements.sql'
        if not os.path.exists(sql_file):
            print(f"ERREUR: Le fichier {sql_file} n'existe pas")
            return False
        
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # Découper le fichier SQL en commandes individuelles
        # En utilisant GO comme séparateur
        sql_commands = []
        current_command = []
        
        for line in sql_content.split('\n'):
            # Ignorer les lignes de commentaires pures
            stripped = line.strip()
            if stripped.startswith('--') and not any(char.isalnum() for char in line[:line.index('--')]):
                continue
            
            # Si on trouve GO, exécuter la commande accumulée
            if stripped.upper() == 'GO':
                if current_command:
                    sql_commands.append('\n'.join(current_command))
                    current_command = []
            else:
                current_command.append(line)
        
        # Ajouter la dernière commande si elle existe
        if current_command:
            sql_commands.append('\n'.join(current_command))
        
        # Exécuter chaque commande
        executed = 0
        for i, cmd in enumerate(sql_commands, 1):
            cmd = cmd.strip()
            if not cmd or cmd.startswith('USE '):
                continue
            
            try:
                print(f"\n[{i}/{len(sql_commands)}] Exécution de la commande...")
                cursor.execute(cmd)
                conn.commit()
                executed += 1
                
                # Afficher les messages SQL Server
                while cursor.nextset():
                    pass
                    
            except Exception as e:
                print(f"ERREUR lors de l'exécution de la commande {i}: {e}")
                print(f"Commande: {cmd[:100]}...")
                # Continuer avec les autres commandes
        
        print(f"\n{'='*70}")
        print(f"✓ {executed} commandes SQL exécutées avec succès")
        print(f"{'='*70}")
        
        # Vérifier que la table a été créée
        cursor.execute("""
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_NAME = 'WEB_TRAITEMENTS'
        """)
        
        if cursor.fetchone()[0] > 0:
            print("\n✓ Table WEB_TRAITEMENTS créée avec succès!")
            
            # Afficher la structure de la table
            print("\nStructure de la table WEB_TRAITEMENTS:")
            print("-" * 70)
            cursor.execute("""
                SELECT 
                    COLUMN_NAME,
                    DATA_TYPE,
                    CHARACTER_MAXIMUM_LENGTH,
                    IS_NULLABLE
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_NAME = 'WEB_TRAITEMENTS'
                ORDER BY ORDINAL_POSITION
            """)
            
            for col in cursor.fetchall():
                col_name = col[0]
                data_type = col[1]
                max_length = col[2]
                nullable = "NULL" if col[3] == "YES" else "NOT NULL"
                
                type_str = data_type
                if max_length:
                    type_str += f"({max_length})"
                
                print(f"  {col_name:<40} {type_str:<20} {nullable}")
            
            # Afficher les clés étrangères
            print("\n" + "-" * 70)
            print("Clés étrangères:")
            print("-" * 70)
            cursor.execute("""
                SELECT 
                    fk.name AS ForeignKey,
                    tp.name AS ParentTable,
                    cp.name AS ParentColumn,
                    tr.name AS ReferencedTable,
                    cr.name AS ReferencedColumn
                FROM sys.foreign_keys AS fk
                INNER JOIN sys.foreign_key_columns AS fkc 
                    ON fk.object_id = fkc.constraint_object_id
                INNER JOIN sys.tables AS tp 
                    ON fkc.parent_object_id = tp.object_id
                INNER JOIN sys.columns AS cp 
                    ON fkc.parent_object_id = cp.object_id 
                    AND fkc.parent_column_id = cp.column_id
                INNER JOIN sys.tables AS tr 
                    ON fkc.referenced_object_id = tr.object_id
                INNER JOIN sys.columns AS cr 
                    ON fkc.referenced_object_id = cr.object_id 
                    AND fkc.referenced_column_id = cr.column_id
                WHERE tp.name = 'WEB_TRAITEMENTS'
                ORDER BY fk.name
            """)
            
            for fk in cursor.fetchall():
                print(f"  {fk[0]}")
                print(f"    {fk[1]}.{fk[2]} -> {fk[3]}.{fk[4]}")
            
            print("\n" + "="*70)
            print("✓ CRÉATION DE LA TABLE TERMINÉE AVEC SUCCÈS")
            print("="*70)
            
        else:
            print("\n✗ ERREUR: La table WEB_TRAITEMENTS n'a pas été créée")
            return False
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"\n✗ ERREUR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    create_web_traitements_table()


