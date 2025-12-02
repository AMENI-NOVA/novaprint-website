"""
Projet 14 - Registre de suivi des déchets
Gestion des déchets collectés
"""
from flask import Blueprint
from db import get_db_cursor

projet14_bp = Blueprint('projet14', __name__, url_prefix='/projet14')

def get_all_dechets():
    """Récupère tous les enregistrements de déchets"""
    with get_db_cursor() as cursor:
        cursor.execute("""
            SELECT 
                ID,
                Date,
                Type,
                Quantite,
                Unite,
                Bon_Reception_Num,
                Receptionnaire,
                Date_Creation,
                MONTH(Date) as MoisNum
            FROM WEB_Suivi_Dechets
            ORDER BY Date DESC, ID DESC
        """)
        
        dechets = []
        for row in cursor.fetchall():
            # Gérer la date qui peut être un objet date ou une chaîne
            if row.Date:
                if isinstance(row.Date, str):
                    date_str = row.Date.split('T')[0] if 'T' in row.Date else row.Date
                else:
                    date_str = row.Date.strftime('%Y-%m-%d')
            else:
                date_str = None
            
            # Gérer date_creation
            if row.Date_Creation:
                if isinstance(row.Date_Creation, str):
                    date_creation_str = row.Date_Creation
                else:
                    date_creation_str = row.Date_Creation.strftime('%Y-%m-%d %H:%M:%S')
            else:
                date_creation_str = None
            
            dechets.append({
                "id": row.ID,
                "date": date_str,
                "type": row.Type,
                "quantite": float(row.Quantite) if row.Quantite else 0,
                "unite": row.Unite,
                "bon_reception_num": row.Bon_Reception_Num,
                "receptionnaire": row.Receptionnaire,
                "date_creation": date_creation_str,
                "mois_num": row.MoisNum
            })
        return dechets

def get_dechet_by_id(dechet_id):
    """Récupère un enregistrement de déchet par son ID"""
    with get_db_cursor() as cursor:
        cursor.execute("""
            SELECT 
                ID,
                Date,
                Type,
                Quantite,
                Unite,
                Bon_Reception_Num,
                Receptionnaire,
                Date_Creation
            FROM WEB_Suivi_Dechets
            WHERE ID = ?
        """, (dechet_id,))
        
        row = cursor.fetchone()
        if row:
            # Gérer la date qui peut être un objet date ou une chaîne
            if row.Date:
                if isinstance(row.Date, str):
                    date_str = row.Date.split('T')[0] if 'T' in row.Date else row.Date
                else:
                    date_str = row.Date.strftime('%Y-%m-%d')
            else:
                date_str = None
            
            # Gérer date_creation
            if row.Date_Creation:
                if isinstance(row.Date_Creation, str):
                    date_creation_str = row.Date_Creation
                else:
                    date_creation_str = row.Date_Creation.strftime('%Y-%m-%d %H:%M:%S')
            else:
                date_creation_str = None
            
            return {
                "id": row.ID,
                "date": date_str,
                "type": row.Type,
                "quantite": float(row.Quantite) if row.Quantite else 0,
                "unite": row.Unite,
                "bon_reception_num": row.Bon_Reception_Num,
                "receptionnaire": row.Receptionnaire,
                "date_creation": date_creation_str
            }
        return None

