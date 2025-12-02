"""
Projet 15 - Analyse de la corrélation entre les déchets et le chiffre d'affaires
"""
import math
from db import get_db_cursor

def get_all_correlations(annee=None):
    """Récupère toutes les données de corrélation déchets/CA (2025+)"""
    with get_db_cursor() as cursor:
        if annee:
            where_clause = f"WHERE Annee = {annee}"
        else:
            where_clause = "WHERE Annee >= 2025"
        
        cursor.execute(f"""
            SELECT 
                ID,
                Annee,
                Mois,
                Date_WEB_Suivi_Dechets,
                Quantite_WEB_Suivi_Dechets,
                Unite_WEB_Suivi_Dechets,
                DteFact_FACTURES,
                TotalHTPce_FACTURES,
                Date_Creation,
                Date_Modification
            FROM WEB_Coor_CH_dech
            {where_clause}
            ORDER BY Annee DESC, Mois DESC
        """)
        
        correlations = []
        for row in cursor.fetchall():
            # Gérer les dates qui peuvent être des objets date ou des chaînes
            if row.Date_WEB_Suivi_Dechets:
                if isinstance(row.Date_WEB_Suivi_Dechets, str):
                    date_dechets = row.Date_WEB_Suivi_Dechets.split('T')[0] if 'T' in row.Date_WEB_Suivi_Dechets else row.Date_WEB_Suivi_Dechets
                else:
                    date_dechets = row.Date_WEB_Suivi_Dechets.strftime('%Y-%m-%d')
            else:
                date_dechets = None
            
            if row.DteFact_FACTURES:
                if isinstance(row.DteFact_FACTURES, str):
                    date_factures = row.DteFact_FACTURES.split('T')[0] if 'T' in row.DteFact_FACTURES else row.DteFact_FACTURES
                else:
                    date_factures = row.DteFact_FACTURES.strftime('%Y-%m-%d')
            else:
                date_factures = None
            
            if row.Date_Creation:
                if isinstance(row.Date_Creation, str):
                    date_creation = row.Date_Creation
                else:
                    date_creation = row.Date_Creation.strftime('%Y-%m-%d %H:%M:%S')
            else:
                date_creation = None
            
            if row.Date_Modification:
                if isinstance(row.Date_Modification, str):
                    date_modification = row.Date_Modification
                else:
                    date_modification = row.Date_Modification.strftime('%Y-%m-%d %H:%M:%S')
            else:
                date_modification = None
            
            correlations.append({
                "id": row.ID,
                "annee": row.Annee,
                "mois": row.Mois,
                "date_dechets": date_dechets,
                "quantite_dechets": float(row.Quantite_WEB_Suivi_Dechets) if row.Quantite_WEB_Suivi_Dechets else 0,
                "unite_dechets": row.Unite_WEB_Suivi_Dechets,
                "date_factures": date_factures,
                "total_ca": float(row.TotalHTPce_FACTURES) if row.TotalHTPce_FACTURES else 0,
                "date_creation": date_creation,
                "date_modification": date_modification
            })
        
        return correlations

def get_correlation_by_id(corr_id):
    """Récupère une corrélation par son ID"""
    with get_db_cursor() as cursor:
        cursor.execute("""
            SELECT 
                ID,
                Annee,
                Mois,
                Date_WEB_Suivi_Dechets,
                Quantite_WEB_Suivi_Dechets,
                Unite_WEB_Suivi_Dechets,
                DteFact_FACTURES,
                TotalHTPce_FACTURES,
                Date_Creation,
                Date_Modification
            FROM WEB_Coor_CH_dech
            WHERE ID = ?
        """, (corr_id,))
        
        row = cursor.fetchone()
        if row:
            # Gérer les dates qui peuvent être des objets date ou des chaînes
            if row.Date_WEB_Suivi_Dechets:
                if isinstance(row.Date_WEB_Suivi_Dechets, str):
                    date_dechets = row.Date_WEB_Suivi_Dechets.split('T')[0] if 'T' in row.Date_WEB_Suivi_Dechets else row.Date_WEB_Suivi_Dechets
                else:
                    date_dechets = row.Date_WEB_Suivi_Dechets.strftime('%Y-%m-%d')
            else:
                date_dechets = None
            
            if row.DteFact_FACTURES:
                if isinstance(row.DteFact_FACTURES, str):
                    date_factures = row.DteFact_FACTURES.split('T')[0] if 'T' in row.DteFact_FACTURES else row.DteFact_FACTURES
                else:
                    date_factures = row.DteFact_FACTURES.strftime('%Y-%m-%d')
            else:
                date_factures = None
            
            if row.Date_Creation:
                if isinstance(row.Date_Creation, str):
                    date_creation = row.Date_Creation
                else:
                    date_creation = row.Date_Creation.strftime('%Y-%m-%d %H:%M:%S')
            else:
                date_creation = None
            
            if row.Date_Modification:
                if isinstance(row.Date_Modification, str):
                    date_modification = row.Date_Modification
                else:
                    date_modification = row.Date_Modification.strftime('%Y-%m-%d %H:%M:%S')
            else:
                date_modification = None
            
            return {
                "id": row.ID,
                "annee": row.Annee,
                "mois": row.Mois,
                "date_dechets": date_dechets,
                "quantite_dechets": float(row.Quantite_WEB_Suivi_Dechets) if row.Quantite_WEB_Suivi_Dechets else 0,
                "unite_dechets": row.Unite_WEB_Suivi_Dechets,
                "date_factures": date_factures,
                "total_ca": float(row.TotalHTPce_FACTURES) if row.TotalHTPce_FACTURES else 0,
                "date_creation": date_creation,
                "date_modification": date_modification
            }
        return None

