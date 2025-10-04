import pyodbc
from datetime import datetime
from contextlib import contextmanager

# ---------------------------
# CONFIGURATION SQL SERVER
# ---------------------------
DB_CONFIG = {
    "DRIVER": "{SQL Server}",
    "SERVER": "LAPTOP-LATIFA",
    "DATABASE": "novaprint_restored",
    "Trusted_Connection": "yes",
    "TrustServerCertificate": "yes"
}
def init_projet6_tables():
    conn, cur = get_db_cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS VOYAGES (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            DateVoyage DATE NOT NULL,
            Destination TEXT,
            Camion TEXT,
            Chauffeur TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS VOYAGE_LIGNES (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            ID_VOYAGE INTEGER,
            Client TEXT,
            NumDossier TEXT,
            Quantite INTEGER,
            NbCarton INTEGER,
            NbPalette INTEGER,
            Termine BOOLEAN,
            FOREIGN KEY (ID_VOYAGE) REFERENCES VOYAGES(ID)
        )
    """)
    conn.commit()

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

# ---------------------------
# PROJET 1 – PLANNING & SUIVI DES DÉLAIS
# ---------------------------
def get_commandes():
    commandes = []
    with get_db_cursor() as cursor:
        cursor.execute("""
            SELECT C.Numero, C.DteLivPrev, C.Reference, S.RaiSocTri AS Client
            FROM COMMANDES C
            LEFT JOIN SOCIETES S ON C.ID_SOCIETE = S.ID
            WHERE C.Termine = 0 AND C.EtatLiv = 0
        """)
        for row in cursor.fetchall():
            if row.DteLivPrev:  # Vérifier que la date n'est pas nulle
                commandes.append({
                    "id": row.Numero,
                    "title": row.Numero,
                    "start": row.DteLivPrev.strftime('%Y-%m-%d'),
                    "reference": row.Reference,
                    "client": row.Client
                })
    return commandes

def update_commande(numero, new_date, user=None):
    try:
        new_date_obj = datetime.strptime(new_date, '%Y-%m-%d')
        with get_db_cursor() as cursor:
            cursor.execute("SELECT DteLivPrev FROM COMMANDES WHERE Numero = ?", numero)
            row = cursor.fetchone()
            if not row:
                return False
            old_date = row.DteLivPrev
            cursor.execute("""
                UPDATE COMMANDES 
                SET DteLivPrev = ? 
                WHERE Numero = ?
            """, new_date_obj, numero)
            if user:
                cursor.execute("""
                    INSERT INTO HISTORIQUE_LIVRAISON 
                    (NumeroCommande, AncienneDate, NouvelleDate, ModifiePar)
                    VALUES (?, ?, ?, ?)
                """, numero, old_date, new_date_obj, user)
            cursor.connection.commit()
            return True
    except Exception as e:
        print(f"[Erreur MAJ planning] {e}")
        return False

def get_historique_commande(numero):
    with get_db_cursor() as cursor:
        cursor.execute("""
            SELECT AncienneDate, NouvelleDate, ModifiePar, DateModification
            FROM HISTORIQUE_LIVRAISON
            WHERE NumeroCommande = ?
            ORDER BY DateModification DESC
        """, numero)
        rows = cursor.fetchall()
        return [
            {
                "ancienne": row.AncienneDate.strftime('%Y-%m-%d'),
                "nouvelle": row.NouvelleDate.strftime('%Y-%m-%d'),
                "user": row.ModifiePar,
                "modifie_le": row.DateModification.strftime('%Y-%m-%d %H:%M')
            }
            for row in rows
        ]

# ---------------------------
# SUIVI DES DÉLAIS ET PONCTUALITÉ
# ---------------------------
def get_commandes_avec_suivi():
    """Récupère les commandes avec informations de suivi des délais"""
    commandes = []
    with get_db_cursor() as cursor:
        cursor.execute("""
            SELECT 
                C.Numero, 
                C.DteLivPrev, 
                L.DteLiv AS DteLivReelle,
                C.Reference, 
                S.RaiSocTri AS Client,
                C.Termine,
                C.EtatLiv,
                CASE 
                    WHEN L.DteLiv IS NOT NULL AND L.DteLiv <> '9999-12-31 00:00:00.000' AND L.DteLiv > '1900-01-01' AND L.DteLiv < '2100-01-01' THEN
                        CASE 
                            WHEN L.DteLiv > C.DteLivPrev THEN 'Livré en Retard'
                            WHEN L.DteLiv <= C.DteLivPrev THEN 'Livré à Temps'
                            ELSE 'Non Défini'
                        END
                    WHEN C.DteLivPrev < GETDATE() THEN 'En Retard'
                    ELSE 'En Cours'
                END AS StatutDelai,
                CASE 
                    WHEN L.DteLiv IS NOT NULL AND L.DteLiv <> '9999-12-31 00:00:00.000' AND L.DteLiv > '1900-01-01' AND L.DteLiv < '2100-01-01' THEN
                        DATEDIFF(day, C.DteLivPrev, L.DteLiv)
                    WHEN C.DteLivPrev < GETDATE() THEN
                        DATEDIFF(day, C.DteLivPrev, GETDATE())
                    ELSE 0
                END AS EcartJours
            FROM COMMANDES C
            INNER JOIN SOCIETES S ON C.ID_SOCIETE = S.ID
            LEFT JOIN LIVRAISONS_CMDE L ON C.ID = L.ID_COMMANDE 
            WHERE C.DteLivPrev IS NOT NULL 
            AND C.DteLivPrev <> '9999-12-31 00:00:00.000' 
            AND C.DteLivPrev > '1900-01-01'
            ORDER BY C.DteLivPrev DESC
        """)
        for row in cursor.fetchall():
            commandes.append({
                "numero": row.Numero,
                "date_prevue": row.DteLivPrev.strftime('%Y-%m-%d') if row.DteLivPrev else None,
                "date_reelle": row.DteLivReelle.strftime('%Y-%m-%d') if row.DteLivReelle else None,
                "reference": row.Reference,
                "client": row.Client,
                "termine": bool(row.Termine),
                "etat_liv": row.EtatLiv,
                "statut_delai": row.StatutDelai,
                "ecart_jours": row.EcartJours
            })
    return commandes

def get_statistiques_performance():
    """Calcule les statistiques de performance de livraison"""
    with get_db_cursor() as cursor:
        cursor.execute("""
            SELECT 
                COUNT(*) as total_commandes,
                SUM(CASE 
                    WHEN L.DteLiv IS NOT NULL AND L.DteLiv <> '9999-12-31 00:00:00.000' AND L.DteLiv > '1900-01-01' AND L.DteLiv < '2100-01-01' THEN 1 
                    ELSE 0 
                END) as commandes_livrees,
                SUM(CASE 
                    WHEN L.DteLiv IS NOT NULL AND L.DteLiv <> '9999-12-31 00:00:00.000' AND L.DteLiv > '1900-01-01' AND L.DteLiv < '2100-01-01' AND L.DteLiv <= C.DteLivPrev THEN 1 
                    ELSE 0 
                END) as livrees_a_temps,
                SUM(CASE 
                    WHEN L.DteLiv IS NOT NULL AND L.DteLiv <> '9999-12-31 00:00:00.000' AND L.DteLiv > '1900-01-01' AND L.DteLiv < '2100-01-01' AND L.DteLiv > C.DteLivPrev THEN 1 
                    ELSE 0 
                END) as livrees_en_retard,
                SUM(CASE 
                    WHEN (L.DteLiv IS NULL OR L.DteLiv = '9999-12-31 00:00:00.000' OR L.DteLiv <= '1900-01-01' OR L.DteLiv >= '2100-01-01') AND C.DteLivPrev < GETDATE() THEN 1 
                    ELSE 0 
                END) as en_retard,
                AVG(CASE 
                    WHEN L.DteLiv IS NOT NULL AND L.DteLiv <> '9999-12-31 00:00:00.000' AND L.DteLiv > '1900-01-01' AND L.DteLiv < '2100-01-01' THEN DATEDIFF(day, C.DteLivPrev, L.DteLiv) 
                    ELSE NULL 
                END) as delai_moyen,
                AVG(CASE 
                    WHEN L.DteLiv IS NOT NULL AND L.DteLiv <> '9999-12-31 00:00:00.000' AND L.DteLiv > '1900-01-01' AND L.DteLiv < '2100-01-01' AND L.DteLiv <= C.DteLivPrev THEN DATEDIFF(day, C.DteLivPrev, L.DteLiv) 
                    ELSE NULL 
                END) as delai_moyen_a_temps,
                AVG(CASE 
                    WHEN L.DteLiv IS NOT NULL AND L.DteLiv <> '9999-12-31 00:00:00.000' AND L.DteLiv > '1900-01-01' AND L.DteLiv < '2100-01-01' AND L.DteLiv > C.DteLivPrev THEN DATEDIFF(day, C.DteLivPrev, L.DteLiv) 
                    ELSE NULL 
                END) as retard_moyen
            FROM COMMANDES C
            LEFT JOIN LIVRAISONS_CMDE L ON C.ID = L.ID_COMMANDE 
            WHERE C.DteLivPrev IS NOT NULL 
            AND C.DteLivPrev <> '9999-12-31 00:00:00.000' 
            AND C.DteLivPrev > '1900-01-01'
        """)
        row = cursor.fetchone()
        if row:
            total = row.total_commandes or 0
            livrees = row.commandes_livrees or 0
            a_temps = row.livrees_a_temps or 0
            en_retard = row.livrees_en_retard or 0
            en_retard_actuel = row.en_retard or 0
            
            taux_ponctualite = (a_temps / livrees * 100) if livrees > 0 else 0
            taux_livraison = (livrees / total * 100) if total > 0 else 0
            
            return {
                "total_commandes": total,
                "commandes_livrees": livrees,
                "livrees_a_temps": a_temps,
                "livrees_en_retard": en_retard,
                "en_retard_actuel": en_retard_actuel,
                "taux_ponctualite": round(taux_ponctualite, 2),
                "taux_livraison": round(taux_livraison, 2),
                "delai_moyen": round(row.delai_moyen or 0, 2),
                "delai_moyen_a_temps": round(row.delai_moyen_a_temps or 0, 2),
                "retard_moyen": round(row.retard_moyen or 0, 2)
            }
    return {}

def get_performance_par_client():
    """Calcule la performance par client"""
    with get_db_cursor() as cursor:
        cursor.execute("""
            SELECT 
                S.RaiSocTri AS Client,
                COUNT(*) as total_commandes,
                SUM(CASE 
                    WHEN L.DteLiv IS NOT NULL AND L.DteLiv <> '9999-12-31 00:00:00.000' AND L.DteLiv > '1900-01-01' AND L.DteLiv < '2100-01-01' THEN 1 
                    ELSE 0 
                END) as commandes_livrees,
                SUM(CASE 
                    WHEN L.DteLiv IS NOT NULL AND L.DteLiv <> '9999-12-31 00:00:00.000' AND L.DteLiv > '1900-01-01' AND L.DteLiv < '2100-01-01' AND L.DteLiv <= C.DteLivPrev THEN 1 
                    ELSE 0 
                END) as livrees_a_temps,
                AVG(CASE 
                    WHEN L.DteLiv IS NOT NULL AND L.DteLiv <> '9999-12-31 00:00:00.000' AND L.DteLiv > '1900-01-01' AND L.DteLiv < '2100-01-01' THEN DATEDIFF(day, C.DteLivPrev, L.DteLiv) 
                    ELSE NULL 
                END) as delai_moyen
            FROM COMMANDES C
            INNER JOIN SOCIETES S ON C.ID_SOCIETE = S.ID
            LEFT JOIN LIVRAISONS_CMDE L ON C.ID = L.ID_COMMANDE 
            WHERE C.DteLivPrev IS NOT NULL 
            AND C.DteLivPrev <> '9999-12-31 00:00:00.000' 
            AND C.DteLivPrev > '1900-01-01'
            AND S.RaiSocTri IS NOT NULL
            GROUP BY S.RaiSocTri
            HAVING COUNT(*) >= 1
            ORDER BY COUNT(*) DESC
        """)
        clients = []
        for row in cursor.fetchall():
            total = row.total_commandes or 0
            livrees = row.commandes_livrees or 0
            a_temps = row.livrees_a_temps or 0
            taux_ponctualite = (a_temps / livrees * 100) if livrees > 0 else 0
            
            clients.append({
                "client": row.Client,
                "total_commandes": total,
                "commandes_livrees": livrees,
                "livrees_a_temps": a_temps,
                "taux_ponctualite": round(taux_ponctualite, 2),
                "delai_moyen": round(row.delai_moyen or 0, 2)
            })
        return clients

def get_alertes_retard():
    """Récupère les commandes en retard nécessitant une attention (sans date de livraison)"""
    with get_db_cursor() as cursor:
        cursor.execute("""
            SELECT 
                C.Numero,
                C.DteLivPrev,
                C.Reference,
                S.RaiSocTri AS Client,
                DATEDIFF(day, C.DteLivPrev, GETDATE()) as jours_retard
            FROM COMMANDES C
            INNER JOIN SOCIETES S ON C.ID_SOCIETE = S.ID
            LEFT JOIN LIVRAISONS_CMDE L ON C.ID = L.ID_COMMANDE 
            WHERE C.Termine = 0 
            AND C.DteLivPrev IS NOT NULL 
            AND C.DteLivPrev <> '9999-12-31 00:00:00.000' 
            AND C.DteLivPrev > '1900-01-01'
            AND C.DteLivPrev < GETDATE()
            AND L.DteLiv IS NULL
            ORDER BY C.DteLivPrev ASC
        """)
        alertes = []
        for row in cursor.fetchall():
            alertes.append({
                "numero": row.Numero,
                "date_prevue": row.DteLivPrev.strftime('%Y-%m-%d'),
                "reference": row.Reference,
                "client": row.Client,
                "jours_retard": row.jours_retard
            })
        return alertes


# ---------------------------
# PROJET 10 - CONTRÔLE QUALITÉ
# ---------------------------
def get_numeros_commandes_disponibles():
    """Récupère tous les numéros de commandes disponibles pour le contrôle qualité"""
    with get_db_cursor() as cursor:
        cursor.execute("""
            SELECT DISTINCT Numero
            FROM COMMANDES
            WHERE Numero IS NOT NULL 
            AND Numero <> ''
            ORDER BY Numero
        """)
        numeros = []
        for row in cursor.fetchall():
            numeros.append(row.Numero.strip())
        return numeros

# ---------------------------
# CONTRÔLE QUALITÉ
# ---------------------------
def get_controles_qualite():
    """Récupère tous les contrôles qualité"""
    with get_db_cursor() as cursor:
        cursor.execute("""
            SELECT 
                id,
                date_controle,
                numero_dossier,
                operateur,
                machine_impression,
                operateur_machine_impression,
                machine_decoupe,
                operateur_machine_decoupe,
                rebus,
                validation_chef,
                date_creation
            FROM CONTROLES_QUALITE
            ORDER BY date_controle DESC, date_creation DESC
        """)
        controles = []
        for row in cursor.fetchall():
            controles.append({
                "id": row.id,
                "date_controle": row.date_controle,
                "numero_dossier": row.numero_dossier,
                "operateur": row.operateur,
                "machine_impression": row.machine_impression,
                "operateur_machine_impression": row.operateur_machine_impression,
                "machine_decoupe": row.machine_decoupe,
                "operateur_machine_decoupe": row.operateur_machine_decoupe,
                "rebus": row.rebus,
                "validation_chef": row.validation_chef,
                "date_creation": row.date_creation
            })
        return controles

def get_controle_qualite_by_id(controle_id):
    """Récupère un contrôle qualité par ID avec ses tolérances"""
    with get_db_cursor() as cursor:
        cursor.execute("""
            SELECT 
                id,
                date_controle,
                numero_dossier,
                operateur,
                machine_impression,
                operateur_machine_impression,
                machine_decoupe,
                operateur_machine_decoupe,
                rebus,
                validation_chef,
                date_creation
            FROM CONTROLES_QUALITE
            WHERE id = ?
        """, (controle_id,))
        
        controle = cursor.fetchone()
        if not controle:
            return None
            
        # Récupérer les tolérances
        cursor.execute("""
            SELECT 
                tolerance,
                quantite_conforme,
                quantite_non_conforme
            FROM TOLERANCES_CONTROLE
            WHERE controle_id = ?
            ORDER BY id
        """, (controle_id,))
        
        tolérances = []
        for row in cursor.fetchall():
            tolérances.append({
                "tolerance": row.tolerance,
                "quantite_conforme": row.quantite_conforme,
                "quantite_non_conforme": row.quantite_non_conforme
            })
        
        return {
            "id": controle.id,
            "date_controle": controle.date_controle,
            "numero_dossier": controle.numero_dossier,
            "operateur": controle.operateur,
            "machine_impression": controle.machine_impression,
            "operateur_machine_impression": controle.operateur_machine_impression,
            "machine_decoupe": controle.machine_decoupe,
            "operateur_machine_decoupe": controle.operateur_machine_decoupe,
            "rebus": controle.rebus,
            "validation_chef": controle.validation_chef,
            "date_creation": controle.date_creation,
            "tolérances": tolérances
        }

def create_controle_qualite(data):
    """Crée un nouveau contrôle qualité"""
    try:
        with get_db_cursor() as cursor:
            # Insérer le contrôle qualité
            cursor.execute("""
                INSERT INTO CONTROLES_QUALITE (
                    date_controle, numero_dossier, operateur, machine_impression, operateur_machine_impression, 
                    machine_decoupe, operateur_machine_decoupe, rebus, validation_chef, date_creation
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, GETDATE())
            """, (
                data['date_controle'],
                data['numero_dossier'],
                data['operateur'],
                data.get('machine_impression', ''),
                data.get('operateur_machine_impression', ''),
                data.get('machine_decoupe', ''),
                data.get('operateur_machine_decoupe', ''),
                data.get('rebus', 0),
                data.get('validation_chef', ''),
            ))
            
            # Récupérer l'ID du contrôle créé
            cursor.execute("SELECT @@IDENTITY")
            controle_id = cursor.fetchone()[0]
            
            # Insérer les tolérances
            if 'tolérances' in data:
                for tolerance_data in data['tolérances']:
                    cursor.execute("""
                        INSERT INTO TOLERANCES_CONTROLE (
                            controle_id, tolerance, quantite_conforme, quantite_non_conforme
                        ) VALUES (?, ?, ?, ?)
                    """, (
                        controle_id,
                        tolerance_data['tolerance'],
                        tolerance_data['quantite_conforme'],
                        tolerance_data['quantite_non_conforme']
                    ))
            
            # Valider la transaction
            cursor.commit()
            return controle_id
    except Exception as e:
        print(f"Erreur lors de la création du contrôle qualité: {e}")
        return None

def update_controle_qualite(controle_id, data):
    """Met à jour un contrôle qualité"""
    try:
        with get_db_cursor() as cursor:
            # Mettre à jour le contrôle qualité
            cursor.execute("""
                UPDATE CONTROLES_QUALITE SET
                    date_controle = ?,
                    numero_dossier = ?,
                    operateur = ?,
                    machine_impression = ?,
                    operateur_machine_impression = ?,
                    machine_decoupe = ?,
                    operateur_machine_decoupe = ?,
                    rebus = ?,
                    validation_chef = ?
                WHERE id = ?
            """, (
                data['date_controle'],
                data['numero_dossier'],
                data['operateur'],
                data.get('machine_impression', ''),
                data.get('operateur_machine_impression', ''),
                data.get('machine_decoupe', ''),
                data.get('operateur_machine_decoupe', ''),
                data.get('rebus', 0),
                data.get('validation_chef', ''),
                controle_id
            ))
            
            # Supprimer les anciennes tolérances
            cursor.execute("DELETE FROM TOLERANCES_CONTROLE WHERE controle_id = ?", (controle_id,))
            
            # Insérer les nouvelles tolérances
            if 'tolérances' in data:
                for tolerance_data in data['tolérances']:
                    cursor.execute("""
                        INSERT INTO TOLERANCES_CONTROLE (
                            controle_id, tolerance, quantite_conforme, quantite_non_conforme
                        ) VALUES (?, ?, ?, ?)
                    """, (
                        controle_id,
                        tolerance_data['tolerance'],
                        tolerance_data['quantite_conforme'],
                        tolerance_data['quantite_non_conforme']
                    ))
            
            return True
    except Exception as e:
        print(f"Erreur lors de la mise à jour du contrôle qualité: {e}")
        return False

def get_statistiques_controle_qualite():
    """Récupère les statistiques de contrôle qualité"""
    with get_db_cursor() as cursor:
        cursor.execute("""
            SELECT 
                COUNT(*) as total_controles,
                COUNT(CASE WHEN validation_chef IS NOT NULL AND validation_chef != '' THEN 1 END) as controles_valides,
                AVG(CAST(rebus AS FLOAT)) as rebus_moyen,
                SUM(rebus) as total_rebus
            FROM CONTROLES_QUALITE
        """)
        
        row = cursor.fetchone()
        if row:
            return {
                "total_controles": row.total_controles or 0,
                "controles_valides": row.controles_valides or 0,
                "rebus_moyen": round(row.rebus_moyen or 0, 2),
                "total_rebus": row.total_rebus or 0
            }
        return {"total_controles": 0, "controles_valides": 0, "rebus_moyen": 0, "total_rebus": 0}

def marquer_livraison_reelle(numero, date_livraison, user=None):
    """Marque une commande comme livrée avec la date réelle"""
    try:
        date_obj = datetime.strptime(date_livraison, '%Y-%m-%d')
        with get_db_cursor() as cursor:
            # Mettre à jour la commande
            cursor.execute("""
                UPDATE COMMANDES 
                SET DteLivReelle = ?, Termine = 1, EtatLiv = 1
                WHERE Numero = ?
            """, date_obj, numero)
            
            # Enregistrer dans l'historique si un utilisateur est fourni
            if user:
                cursor.execute("""
                    INSERT INTO HISTORIQUE_LIVRAISON 
                    (NumeroCommande, AncienneDate, NouvelleDate, ModifiePar, TypeModification)
                    VALUES (?, NULL, ?, ?, 'Livraison Réelle')
                """, numero, date_obj, user)
            
            cursor.connection.commit()
            return True
    except Exception as e:
        print(f"[Erreur marquage livraison] {e}")
        return False

# ---------------------------
# PROJET 2 – COMMANDES EN COURS
# ---------------------------
def get_commandes_en_cours():
    with get_db_cursor() as cursor:
        cursor.execute("""
            SELECT 
                C.Numero, 
                S.RaiSocTri, 
                C.Reference, 
                C.PourcentageReceptElem, 
                C.EtatPrepress, 
                C.EtatImpression, 
                C.EtatFaconnage, 
                C.EtatLiv,
                CASE WHEN MVT.TypePiece = 'D' THEN 'OK' ELSE 'En Attente' END AS SortiePapier
            FROM COMMANDES C
            LEFT JOIN SOCIETES S ON C.ID_SOCIETE = S.ID
            LEFT JOIN GS_MVT_STOCKS MVT ON LTRIM(RTRIM(C.Numero)) = LTRIM(RTRIM(MVT.NumDossier))
            LEFT JOIN GS_STOCKS ST ON ST.ID = MVT.ID_STOCK
            LEFT JOIN GS_ARTICLES A ON A.ID = ST.ID
            LEFT JOIN GS_FAMILLES F ON F.ID = A.ID_FAMILLE
            LEFT JOIN GS_TYPES_ARTICLE T ON T.ID = F.ID_TYPE_ARTICLE
            WHERE C.Termine = 0 AND T.Code IN ('P','B','O','D','V')
            ORDER BY C.Numero DESC
        """)
        return cursor.fetchall()

# ---------------------------
# PROJET 3 – SUIVI BAT
# ---------------------------
def get_commandes_bat():
    with get_db_cursor() as cursor:
        cursor.execute("""
            SELECT 
                C.ID, 
                C.Numero, 
                S.RaiSocTri AS RaisonSociale, 
                C.DteBat, 
                C.DteReceptElem, 
                C.EtatPrepress, 
                C.PourcentageReceptElem, 
                C.EtatLiv
            FROM COMMANDES C
            LEFT JOIN SOCIETES S ON S.ID = C.ID_SOCIETE
            WHERE C.Termine = 0
        """)
        columns = [col[0] for col in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        return results

def update_date_bat(id_commande, date_bat):
    try:
        date_obj = datetime.strptime(date_bat, "%Y-%m-%d")
        with get_db_cursor() as cursor:
            cursor.execute("""
                UPDATE COMMANDES 
                SET DteBat = ?
                WHERE ID = ?
            """, date_obj, id_commande)
            cursor.connection.commit()
            return True
    except Exception as e:
        print(f"[Erreur MAJ DteBat] {e}")
        return False

def update_reception_elem(id_commande):
    try:
        today = datetime.now().date()
        with get_db_cursor() as cursor:
            cursor.execute("""
                UPDATE COMMANDES
                SET DteReceptElem = ?
                WHERE ID = ?
            """, today, id_commande)
            cursor.connection.commit()
            return True
    except Exception as e:
        print(f"[Erreur MAJ réception] {e}")
        return False

def envoyer_bat(id_commande):
    try:
        with get_db_cursor() as cursor:
            cursor.execute("""
                UPDATE COMMANDES
                SET EtatPrepress = 1
                WHERE ID = ?
            """, id_commande)
            cursor.connection.commit()
            return True
    except Exception as e:
        print(f"[Erreur envoi BAT] {e}")
        return False

def get_contact_principal(id_societe):
    with get_db_cursor() as cursor:
        cursor.execute("""
            SELECT 
                P.ID AS ID_PERSONNE,
                P.Nom,
                P.Prenom,
                P.Telephone,
                P.Mobile,
                M.Mail,
                FCT.Fonction
            FROM SOCIETES_PERSONNES SP
            INNER JOIN PERSONNES P ON P.ID = SP.ID_PERSONNE
            LEFT JOIN (
                SELECT ID_PERSONNE, Mail
                FROM PERSONNES_MAIL
                WHERE ParDefaut = 1
            ) M ON M.ID_PERSONNE = P.ID
            LEFT JOIN (
                SELECT PF.ID_PERSONNE, FO.Nom AS Fonction, 
                       ROW_NUMBER() OVER (PARTITION BY PF.ID_PERSONNE ORDER BY PF.Ordre ASC) AS rn
                FROM PERSONNES_FONCTIONS PF
                INNER JOIN FONCTIONS FO ON FO.ID = PF.ID_FONCTION
            ) FCT ON FCT.ID_PERSONNE = P.ID AND FCT.rn = 1
            WHERE SP.ID_SOCIETE = ? AND SP.Principal = 1
        """, id_societe)

        row = cursor.fetchone()
        if row:
            return {
                "nom": row.Nom,
                "prenom": row.Prenom,
                "telephone": row.Telephone or row.Mobile,
                "email": row.Mail,
                "fonction": row.Fonction
            }
    return None

# ---------------------------
# PROJET 4 – CRM – Création Prospect + Contact
# ---------------------------
def creer_prospect(raison_sociale, ville=None, pays=None, telephone=None, email=None, id_categorie=None):
    with get_db_cursor() as cursor:
        # 1. Insertion dans SOCIETES avec ID_CATEGORIE en plus
        cursor.execute("""
            INSERT INTO SOCIETES (
                ID_CATEGORIE,
                ID_DEVISE,
                RaiSocTri,
                Archive,
                DateCreation,
                Langue,
                Effectif,
                CA,
                Modele,
                DepotFichiers,
                ApprobationEnLigne,
                ExpediteurSocUtil
            )
            OUTPUT INSERTED.ID
            VALUES (?, ?, ?, 0, GETDATE(), ?, ?, ?, 0, 0, 0, 1)
        """, (
            id_categorie,
            'TND',
            raison_sociale,
            1036,  # Langue
            0,     # Effectif
            0      # Chiffre d'affaires
        ))
        id_societe = cursor.fetchone()[0]

        # 2. Insertion dans SOCIETES_ADRESSES
        cursor.execute("""
            INSERT INTO SOCIETES_ADRESSES (
                ID_SOCIETE, Nom, Adresse, Ville, CodePostal,
                ID_PAYS, Telephone, Fax, Mail,
                RefuseEMailling, AdrPostale, AdrPhysique,
                AdrFacturation, AdrLivraison
            )
            VALUES (?, ?, ?, ?, ?, 
                (SELECT TOP 1 ID FROM PAYS WHERE Nom = ?),
                ?, ?, ?, 
                0, 1, 1, 0, 1
            )
        """, (
            id_societe,
            raison_sociale,
            '',                 # Adresse vide mais requise
            ville or '',
            '',                 # CodePostal vide
            pays,
            telephone or '',
            '',                 # Fax vide
            email or ''
        ))

        # 3. Générer un numéro de compte unique
        cursor.execute("SELECT ISNULL(MAX(CAST(Compte AS INT)), 0) + 1 FROM SOCIETES_SOCUTIL")
        nouveau_compte = cursor.fetchone()[0]

        # 4. Insertion dans SOCIETES_SOCUTIL
        cursor.execute("""
            INSERT INTO SOCIETES_SOCUTIL (
                ID_SOCIETE, ID_SOCUTIL, Compte, Coefficient,
                ClientProspect, RegElemFact, ID_TARIF
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            id_societe,
            0,  # ID_SOCUTIL existant
            str(nouveau_compte).zfill(5),
            30,
            2,  # Prospect
            1,  # RegElemFact
            0   # ID_TARIF par défaut
        ))


        cursor.connection.commit()
        return id_societe

