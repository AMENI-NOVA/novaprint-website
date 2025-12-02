import pyodbc
import pandas as pd
from datetime import datetime
from contextlib import contextmanager

# Configuration de la base de données
DB_CONFIG = {
    "DRIVER": "{SQL Server}",
    "SERVER": "LAPTOP-LATIFA",
    "DATABASE": "novaprint_restored",
    "Trusted_Connection": "yes",
    "TrustServerCertificate": "yes"
}

def get_connection_string():
    return ";".join(f"{k}={v}" for k, v in DB_CONFIG.items())

@contextmanager
def get_db_cursor():
    conn = pyodbc.connect(get_connection_string())
    cursor = conn.cursor()
    try:
        yield cursor
    finally:
        cursor.close()
        conn.close()

def convert_date(date_str):
    """Convertit une date du format DD/MM/YYYY au format YYYY-MM-DD"""
    try:
        # Si c'est déjà un objet datetime de pandas
        if isinstance(date_str, pd.Timestamp):
            return date_str.strftime('%Y-%m-%d')
        
        # Si c'est une chaîne de caractères
        if isinstance(date_str, str):
            # Format DD/MM/YYYY
            if '/' in date_str:
                day, month, year = date_str.split('/')
                return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
            # Format DD-MM-YYYY
            elif '-' in date_str and len(date_str.split('-')[2]) == 4:
                day, month, year = date_str.split('-')
                return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
        
        return str(date_str)
    except Exception as e:
        print(f"⚠️ Erreur conversion date '{date_str}': {e}")
        return None

def check_duplicate(cursor, date, type_dechet, quantite):
    """Vérifie si un enregistrement existe déjà (date + type + quantité)"""
    query = """
        SELECT COUNT(*) 
        FROM WEB_Suivi_Dechets 
        WHERE Date = ? AND Type = ? AND Quantite = ?
    """
    cursor.execute(query, (date, type_dechet, quantite))
    count = cursor.fetchone()[0]
    return count > 0

