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

def get_db_connection():
    """Retourne une connexion à la base de données"""
    return pyodbc.connect(get_connection_string())

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
                Numero_COMMANDES,
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
                "Numero_COMMANDES": row.Numero_COMMANDES,
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
                Numero_COMMANDES,
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
        
        # Récupérer les détails des opérateurs depuis la table Employes si disponible
        operateur_machine_impression_details = []
        chef_details = {}
        
        try:
            if controle.operateur_machine_impression:
                # Parser les noms des opérateurs séparés par des virgules
                op_names = [name.strip() for name in controle.operateur_machine_impression.split(',')]
                for full_name in op_names:
                    if full_name:
                        # Essayer de récupérer les détails depuis la base
                        parts = full_name.split()
                        if len(parts) >= 2:
                            nom = parts[0]
                            prenom = ' '.join(parts[1:])
                            cursor.execute("""
                                SELECT TOP 1 Matricule, Nom, Prenom 
                                FROM Employes 
                                WHERE LTRIM(RTRIM(Nom)) = ? AND LTRIM(RTRIM(Prenom)) = ?
                            """, (nom, prenom))
                            emp = cursor.fetchone()
                            if emp:
                                operateur_machine_impression_details.append({
                                    'matricule': (emp.Matricule or '').strip(),
                                    'nom': (emp.Nom or '').strip(),
                                    'prenom': (emp.Prenom or '').strip()
                                })
            
            # Récupérer les détails du chef de section
            if controle.validation_chef:
                parts = controle.validation_chef.split()
                if len(parts) >= 2:
                    nom = parts[0]
                    prenom = ' '.join(parts[1:])
                    cursor.execute("""
                        SELECT TOP 1 Matricule, Nom, Prenom 
                        FROM Employes 
                        WHERE LTRIM(RTRIM(Nom)) = ? AND LTRIM(RTRIM(Prenom)) = ?
                    """, (nom, prenom))
                    emp = cursor.fetchone()
                    if emp:
                        chef_details = {
                            'chef_matricule': (emp.Matricule or '').strip(),
                            'chef_nom': (emp.Nom or '').strip(),
                            'chef_prenom': (emp.Prenom or '').strip()
                        }
        except Exception as e:
            # Si la table Employes n'existe pas ou autre erreur, on continue sans les détails
            print(f"Avertissement: Impossible de récupérer les détails des opérateurs depuis Employes: {e}")
        
        result = {
            "id": controle.id,
            "date_controle": controle.date_controle,
            "Numero_COMMANDES": controle.Numero_COMMANDES,
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
        
        # Ajouter les détails des opérateurs machine impression si disponibles
        if operateur_machine_impression_details:
            result['operateur_machine_impression_matricules'] = [d['matricule'] for d in operateur_machine_impression_details]
            result['operateur_machine_impression_noms'] = [d['nom'] for d in operateur_machine_impression_details]
            result['operateur_machine_impression_prenoms'] = [d['prenom'] for d in operateur_machine_impression_details]
        
        # Ajouter les détails du chef de section si disponibles
        if chef_details:
            result.update(chef_details)
        
        return result

def get_controle_qualite_by_numero(numero_commande):
    """Récupère le contrôle qualité le plus récent par numéro de commande avec ses tolérances"""
    with get_db_cursor() as cursor:
        # Nettoyer le numéro de commande (enlever les espaces)
        numero_clean = numero_commande.strip() if numero_commande else ''
        
        cursor.execute("""
            SELECT TOP 1
                id,
                date_controle,
                Numero_COMMANDES,
                operateur,
                machine_impression,
                operateur_machine_impression,
                machine_decoupe,
                operateur_machine_decoupe,
                rebus,
                validation_chef,
                date_creation
            FROM CONTROLES_QUALITE
            WHERE LTRIM(RTRIM(Numero_COMMANDES)) = ?
            ORDER BY date_creation DESC
        """, (numero_clean,))
        
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
        """, (controle.id,))
        
        tolérances = []
        for row in cursor.fetchall():
            tolérances.append({
                "tolerance": row.tolerance,
                "quantite_conforme": row.quantite_conforme,
                "quantite_non_conforme": row.quantite_non_conforme
            })
        
        result = {
            "id": controle.id,
            "date_controle": controle.date_controle,
            "Numero_COMMANDES": controle.Numero_COMMANDES,
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
        
        return result

def create_controle_qualite(data):
    """Crée un nouveau contrôle qualité"""
    try:
        with get_db_cursor() as cursor:
            # Insérer le contrôle qualité et récupérer l'ID directement
            print(f"DEBUG CREATE: Insertion contrôle avec data={data}")
            cursor.execute("""
                INSERT INTO CONTROLES_QUALITE (
                    date_controle, Numero_COMMANDES, operateur, machine_impression, operateur_machine_impression, 
                    machine_decoupe, operateur_machine_decoupe, rebus, validation_chef, date_creation
                )
                OUTPUT INSERTED.id
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, GETDATE())
            """, (
                data['date_controle'],
                data['Numero_COMMANDES'],
                data['operateur'],
                data.get('machine_impression', ''),
                data.get('operateur_machine_impression', ''),
                data.get('machine_decoupe', ''),
                data.get('operateur_machine_decoupe', ''),
                data.get('rebus', 0),
                data.get('validation_chef', ''),
            ))
            
            # Récupérer l'ID du contrôle créé
            controle_id = cursor.fetchone()[0]
            print(f"DEBUG CREATE: Contrôle créé avec ID={controle_id}")
            
            # Insérer les tolérances (accepte 'tolérances' ou 'tolerances')
            tolerances_list = data.get('tolérances') or data.get('tolerances') or []
            print(f"DEBUG CREATE: Insertion de {len(tolerances_list)} tolérances")
            if tolerances_list:
                for i, tolerance_data in enumerate(tolerances_list):
                    # Ne pas insérer de lignes vides
                    if (tolerance_data.get('tolerance', '').strip() or 
                        tolerance_data.get('quantite_conforme', 0) or 
                        tolerance_data.get('quantite_non_conforme', 0)):
                        print(f"DEBUG CREATE: Insertion tolérance {i+1}: {tolerance_data}")
                    cursor.execute("""
                        INSERT INTO TOLERANCES_CONTROLE (
                            controle_id, tolerance, quantite_conforme, quantite_non_conforme
                        ) VALUES (?, ?, ?, ?)
                    """, (
                        controle_id,
                            tolerance_data.get('tolerance', ''),
                            tolerance_data.get('quantite_conforme', 0),
                            tolerance_data.get('quantite_non_conforme', 0)
                    ))
            
            # Valider la transaction
            cursor.commit()
            print(f"DEBUG CREATE: Transaction validée, retour ID={controle_id}")
            return controle_id
    except Exception as e:
        print(f"ERREUR lors de la création du contrôle qualité: {e}")
        import traceback
        traceback.print_exc()
        return None

def update_controle_qualite(controle_id, data):
    """Met à jour un contrôle qualité"""
    try:
        with get_db_cursor() as cursor:
            # Mettre à jour le contrôle qualité
            cursor.execute("""
                UPDATE CONTROLES_QUALITE SET
                    date_controle = ?,
                    Numero_COMMANDES = ?,
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
                data['Numero_COMMANDES'],
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
            
            # Insérer les nouvelles tolérances (accepte 'tolérances' ou 'tolerances')
            tolerances_list = data.get('tolérances') or data.get('tolerances') or []
            if tolerances_list:
                for tolerance_data in tolerances_list:
                    # Ne pas insérer de lignes vides
                    if (tolerance_data.get('tolerance', '').strip() or 
                        tolerance_data.get('quantite_conforme', 0) or 
                        tolerance_data.get('quantite_non_conforme', 0)):
                        cursor.execute("""
                            INSERT INTO TOLERANCES_CONTROLE (
                            controle_id, tolerance, quantite_conforme, quantite_non_conforme
                            ) VALUES (?, ?, ?, ?)
                            """, (
                            controle_id,
                            tolerance_data.get('tolerance', ''),
                            tolerance_data.get('quantite_conforme', 0),
                            tolerance_data.get('quantite_non_conforme', 0)
                            ))
            # Valider la transaction
            cursor.connection.commit()
            
            return True
    except Exception as e:
        print(f"Erreur lors de la mise à jour du contrôle qualité: {e}")
        return False

