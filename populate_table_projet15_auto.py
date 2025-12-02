"""
Script de population automatique de la table WEB_Coor_CH_dech (sans interaction)
"""
import pyodbc
from contextlib import contextmanager

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

def populate_data():
    print("=" * 80)
    print("POPULATION AUTOMATIQUE - TABLE WEB_Coor_CH_dech")
    print("=" * 80)
    print()
    
    try:
        with get_db_cursor() as cursor:
            # Vérifier si la table existe
            cursor.execute("SELECT OBJECT_ID(N'WEB_Coor_CH_dech', 'U')")
            if cursor.fetchone()[0] is None:
                print("[ERREUR] La table WEB_Coor_CH_dech n'existe pas.")
                return False
            
            # Vider la table automatiquement
            cursor.execute("SELECT COUNT(*) FROM WEB_Coor_CH_dech")
            count = cursor.fetchone()[0]
            if count > 0:
                print(f"[INFO] La table contient {count} enregistrement(s). Vidage...")
                cursor.execute("DELETE FROM WEB_Coor_CH_dech")
                cursor.connection.commit()
                print("[OK] Table videe.")
            
            print("\n[TRAITEMENT] Agregation des donnees...")
            print("-" * 80)
            
            # Agrégation (uniquement données 2025+)
            cursor.execute("""
                WITH Dechets_Mensuels AS (
                    SELECT 
                        YEAR(Date) AS Annee,
                        MONTH(Date) AS Mois,
                        DATEFROMPARTS(YEAR(Date), MONTH(Date), 1) AS Date_Mois,
                        SUM(CASE WHEN LOWER(Unite) IN ('kg', 'kilogramme', 'kilogrammes') 
                            THEN Quantite ELSE 0 END) AS Total_Kg
                    FROM WEB_Suivi_Dechets
                    WHERE YEAR(Date) >= 2025
                    GROUP BY YEAR(Date), MONTH(Date)
                ),
                CA_Mensuel AS (
                    SELECT 
                        YEAR(DteFact) AS Annee,
                        MONTH(DteFact) AS Mois,
                        DATEFROMPARTS(YEAR(DteFact), MONTH(DteFact), 1) AS Date_Mois,
                        SUM(TotalHTPce) AS Total_CA_HT
                    FROM FACTURES
                    WHERE DteFact IS NOT NULL AND YEAR(DteFact) >= 2025
                    GROUP BY YEAR(DteFact), MONTH(DteFact)
                )
                SELECT 
                    COALESCE(D.Annee, C.Annee) AS Annee,
                    COALESCE(D.Mois, C.Mois) AS Mois,
                    COALESCE(D.Date_Mois, C.Date_Mois) AS Date_Mois_Dechets,
                    COALESCE(D.Total_Kg, 0) AS Total_Dechets_Kg,
                    COALESCE(C.Date_Mois, D.Date_Mois) AS Date_Mois_CA,
                    COALESCE(C.Total_CA_HT, 0) AS Total_CA_HT
                FROM Dechets_Mensuels D
                FULL OUTER JOIN CA_Mensuel C
                    ON D.Annee = C.Annee AND D.Mois = C.Mois
                ORDER BY COALESCE(D.Annee, C.Annee), COALESCE(D.Mois, C.Mois)
            """)
            
            rows = cursor.fetchall()
            inserted = 0
            
            for row in rows:
                annee = row.Annee
                mois = row.Mois
                date_dechets = row.Date_Mois_Dechets
                total_dechets = float(row.Total_Dechets_Kg) if row.Total_Dechets_Kg else 0
                date_ca = row.Date_Mois_CA
                total_ca = float(row.Total_CA_HT) if row.Total_CA_HT else 0
                
                cursor.execute("""
                    INSERT INTO WEB_Coor_CH_dech (
                        Annee, Mois,
                        Date_WEB_Suivi_Dechets, Quantite_WEB_Suivi_Dechets, Unite_WEB_Suivi_Dechets,
                        DteFact_FACTURES, TotalHTPce_FACTURES
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (annee, mois, date_dechets, total_dechets, 'kg', date_ca, total_ca))
                
                inserted += 1
                if inserted % 5 == 0:
                    print(f"[PROGRESS] {inserted} enregistrements inseres...")
            
            cursor.connection.commit()
            
            print("-" * 80)
            print(f"\n[SUCCESS] {inserted} enregistrement(s) insere(s) !")
            
            # Statistiques
            cursor.execute("""
                SELECT 
                    COUNT(*) AS Total_Mois,
                    SUM(Quantite_WEB_Suivi_Dechets) AS Total_Dechets,
                    SUM(TotalHTPce_FACTURES) AS Total_CA,
                    MIN(Annee) AS Annee_Min,
                    MAX(Annee) AS Annee_Max
                FROM WEB_Coor_CH_dech
            """)
            
            stats = cursor.fetchone()
            print("\n[STATS] Statistiques globales :")
            print(f"   Periode : {stats.Annee_Min} - {stats.Annee_Max}")
            print(f"   Nombre de mois : {stats.Total_Mois}")
            print(f"   Total dechets : {stats.Total_Dechets:.2f} kg")
            print(f"   Total CA HT : {stats.Total_CA:.2f} euros")
            
            return True
            
    except Exception as e:
        print(f"\n[ERREUR] Erreur : {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = populate_data()
    print("\n" + "=" * 80)
    if success:
        print("Operation terminee avec succes !")
    else:
        print("Operation echouee.")
    print("=" * 80)