def import_excel_to_database(excel_file_path):
    """Importe les données du fichier Excel dans la base de données"""
    
    print("=" * 80)
    print("IMPORT DES DONNÉES EXCEL VERS WEB_Suivi_Dechets")
    print("=" * 80)
    print()
    
    # 1. Lecture du fichier Excel
    print("📂 Lecture du fichier Excel...")
    try:
        df = pd.read_excel(excel_file_path)
        print(f"✅ Fichier lu avec succès : {len(df)} lignes trouvées")
        print(f"📋 Colonnes détectées : {list(df.columns)}")
    except Exception as e:
        print(f"❌ Erreur lors de la lecture du fichier : {e}")
        return
    
    print()
    
    # 2. Nettoyage des espaces dans les noms de colonnes
    print("🧹 Nettoyage des espaces dans les noms de colonnes...")
    df.columns = df.columns.str.strip()
    print(f"✅ Colonnes nettoyées : {list(df.columns)}")
    print()
    
    # 3. Mapping des colonnes
    print("🔄 Mapping des colonnes...")
    column_mapping = {
        'Date': 'Date',
        'Type de déchet': 'Type',
        'Quantité': 'Quantite',
        'Unité': 'Unite',
        'Bon de réception N°': 'Bon_Reception_Num',
        'Bon de récéption N°': 'Bon_Reception_Num',  # Variante orthographique
        'Réceptionnaire': 'Receptionnaire',
        'Récéptionnaire': 'Receptionnaire'  # Variante orthographique
    }
    
    # Renommer les colonnes
    df = df.rename(columns=column_mapping)
    print(f"✅ Colonnes après mapping : {list(df.columns)}")
    print()
    
    # 4. Validation des colonnes requises
    required_columns = ['Date', 'Type', 'Quantite', 'Unite']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        print(f"❌ Colonnes manquantes : {missing_columns}")
        return
    
    # 5. Conversion des dates et filtrage 2025
    print("📅 Conversion des dates et filtrage année 2025...")
    df['Date_Converted'] = df['Date'].apply(convert_date)
    
    # Filtrer uniquement l'année 2025
    df['Year'] = pd.to_datetime(df['Date_Converted'], errors='coerce').dt.year
    df_2025 = df[df['Year'] == 2025].copy()
    
    print(f"✅ {len(df_2025)} enregistrements de l'année 2025 à importer")
    print()
    
    # 6. Import dans la base de données
    print("💾 Import dans la base de données...")
    
    with get_db_cursor() as cursor:
        inserted = 0
        duplicates = 0
        errors = 0
        
        for index, row in df_2025.iterrows():
            try:
                date_converted = row['Date_Converted']
                type_dechet = str(row['Type']).strip() if pd.notna(row['Type']) else ''
                quantite = float(row['Quantite']) if pd.notna(row['Quantite']) else 0
                unite = str(row['Unite']).strip() if pd.notna(row['Unite']) else 'kg'
                bon_reception = str(row['Bon_Reception_Num']) if pd.notna(row.get('Bon_Reception_Num')) else None
                receptionnaire = str(row['Receptionnaire']).strip() if pd.notna(row.get('Receptionnaire')) else None
                
                # Vérifier les doublons
                if check_duplicate(cursor, date_converted, type_dechet, quantite):
                    duplicates += 1
                    print(f"⏭️  Ligne {index + 1} : Doublon ignoré ({date_converted} - {type_dechet} - {quantite})")
                    continue
                
                # Insérer l'enregistrement
                insert_query = """
                    INSERT INTO WEB_Suivi_Dechets 
                    (Date, Type, Quantite, Unite, Bon_Reception_Num, Receptionnaire)
                    VALUES (?, ?, ?, ?, ?, ?)
                """
                
                cursor.execute(insert_query, (
                    date_converted,
                    type_dechet,
                    quantite,
                    unite,
                    bon_reception,
                    receptionnaire
                ))
                
                inserted += 1
                
                # Afficher la progression tous les 10 enregistrements
                if inserted % 10 == 0:
                    print(f"✅ {inserted} enregistrements insérés...")
                
            except Exception as e:
                errors += 1
                print(f"❌ Erreur ligne {index + 1} : {e}")
                continue
        
        # Commit des changements
        cursor.connection.commit()
    
    print()
    print("=" * 80)
    print("📊 RÉSUMÉ DE L'IMPORT")
    print("=" * 80)
    print(f"✅ Enregistrements insérés : {inserted}")
    print(f"⏭️  Doublons ignorés : {duplicates}")
    print(f"❌ Erreurs : {errors}")
    print(f"📁 Total traité : {len(df_2025)}")
    print("=" * 80)
    print()
    
    if inserted > 0:
        print("🎉 Import terminé avec succès !")
        print("💡 Vous pouvez maintenant utiliser l'interface web du Projet 14.")
    else:
        print("⚠️ Aucun enregistrement n'a été inséré.")

if __name__ == "__main__":
    print()
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "IMPORT DONNÉES EXCEL - PROJET 14" + " " * 26 + "║")
    print("╚" + "=" * 78 + "╝")
    print()
    
    # Demander le chemin du fichier Excel
    excel_file = input("📂 Entrez le chemin du fichier Excel (ou appuyez sur Entrée pour 'dechets_2025.xlsx') : ").strip()
    
    if not excel_file:
        excel_file = "dechets_2025.xlsx"
    
    print()
    
    # Vérifier l'existence du fichier
    import os
    if not os.path.exists(excel_file):
        print(f"❌ Fichier introuvable : {excel_file}")
        print("💡 Assurez-vous que le fichier se trouve dans le même dossier que ce script.")
    else:
        import_excel_to_database(excel_file)
    
    print()
    input("Appuyez sur Entrée pour quitter...")