def get_statistiques_controle_qualite():
    """Récupère les statistiques globales de contrôle qualité"""
    with get_db_cursor() as cursor:
        # Statistiques globales
        cursor.execute("""
            SELECT 
                COUNT(*) as total_controles,
                COUNT(CASE WHEN validation_chef IS NOT NULL AND validation_chef != '' THEN 1 END) as controles_valides,
                AVG(CAST(rebus AS FLOAT)) as rebus_moyen,
                SUM(rebus) as total_rebus
            FROM CONTROLES_QUALITE
        """)
        
        row = cursor.fetchone()
        stats = {
                "total_controles": row.total_controles or 0,
                "controles_valides": row.controles_valides or 0,
                "rebus_moyen": round(row.rebus_moyen or 0, 3),
                "total_rebus": row.total_rebus or 0
            }
        
        # Calculer taux de conformité et taux de rebus
        cursor.execute("""
            SELECT 
                SUM(T.quantite_conforme) as total_conforme,
                SUM(CASE 
                    WHEN rn = 1 THEN T.quantite_non_conforme 
                    ELSE 0 
                END) as total_non_conforme_final
            FROM TOLERANCES_CONTROLE T
            INNER JOIN (
                SELECT controle_id, id, 
                       ROW_NUMBER() OVER (PARTITION BY controle_id ORDER BY id DESC) as rn
                FROM TOLERANCES_CONTROLE
            ) LastRow ON T.id = LastRow.id
        """)
        
        row2 = cursor.fetchone()
        total_conforme = row2.total_conforme or 0
        total_non_conforme = row2.total_non_conforme_final or 0
        total_produit = total_conforme + total_non_conforme
        
        stats["total_conforme"] = total_conforme
        stats["total_non_conforme"] = total_non_conforme
        stats["total_produit"] = total_produit
        stats["taux_conformite"] = round((total_conforme / total_produit * 100) if total_produit > 0 else 0, 3)
        stats["taux_rebus"] = round((total_non_conforme / total_produit * 100) if total_produit > 0 else 0, 3)
        
        return stats

