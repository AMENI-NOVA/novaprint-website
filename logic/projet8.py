# C:\Apps\logic\projet8.py

from flask import Blueprint, render_template
from db import get_db_cursor

bp = Blueprint('projet8', __name__, url_prefix='/projet8')

@bp.route('/')
def stats_devis_commandes():
    with get_db_cursor() as cursor:
        cursor.execute("""
            SELECT 
                CAT.Categorie,
                COUNT(DISTINCT D.ID) AS NbDevis,
                COUNT(DISTINCT CM.ID) AS NbCommandes,
                SUM(D.MontantHT) AS TotalDevis,
                SUM(CM.MontantHT) AS TotalCommandes,
                CASE WHEN COUNT(D.ID) > 0 THEN 
                    ROUND(CAST(COUNT(CM.ID) AS FLOAT) / COUNT(D.ID) * 100, 2)
                ELSE 0 END AS TauxTransformation
            FROM 
                DEVIS D
            LEFT JOIN 
                COMMANDES CM ON D.ID = CM.ID_DEVIS
            LEFT JOIN 
                CATEGORIES_SOCIETES CAT ON D.ID_CATEGORIE = CAT.ID
            GROUP BY 
                CAT.Categorie
            ORDER BY 
                CAT.Categorie
        """)
        stats = cursor.fetchall()

    return render_template('projet8.html', stats=stats)