def update_correlation(corr_id, data):
    """Met à jour une corrélation (uniquement dans WEB_Coor_CH_dech)"""
    try:
        with get_db_cursor() as cursor:
            cursor.execute("""
                UPDATE WEB_Coor_CH_dech
                SET Quantite_WEB_Suivi_Dechets = ?,
                    TotalHTPce_FACTURES = ?,
                    Date_Modification = GETDATE()
                WHERE ID = ?
            """, (
                data.get('quantite_dechets'),
                data.get('total_ca'),
                corr_id
            ))
            
            cursor.connection.commit()
            return True
    except Exception as e:
        print(f"Erreur lors de la mise à jour : {e}")
        import traceback
        traceback.print_exc()
        return False

def calculer_coefficient_correlation(donnees):
    """Calcule le coefficient de corrélation de Pearson entre déchets et CA."""
    # Filtrer les points valides (au moins un CA non nul pour éviter division par zéro)
    points = [
        (d["quantite_dechets"], d["total_ca"])
        for d in donnees
        if d["quantite_dechets"] is not None and d["total_ca"] is not None
    ]
    
    n = len(points)
    if n < 2:
        return None
    
    sum_x = sum(p[0] for p in points)
    sum_y = sum(p[1] for p in points)
    sum_x2 = sum(p[0] ** 2 for p in points)
    sum_y2 = sum(p[1] ** 2 for p in points)
    sum_xy = sum(p[0] * p[1] for p in points)
    
    numerator = n * sum_xy - sum_x * sum_y
    denominator_part_x = n * sum_x2 - sum_x ** 2
    denominator_part_y = n * sum_y2 - sum_y ** 2
    
    if denominator_part_x <= 0 or denominator_part_y <= 0:
        return None
    
    denominator = math.sqrt(denominator_part_x * denominator_part_y)
    if denominator == 0:
        return None
    
    return numerator / denominator


def get_statistiques_correlation(annee=None):
    """Calcule les statistiques de corrélation (2025+)"""
    with get_db_cursor() as cursor:
        if annee:
            where_clause = f"WHERE Annee = {annee}"
        else:
            where_clause = "WHERE Annee >= 2025"
        
        # Données pour le graphique comparatif
        cursor.execute(f"""
            SELECT 
                Annee,
                Mois,
                FORMAT(Date_WEB_Suivi_Dechets, 'yyyy-MM') AS Periode,
                Quantite_WEB_Suivi_Dechets,
                TotalHTPce_FACTURES
            FROM WEB_Coor_CH_dech
            {where_clause}
            ORDER BY Annee, Mois
        """)
        
        donnees_graphique = []
        for row in cursor.fetchall():
            quantite_dechets = float(row.Quantite_WEB_Suivi_Dechets) if row.Quantite_WEB_Suivi_Dechets else 0
            total_ca = float(row.TotalHTPce_FACTURES) if row.TotalHTPce_FACTURES else 0
            ratio_dechets_ca = (quantite_dechets / total_ca * 100) if total_ca else 0
            kg_dechets_par_100k_ca = (quantite_dechets / total_ca * 100000) if total_ca else 0
            donnees_graphique.append({
                "annee": row.Annee,
                "mois": row.Mois,
                "periode": row.Periode,
                "quantite_dechets": quantite_dechets,
                "total_ca": total_ca,
                "ratio_dechets_ca": ratio_dechets_ca,
                "kg_dechets_par_100k_ca": kg_dechets_par_100k_ca
            })
        
        # Statistiques globales
        cursor.execute(f"""
            SELECT 
                COUNT(*) AS Nb_Mois,
                SUM(Quantite_WEB_Suivi_Dechets) AS Total_Dechets,
                AVG(Quantite_WEB_Suivi_Dechets) AS Moyenne_Dechets,
                SUM(TotalHTPce_FACTURES) AS Total_CA,
                AVG(TotalHTPce_FACTURES) AS Moyenne_CA,
                MIN(Annee) AS Annee_Min,
                MAX(Annee) AS Annee_Max
            FROM WEB_Coor_CH_dech
            {where_clause}
        """)
        
        row = cursor.fetchone()
        coefficient_correlation = calculer_coefficient_correlation(donnees_graphique)
        
        stats_globales = {
            "nb_mois": row.Nb_Mois or 0,
            "total_dechets": float(row.Total_Dechets) if row.Total_Dechets else 0,
            "moyenne_dechets": float(row.Moyenne_Dechets) if row.Moyenne_Dechets else 0,
            "total_ca": float(row.Total_CA) if row.Total_CA else 0,
            "moyenne_ca": float(row.Moyenne_CA) if row.Moyenne_CA else 0,
            "annee_min": row.Annee_Min,
            "annee_max": row.Annee_Max,
            "coefficient_correlation": coefficient_correlation
        }
        
        return {
            "donnees_graphique": donnees_graphique,
            "stats_globales": stats_globales
        }