def get_performance_par_machine():
    """Récupère les statistiques de performance par machine d'impression"""
    with get_db_cursor() as cursor:
        cursor.execute("""
            WITH DernieresLignes AS (
                SELECT 
                    T.controle_id,
                    T.quantite_conforme,
                    T.quantite_non_conforme,
                    ROW_NUMBER() OVER (PARTITION BY T.controle_id ORDER BY T.id DESC) as rn
                FROM TOLERANCES_CONTROLE T
            ),
            StatsParControle AS (
                SELECT 
                    C.id,
                    C.machine_impression,
                    SUM(T.quantite_conforme) as total_conforme,
                    MAX(CASE WHEN D.rn = 1 THEN D.quantite_non_conforme ELSE 0 END) as rebus
                FROM CONTROLES_QUALITE C
                LEFT JOIN TOLERANCES_CONTROLE T ON T.controle_id = C.id
                LEFT JOIN DernieresLignes D ON D.controle_id = C.id AND D.rn = 1
                WHERE C.machine_impression IS NOT NULL AND C.machine_impression != ''
                GROUP BY C.id, C.machine_impression
            )
            SELECT 
                machine_impression,
                COUNT(*) as nombre_controles,
                SUM(total_conforme) as total_conforme,
                SUM(rebus) as total_rebus,
                SUM(total_conforme + rebus) as total_produit,
                CASE 
                    WHEN SUM(total_conforme + rebus) > 0 
                    THEN ROUND(SUM(total_conforme) * 100.0 / SUM(total_conforme + rebus), 2)
                    ELSE 0 
                END as taux_conformite
            FROM StatsParControle
            GROUP BY machine_impression
            ORDER BY taux_conformite DESC
        """)
        
        machines = []
        for row in cursor.fetchall():
            machines.append({
                "machine": row.machine_impression,
                "nombre_controles": row.nombre_controles or 0,
                "total_conforme": row.total_conforme or 0,
                "total_rebus": row.total_rebus or 0,
                "total_produit": row.total_produit or 0,
                "taux_conformite": row.taux_conformite or 0
            })
        return machines