def create_dechet(data):
    """Crée un nouvel enregistrement de déchet"""
    try:
        with get_db_cursor() as cursor:
            cursor.execute("""
                INSERT INTO WEB_Suivi_Dechets (
                    Date, Type, Quantite, Unite, Bon_Reception_Num, Receptionnaire
                )
                OUTPUT INSERTED.ID
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                data.get('date'),
                data.get('type'),
                data.get('quantite'),
                data.get('unite', 'kg'),
                data.get('bon_reception_num'),
                data.get('receptionnaire')
            ))
            
            dechet_id = cursor.fetchone()[0]
            cursor.commit()
            return dechet_id
    except Exception as e:
        print(f"Erreur lors de la création du déchet: {e}")
        import traceback
        traceback.print_exc()
        return None

def update_dechet(dechet_id, data):
    """Met à jour un enregistrement de déchet"""
    try:
        with get_db_cursor() as cursor:
            cursor.execute("""
                UPDATE WEB_Suivi_Dechets
                SET Date = ?,
                    Type = ?,
                    Quantite = ?,
                    Unite = ?,
                    Bon_Reception_Num = ?,
                    Receptionnaire = ?
                WHERE ID = ?
            """, (
                data.get('date'),
                data.get('type'),
                data.get('quantite'),
                data.get('unite', 'kg'),
                data.get('bon_reception_num'),
                data.get('receptionnaire'),
                dechet_id
            ))
            
            cursor.connection.commit()
            return True
    except Exception as e:
        print(f"Erreur lors de la mise à jour du déchet: {e}")
        import traceback
        traceback.print_exc()
        return False

def delete_dechet(dechet_id):
    """Supprime un enregistrement de déchet"""
    try:
        with get_db_cursor() as cursor:
            cursor.execute("DELETE FROM WEB_Suivi_Dechets WHERE ID = ?", (dechet_id,))
            cursor.connection.commit()
            return True
    except Exception as e:
        print(f"Erreur lors de la suppression du déchet: {e}")
        return False

def get_types_predefined():
    """Retourne les types de déchets prédéfinis"""
    return [
        "Papier Offset",
        "Carton blanc gris",
        "Carton blanc bois",
        "Eaux polluées"
    ]

def get_statistiques_dechets(annee=None):
    """Calcule les statistiques globales des déchets
    
    Args:
        annee (str, optional): Année pour filtrer les statistiques (format: '2025')
    """
    with get_db_cursor() as cursor:
        # Clause WHERE pour le filtre d'année
        where_clause = f"WHERE YEAR(Date) = {annee}" if annee else ""
        # Total par type (normalisation pour éviter les doublons de casse)
        # On regroupe UNIQUEMENT par type, sans tenir compte de l'unité pour éviter les doublons
        cursor.execute(f"""
            SELECT 
                -- Normaliser le type : majuscule initiale, reste en minuscules
                UPPER(LEFT(LTRIM(Type), 1)) + LOWER(SUBSTRING(LTRIM(Type), 2, LEN(LTRIM(Type)))) as Type_Normalise,
                SUM(Quantite) as Total_Quantite,
                'kg' as Unite,  -- Unité par défaut pour l'affichage
                COUNT(*) as Nombre_Enregistrements
            FROM WEB_Suivi_Dechets
            {where_clause}
            GROUP BY UPPER(LEFT(LTRIM(Type), 1)) + LOWER(SUBSTRING(LTRIM(Type), 2, LEN(LTRIM(Type))))
            ORDER BY Total_Quantite DESC
        """)
        
        stats_par_type = []
        for row in cursor.fetchall():
            stats_par_type.append({
                "type": row.Type_Normalise,
                "total_quantite": float(row.Total_Quantite) if row.Total_Quantite else 0,
                "unite": row.Unite,
                "nombre_enregistrements": row.Nombre_Enregistrements
            })
        
        # Total global - séparé par unité (kg et m³)
        cursor.execute(f"""
            SELECT 
                COUNT(*) as Total_Enregistrements,
                SUM(CASE WHEN LOWER(Unite) IN ('kg', 'kilogramme', 'kilogrammes') THEN Quantite ELSE 0 END) as Total_Quantite_Kg,
                SUM(CASE WHEN LOWER(Unite) IN ('m³', 'm3', 'mètre cube', 'mètres cubes') THEN Quantite ELSE 0 END) as Total_Quantite_M3,
                SUM(CASE WHEN LOWER(Unite) NOT IN ('kg', 'kilogramme', 'kilogrammes', 'm³', 'm3', 'mètre cube', 'mètres cubes') THEN Quantite ELSE 0 END) as Total_Quantite_Autre
            FROM WEB_Suivi_Dechets
            {where_clause}
        """)
        
        row = cursor.fetchone()
        total_enregistrements = row.Total_Enregistrements or 0
        total_quantite_kg = float(row.Total_Quantite_Kg) if row.Total_Quantite_Kg else 0
        total_quantite_m3 = float(row.Total_Quantite_M3) if row.Total_Quantite_M3 else 0
        total_quantite_autre = float(row.Total_Quantite_Autre) if row.Total_Quantite_Autre else 0
        
        # Total par mois - UNIQUEMENT pour les déchets solides (kg)
        # Exclusion des déchets liquides (m³) pour éviter l'addition de quantités incompatibles
        # Si une année est spécifiée, afficher tous les mois de cette année
        # Sinon, afficher les 12 derniers mois
        if annee:
            where_mois = f"WHERE YEAR(Date) = {annee} AND LOWER(Unite) IN ('kg', 'kilogramme', 'kilogrammes')"
        else:
            where_mois = "WHERE Date >= DATEADD(MONTH, -12, GETDATE()) AND LOWER(Unite) IN ('kg', 'kilogramme', 'kilogrammes')"
            
        cursor.execute(f"""
            SELECT 
                FORMAT(Date, 'yyyy-MM') as Mois,
                SUM(Quantite) as Total_Quantite_Kg,
                COUNT(*) as Nombre_Enregistrements
            FROM WEB_Suivi_Dechets
            {where_mois}
            GROUP BY FORMAT(Date, 'yyyy-MM')
            ORDER BY FORMAT(Date, 'yyyy-MM')
        """)
        
        stats_par_mois = []
        for row in cursor.fetchall():
            stats_par_mois.append({
                "mois": row.Mois,
                "total_quantite_kg": float(row.Total_Quantite_Kg) if row.Total_Quantite_Kg else 0,
                "nombre_enregistrements": row.Nombre_Enregistrements
            })
        
        return {
            "total_enregistrements": total_enregistrements,
            "total_quantite_kg": total_quantite_kg,
            "total_quantite_m3": total_quantite_m3,
            "total_quantite_autre": total_quantite_autre,
            "stats_par_type": stats_par_type,
            "stats_par_mois": stats_par_mois
        }

def get_dechets_par_mois(annee, mois):
    """Récupère les déchets pour un mois donné"""
    with get_db_cursor() as cursor:
        cursor.execute("""
            SELECT 
                ID,
                Date,
                Type,
                Quantite,
                Unite,
                Bon_Reception_Num,
                Receptionnaire,
                Date_Creation
            FROM WEB_Suivi_Dechets
            WHERE YEAR(Date) = ? AND MONTH(Date) = ?
            ORDER BY Date DESC, ID DESC
        """, (annee, mois))
        
        dechets = []
        for row in cursor.fetchall():
            # Gérer la date qui peut être un objet date ou une chaîne
            if row.Date:
                if isinstance(row.Date, str):
                    date_str = row.Date.split('T')[0] if 'T' in row.Date else row.Date
                else:
                    date_str = row.Date.strftime('%Y-%m-%d')
            else:
                date_str = None
            
            # Gérer date_creation
            if row.Date_Creation:
                if isinstance(row.Date_Creation, str):
                    date_creation_str = row.Date_Creation
                else:
                    date_creation_str = row.Date_Creation.strftime('%Y-%m-%d %H:%M:%S')
            else:
                date_creation_str = None
            
            dechets.append({
                "id": row.ID,
                "date": date_str,
                "type": row.Type,
                "quantite": float(row.Quantite) if row.Quantite else 0,
                "unite": row.Unite,
                "bon_reception_num": row.Bon_Reception_Num,
                "receptionnaire": row.Receptionnaire,
                "date_creation": date_creation_str
            })
        return dechets