def get_annees_disponibles():
    """Récupère la liste des années disponibles (2025+)"""
    with get_db_cursor() as cursor:
        cursor.execute("""
            SELECT DISTINCT Annee
            FROM WEB_Coor_CH_dech
            WHERE Annee >= 2025
            ORDER BY Annee DESC
        """)
        
        return [row.Annee for row in cursor.fetchall()]

def get_correlation_par_type(annee=None):
    """Récupère les données de corrélation agrégées par type de déchet (2025+)"""
    with get_db_cursor() as cursor:
        if annee:
            where_clause = f"AND YEAR(D.Date) = {annee}"
        else:
            where_clause = "AND YEAR(D.Date) >= 2025"
        
        # Récupérer les données mensuelles par type de déchet
        cursor.execute(f"""
            WITH Dechets_Par_Type AS (
                SELECT 
                    YEAR(Date) AS Annee,
                    MONTH(Date) AS Mois,
                    FORMAT(Date, 'yyyy-MM') AS Periode,
                    UPPER(LEFT(LTRIM(Type), 1)) + LOWER(SUBSTRING(LTRIM(Type), 2, LEN(LTRIM(Type)))) AS Type_Normalise,
                    SUM(CASE WHEN LOWER(Unite) IN ('kg', 'kilogramme', 'kilogrammes') 
                        THEN Quantite ELSE 0 END) AS Total_Kg
                FROM WEB_Suivi_Dechets D
                WHERE 1=1 {where_clause}
                GROUP BY YEAR(Date), MONTH(Date), FORMAT(Date, 'yyyy-MM'), 
                         UPPER(LEFT(LTRIM(Type), 1)) + LOWER(SUBSTRING(LTRIM(Type), 2, LEN(LTRIM(Type))))
            ),
            CA_Mensuel AS (
                SELECT 
                    YEAR(DteFact) AS Annee,
                    MONTH(DteFact) AS Mois,
                    FORMAT(DteFact, 'yyyy-MM') AS Periode,
                    SUM(TotalHTPce) AS Total_CA_HT
                FROM FACTURES
                WHERE DteFact IS NOT NULL AND YEAR(DteFact) >= 2025
                {where_clause.replace('D.Date', 'DteFact') if where_clause else ''}
                GROUP BY YEAR(DteFact), MONTH(DteFact), FORMAT(DteFact, 'yyyy-MM')
            )
            SELECT 
                D.Annee,
                D.Mois,
                D.Periode,
                D.Type_Normalise,
                D.Total_Kg,
                COALESCE(C.Total_CA_HT, 0) AS Total_CA_HT
            FROM Dechets_Par_Type D
            LEFT JOIN CA_Mensuel C
                ON D.Annee = C.Annee AND D.Mois = C.Mois
            ORDER BY D.Type_Normalise, D.Annee, D.Mois
        """)
        
        # Organiser les données par type
        donnees_par_type = {}
        for row in cursor.fetchall():
            type_dechet = row.Type_Normalise
            
            if type_dechet not in donnees_par_type:
                donnees_par_type[type_dechet] = []
            
            donnees_par_type[type_dechet].append({
                "annee": row.Annee,
                "mois": row.Mois,
                "periode": row.Periode,
                "quantite_kg": float(row.Total_Kg) if row.Total_Kg else 0,
                "total_ca": float(row.Total_CA_HT) if row.Total_CA_HT else 0
            })
        
        return donnees_par_type

def get_types_dechets_disponibles():
    """Récupère la liste des types de déchets disponibles (2025+)"""
    with get_db_cursor() as cursor:
        cursor.execute("""
            SELECT DISTINCT 
                UPPER(LEFT(LTRIM(Type), 1)) + LOWER(SUBSTRING(LTRIM(Type), 2, LEN(LTRIM(Type)))) AS Type_Normalise
            FROM WEB_Suivi_Dechets
            WHERE LOWER(Unite) IN ('kg', 'kilogramme', 'kilogrammes')
                AND YEAR(Date) >= 2025
            ORDER BY Type_Normalise
        """)
        
        return [row.Type_Normalise for row in cursor.fetchall()]