def get_evolution_qualite(jours=30):
    """Récupère l'évolution de la qualité sur les N derniers jours"""
    with get_db_cursor() as cursor:
        cursor.execute("""
            WITH DernieresLignes AS (
                SELECT 
                    T.controle_id,
                    T.quantite_non_conforme,
                    ROW_NUMBER() OVER (PARTITION BY T.controle_id ORDER BY T.id DESC) as rn
                FROM TOLERANCES_CONTROLE T
            ),
            StatsParJour AS (
                SELECT 
                    CAST(C.date_controle AS DATE) as jour,
                    SUM(T.quantite_conforme) as total_conforme,
                    SUM(CASE WHEN D.rn = 1 THEN D.quantite_non_conforme ELSE 0 END) as total_rebus
                FROM CONTROLES_QUALITE C
                LEFT JOIN TOLERANCES_CONTROLE T ON T.controle_id = C.id
                LEFT JOIN DernieresLignes D ON D.controle_id = C.id
                WHERE C.date_controle >= DATEADD(day, -?, GETDATE())
                GROUP BY CAST(C.date_controle AS DATE)
            )
            SELECT 
                jour,
                total_conforme,
                total_rebus,
                (total_conforme + total_rebus) as total_produit,
                CASE 
                    WHEN (total_conforme + total_rebus) > 0 
                    THEN ROUND(total_conforme * 100.0 / (total_conforme + total_rebus), 2)
                    ELSE 0 
                END as taux_conformite
            FROM StatsParJour
            ORDER BY jour
        """, (jours,))
        
        evolution = []
        for row in cursor.fetchall():
            # Gérer le cas où jour est déjà une chaîne
            date_str = ''
            if row.jour:
                if isinstance(row.jour, str):
                    date_str = row.jour.split('T')[0] if 'T' in row.jour else row.jour
                else:
                    date_str = row.jour.strftime('%Y-%m-%d')
            
            evolution.append({
                "date": date_str,
                "total_conforme": row.total_conforme or 0,
                "total_rebus": row.total_rebus or 0,
                "total_produit": row.total_produit or 0,
                "taux_conformite": row.taux_conformite or 0
            })
        return evolution

