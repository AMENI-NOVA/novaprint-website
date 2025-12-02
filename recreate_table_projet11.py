#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pyodbc
import os

def recreate_web_traitements_table():
    """Recrée la table WEB_TRAITEMENTS avec la structure simplifiée (sans ID de liaison)"""
    
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
        print("RECRÉATION DE LA TABLE WEB_TRAITEMENTS - VERSION SIMPLIFIÉE")
        print("="*70)
        print("\n⚠️  IMPORTANT: Cette version ne stocke QUE les données métier")
        print("   Les ID de liaison ne sont plus stockés dans la table")
        print("   Seul ID_FICHE_TRAVAIL est conservé comme clé de liaison\n")
        
        # Lire le fichier SQL v2
        sql_file = 'create_web_traitements_v2.sql'
        if not os.path.exists(sql_file):
            print(f"ERREUR: Le fichier {sql_file} n'existe pas")
            return False
        
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # Découper le fichier SQL en commandes individuelles
        sql_commands = []
        current_command = []
        
        for line in sql_content.split('\n'):
            stripped = line.strip()
            if stripped.startswith('--') and not any(char.isalnum() for char in line[:line.index('--')] if '--' in line):
                continue
            
            if stripped.upper() == 'GO':
                if current_command:
                    sql_commands.append('\n'.join(current_command))
                    current_command = []
            else:
                current_command.append(line)
        
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
                
                while cursor.nextset():
                    pass
                    
            except Exception as e:
                print(f"ERREUR lors de l'exécution de la commande {i}: {e}")
                print(f"Commande: {cmd[:100]}...")
        
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
            print("\n✓ Table WEB_TRAITEMENTS recréée avec succès!")
            
            # Afficher la structure de la table
            print("\nStructure de la table WEB_TRAITEMENTS (VERSION SIMPLIFIÉE):")
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
            
            print("\n📊 CHAMPS DE LA TABLE:")
            print("-" * 70)
            
            field_count = 0
            for col in cursor.fetchall():
                col_name = col[0]
                data_type = col[1]
                max_length = col[2]
                nullable = "NULL" if col[3] == "YES" else "NOT NULL"
                
                type_str = data_type
                if max_length:
                    type_str += f"({max_length})"
                
                # Identifier le type de champ
                if col_name == 'ID':
                    prefix = "🔑 [ID Principal]      "
                elif col_name == 'ID_FICHE_TRAVAIL':
                    prefix = "🔗 [Clé de Liaison]    "
                elif col_name in ['DteDeb', 'DteFin', 'NbOp', 'NbPers']:
                    prefix = "✏️  [Champ Web]         "
                elif col_name in ['DateCreation', 'DateModification']:
                    prefix = "📅 [Métadonnée]        "
                else:
                    prefix = "📦 [Donnée Métier]     "
                
                print(f"{prefix}{col_name:<40} {type_str:<20} {nullable}")
                field_count += 1
            
            print("-" * 70)
            print(f"Total: {field_count} champs")
            
            # Compter les champs par catégorie
            cursor.execute("""
                SELECT COUNT(*) 
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_NAME = 'WEB_TRAITEMENTS'
                AND COLUMN_NAME IN ('DteDeb', 'DteFin', 'NbOp', 'NbPers')
            """)
            web_fields = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT COUNT(*) 
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_NAME = 'WEB_TRAITEMENTS'
                AND COLUMN_NAME LIKE '%\_%'
                AND COLUMN_NAME NOT IN ('ID_FICHE_TRAVAIL', 'DateCreation', 'DateModification')
            """)
            metier_fields = cursor.fetchone()[0]
            
            print(f"\n📈 RÉPARTITION:")
            print(f"  - 1 clé principale (ID)")
            print(f"  - 1 clé de liaison (ID_FICHE_TRAVAIL)")
            print(f"  - {web_fields} champs web (DteDeb, DteFin, NbOp, NbPers)")
            print(f"  - {metier_fields} champs métier (données importées)")
            print(f"  - 2 métadonnées (DateCreation, DateModification)")
            
            # Afficher les clés étrangères
            print("\n" + "-" * 70)
            print("🔗 CLÉS ÉTRANGÈRES:")
            print("-" * 70)
            cursor.execute("""
                SELECT 
                    fk.name AS ForeignKey,
                    cp.name AS Column,
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
            """)
            
            fk_count = 0
            for fk in cursor.fetchall():
                print(f"  ✓ {fk[0]}")
                print(f"    WEB_TRAITEMENTS.{fk[1]} → {fk[2]}.{fk[3]}")
                fk_count += 1
            
            if fk_count == 0:
                print("  (Aucune clé étrangère)")
            
            print("\n" + "="*70)
            print("✅ MODIFICATION TERMINÉE AVEC SUCCÈS")
            print("="*70)
            print("\n💡 RAPPEL:")
            print("  - Seules les DONNÉES MÉTIER sont stockées")
            print("  - Les ID de liaison ne sont PAS stockés")
            print("  - Les jointures se font via ID_FICHE_TRAVAIL")
            print("  - Les autres données sont récupérées par jointure SQL\n")
            
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
    recreate_web_traitements_table()