def ajouter_contact(id_societe, nom, prenom, telephone, email, id_fonction=None, langue=1):
    with get_db_cursor() as cursor:
        cursor.execute("""
            INSERT INTO PERSONNES (Nom, Prenom, Telephone, Langue, Archive)
            VALUES (?, ?, ?, ?, 0)
        """, nom, prenom, telephone, langue)
        cursor.execute("SELECT SCOPE_IDENTITY()")
        id_personne = cursor.fetchone()[0]

        cursor.execute("""
            INSERT INTO PERSONNES_MAIL (ID_PERSONNE, Mail, ParDefaut, RefuseEMailling)
            VALUES (?, ?, 1, 0)
        """, id_personne, email)

        cursor.execute("""
            INSERT INTO SOCIETES_PERSONNES (ID_SOCIETE, ID_PERSONNE, Principal, ApprobateurPage, EmetteurPage)
            VALUES (?, ?, 1, 0, 0)
        """, id_societe, id_personne)

        if id_fonction:
            cursor.execute("""
                INSERT INTO PERSONNES_FONCTIONS (ID_PERSONNE, ID_FONCTION, Ordre)
                VALUES (?, ?, 1)
            """, id_personne, id_fonction)

        cursor.connection.commit()
        return id_personne
# Fonction pour insérer un rapport dans VISITES_CLIENTS (type client retiré)
def enregistrer_visite(id_societe, raison_sociale, nature_visite, objet, origine, sujets, bilan, visiteur, cree_par):
    with get_db_cursor() as cursor:
        cursor.execute("""
            INSERT INTO VISITES_CLIENTS (
                ID_SOCIETE, RaisonSociale, DateVisite, NatureVisite,
                Objet, Origine, Sujets, Bilan, Visiteur, CreePar, CreeLe
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            id_societe,
            raison_sociale,
            datetime.today().date(),
            nature_visite,
            objet,
            origine,
            sujets,
            bilan,
            visiteur,
            cree_par,
            datetime.now()
        ))
        cursor.connection.commit()
        return True