def get_dossiers_probleme(seuil_rebus_pct=10):
    """Récupère les contrôles individuels avec un taux de rebus élevé"""
    with get_db_cursor() as cursor:
        cursor.execute("""
            WITH DernieresLignes AS (
                SELECT 
                    T.controle_id,
                    T.quantite_non_conforme,
                    ROW_NUMBER() OVER (PARTITION BY T.controle_id ORDER BY T.id DESC) as rn
                FROM TOLERANCES_CONTROLE T
            ),
            StatsControle AS (
                SELECT 
                    C.id as controle_id,
                    C.Numero_COMMANDES,
                    C.date_controle,
                    C.operateur,
                    C.machine_impression,
                    SUM(T.quantite_conforme) as total_conforme,
                    MAX(CASE WHEN D.rn = 1 THEN D.quantite_non_conforme ELSE 0 END) as total_rebus
                FROM CONTROLES_QUALITE C
                LEFT JOIN TOLERANCES_CONTROLE T ON T.controle_id = C.id
                LEFT JOIN DernieresLignes D ON D.controle_id = C.id
                GROUP BY C.id, C.Numero_COMMANDES, C.date_controle, C.operateur, C.machine_impression
            )
            SELECT 
                controle_id,
                Numero_COMMANDES,
                date_controle,
                operateur,
                machine_impression,
                total_conforme,
                total_rebus,
                (total_conforme + total_rebus) as total_produit,
                CASE 
                    WHEN (total_conforme + total_rebus) > 0 
                    THEN ROUND(total_rebus * 100.0 / (total_conforme + total_rebus), 3)
                    ELSE 0 
                END as taux_rebus
            FROM StatsControle
            WHERE (total_conforme + total_rebus) > 0
              AND (total_rebus * 100.0 / (total_conforme + total_rebus)) >= ?
            ORDER BY taux_rebus DESC
        """, (seuil_rebus_pct,))
        
        dossiers = []
        for row in cursor.fetchall():
            # Gérer le cas où date_controle est déjà une chaîne
            date_str = ''
            if row.date_controle:
                if isinstance(row.date_controle, str):
                    date_str = row.date_controle.split('T')[0] if 'T' in row.date_controle else row.date_controle
                else:
                    date_str = row.date_controle.strftime('%Y-%m-%d')
            
            dossiers.append({
                "controle_id": row.controle_id,
                "Numero_COMMANDES": row.Numero_COMMANDES,
                "date": date_str,
                "operateur": row.operateur or '',
                "machine": row.machine_impression or '',
                "total_conforme": row.total_conforme or 0,
                "total_rebus": row.total_rebus or 0,
                "total_produit": row.total_produit or 0,
                "taux_rebus": row.taux_rebus or 0
            })
        return dossiers

def get_comparaison_periodes(date_debut1, date_fin1, date_debut2, date_fin2):
    """Compare les statistiques entre deux périodes"""
    with get_db_cursor() as cursor:
        # Statistiques pour la période 1
        cursor.execute("""
            WITH DernieresLignes AS (
                SELECT 
                    T.controle_id,
                    T.quantite_non_conforme,
                    ROW_NUMBER() OVER (PARTITION BY T.controle_id ORDER BY T.id DESC) as rn
                FROM TOLERANCES_CONTROLE T
            )
            SELECT 
                COUNT(DISTINCT C.id) as nombre_controles,
                SUM(T.quantite_conforme) as total_conforme,
                SUM(CASE WHEN D.rn = 1 THEN D.quantite_non_conforme ELSE 0 END) as total_rebus,
                SUM(T.quantite_conforme) + SUM(CASE WHEN D.rn = 1 THEN D.quantite_non_conforme ELSE 0 END) as total_produit
            FROM CONTROLES_QUALITE C
            LEFT JOIN TOLERANCES_CONTROLE T ON T.controle_id = C.id
            LEFT JOIN DernieresLignes D ON D.controle_id = C.id
            WHERE CAST(C.date_controle AS DATE) BETWEEN ? AND ?
        """, (date_debut1, date_fin1))
        
        row1 = cursor.fetchone()
        periode1 = {
            "nombre_controles": row1.nombre_controles or 0,
            "total_conforme": row1.total_conforme or 0,
            "total_rebus": row1.total_rebus or 0,
            "total_produit": row1.total_produit or 0
        }
        periode1["taux_conformite"] = round((periode1["total_conforme"] / periode1["total_produit"] * 100) if periode1["total_produit"] > 0 else 0, 3)
        periode1["taux_rebus"] = round((periode1["total_rebus"] / periode1["total_produit"] * 100) if periode1["total_produit"] > 0 else 0, 3)
        
        # Statistiques pour la période 2
        cursor.execute("""
            WITH DernieresLignes AS (
                SELECT 
                    T.controle_id,
                    T.quantite_non_conforme,
                    ROW_NUMBER() OVER (PARTITION BY T.controle_id ORDER BY T.id DESC) as rn
                FROM TOLERANCES_CONTROLE T
            )
            SELECT 
                COUNT(DISTINCT C.id) as nombre_controles,
                SUM(T.quantite_conforme) as total_conforme,
                SUM(CASE WHEN D.rn = 1 THEN D.quantite_non_conforme ELSE 0 END) as total_rebus,
                SUM(T.quantite_conforme) + SUM(CASE WHEN D.rn = 1 THEN D.quantite_non_conforme ELSE 0 END) as total_produit
            FROM CONTROLES_QUALITE C
            LEFT JOIN TOLERANCES_CONTROLE T ON T.controle_id = C.id
            LEFT JOIN DernieresLignes D ON D.controle_id = C.id
            WHERE CAST(C.date_controle AS DATE) BETWEEN ? AND ?
        """, (date_debut2, date_fin2))
        
        row2 = cursor.fetchone()
        periode2 = {
            "nombre_controles": row2.nombre_controles or 0,
            "total_conforme": row2.total_conforme or 0,
            "total_rebus": row2.total_rebus or 0,
            "total_produit": row2.total_produit or 0
        }
        periode2["taux_conformite"] = round((periode2["total_conforme"] / periode2["total_produit"] * 100) if periode2["total_produit"] > 0 else 0, 3)
        periode2["taux_rebus"] = round((periode2["total_rebus"] / periode2["total_produit"] * 100) if periode2["total_produit"] > 0 else 0, 3)
        
        return {
            "periode1": periode1,
            "periode2": periode2
        }

def get_machines_impression():
    """Récupère la liste des machines d'impression depuis GP_POSTES (centre de coût 6)"""
    with get_db_cursor() as cursor:
        cursor.execute("""
            SELECT DISTINCT P.Nom, P.ID
            FROM GP_POSTES P
            WHERE P.ID_CENTRE_COUT = 6
              AND P.Nom IS NOT NULL 
              AND P.Nom != ''
            ORDER BY P.Nom
        """)
        machines = []
        for row in cursor.fetchall():
            machines.append({
                "nom": row.Nom,
                "id": row.ID
            })
        return machines

def get_comparaison_machines(machine1, machine2, jours=30):
    """Compare les statistiques entre deux machines sur une période donnée"""
    with get_db_cursor() as cursor:
        # Statistiques pour la machine 1
        cursor.execute("""
            WITH DernieresLignes AS (
                SELECT 
                    T.controle_id,
                    T.quantite_non_conforme,
                    ROW_NUMBER() OVER (PARTITION BY T.controle_id ORDER BY T.id DESC) as rn
                FROM TOLERANCES_CONTROLE T
            )
            SELECT 
                COUNT(DISTINCT C.id) as nombre_controles,
                SUM(T.quantite_conforme) as total_conforme,
                SUM(CASE WHEN D.rn = 1 THEN D.quantite_non_conforme ELSE 0 END) as total_rebus,
                SUM(T.quantite_conforme) + SUM(CASE WHEN D.rn = 1 THEN D.quantite_non_conforme ELSE 0 END) as total_produit
            FROM CONTROLES_QUALITE C
            LEFT JOIN TOLERANCES_CONTROLE T ON T.controle_id = C.id
            LEFT JOIN DernieresLignes D ON D.controle_id = C.id
            WHERE C.machine_impression = ?
              AND C.date_controle >= DATEADD(day, -?, GETDATE())
        """, (machine1, jours))
        
        row1 = cursor.fetchone()
        stats_machine1 = {
            "machine": machine1,
            "nombre_controles": row1.nombre_controles or 0,
            "total_conforme": row1.total_conforme or 0,
            "total_rebus": row1.total_rebus or 0,
            "total_produit": row1.total_produit or 0
        }
        stats_machine1["taux_conformite"] = round((stats_machine1["total_conforme"] / stats_machine1["total_produit"] * 100) if stats_machine1["total_produit"] > 0 else 0, 3)
        stats_machine1["taux_rebus"] = round((stats_machine1["total_rebus"] / stats_machine1["total_produit"] * 100) if stats_machine1["total_produit"] > 0 else 0, 3)
        
        # Statistiques pour la machine 2
        cursor.execute("""
            WITH DernieresLignes AS (
                SELECT 
                    T.controle_id,
                    T.quantite_non_conforme,
                    ROW_NUMBER() OVER (PARTITION BY T.controle_id ORDER BY T.id DESC) as rn
                FROM TOLERANCES_CONTROLE T
            )
            SELECT 
                COUNT(DISTINCT C.id) as nombre_controles,
                SUM(T.quantite_conforme) as total_conforme,
                SUM(CASE WHEN D.rn = 1 THEN D.quantite_non_conforme ELSE 0 END) as total_rebus,
                SUM(T.quantite_conforme) + SUM(CASE WHEN D.rn = 1 THEN D.quantite_non_conforme ELSE 0 END) as total_produit
            FROM CONTROLES_QUALITE C
            LEFT JOIN TOLERANCES_CONTROLE T ON T.controle_id = C.id
            LEFT JOIN DernieresLignes D ON D.controle_id = C.id
            WHERE C.machine_impression = ?
              AND C.date_controle >= DATEADD(day, -?, GETDATE())
        """, (machine2, jours))
        
        row2 = cursor.fetchone()
        stats_machine2 = {
            "machine": machine2,
            "nombre_controles": row2.nombre_controles or 0,
            "total_conforme": row2.total_conforme or 0,
            "total_rebus": row2.total_rebus or 0,
            "total_produit": row2.total_produit or 0
        }
        stats_machine2["taux_conformite"] = round((stats_machine2["total_conforme"] / stats_machine2["total_produit"] * 100) if stats_machine2["total_produit"] > 0 else 0, 3)
        stats_machine2["taux_rebus"] = round((stats_machine2["total_rebus"] / stats_machine2["total_produit"] * 100) if stats_machine2["total_produit"] > 0 else 0, 3)
        
        return {
            "machine1": stats_machine1,
            "machine2": stats_machine2
        }

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
# PROJET 10 – Contrôle Qualité - Gestion des Opérateurs
# ---------------------------
def get_operateurs():
    """Récupère la liste des opérateurs disponibles (employés)"""
    with get_db_cursor() as cursor:
        operateurs: list[dict] = []
        # Utiliser la table [dbo].[personel]
        try:
            cursor.execute("""
                SELECT 
                    Matricule,
                    COALESCE(Nom, '') AS Nom,
                    COALESCE(Prenom, '') AS Prenom
                FROM [dbo].[personel]
                WHERE Matricule IS NOT NULL
                ORDER BY Nom, Prenom
            """)
            rows = cursor.fetchall()
            for row in rows:
                # Matricule peut être un INT, le convertir en string
                matricule_str = str(row.Matricule) if row.Matricule is not None else ''
                operateurs.append({
                    "id": None,
                    "matricule": matricule_str.strip(),
                    "nom": (row.Nom or '').strip(),
                    "prenom": (row.Prenom or '').strip(),
                    "nom_complet": f"{(row.Nom or '').strip()} {(row.Prenom or '').strip()}".strip(),
                    "telephone": None,
                    "email": None
                })
        except Exception as e:
            print(f"Erreur lors de la récupération des opérateurs depuis [dbo].[personel]: {e}")
            import traceback
            traceback.print_exc()

        # Dédupliquer par matricule si nécessaire et trier
        seen = set()
        unique_operateurs = []
        for op in operateurs:
            key = (op.get("matricule") or "").strip().lower()
            if key in seen:
                continue
            seen.add(key)
            unique_operateurs.append(op)

        # Tri alpha par Nom, Prénom si disponible, sinon par matricule
        unique_operateurs.sort(key=lambda o: (
            (o.get("nom") or "").lower(),
            (o.get("prenom") or "").lower(),
            (o.get("matricule") or "").lower()
        ))
        return unique_operateurs

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