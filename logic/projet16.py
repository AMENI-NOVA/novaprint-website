"""
Projet 16 - GMAO (Gestion de la Maintenance Assistée par Ordinateur)
Gestion des interventions préventives et correctives
"""
from db import get_db_cursor

def convert_datetime_for_sql(dt_str):
    """Convertit un datetime du format ISO (avec T) vers le format SQL Server"""
    if not dt_str:
        return None
    # Remplacer le 'T' par un espace et ajouter :00 pour les secondes si nécessaire
    dt_str = str(dt_str).replace('T', ' ')
    # Ajouter les secondes si elles manquent
    if len(dt_str) == 16:  # Format 'YYYY-MM-DD HH:MM'
        dt_str += ':00'
    return dt_str

def get_operateurs_disponibles():
    """Récupère la liste de tous les opérateurs disponibles"""
    with get_db_cursor() as cursor:
        cursor.execute("""
            SELECT 
                Matricule,
                Nom,
                Prenom
            FROM personel
            WHERE Matricule IS NOT NULL
            ORDER BY Nom, Prenom
        """)
        
        operateurs = []
        for row in cursor.fetchall():
            operateurs.append({
                "matricule": row.Matricule,
                "nom": (row.Nom or '').strip(),
                "prenom": (row.Prenom or '').strip(),
                "nom_complet": f"{(row.Nom or '').strip()} {(row.Prenom or '').strip()}".strip()
            })
        
        return operateurs

def search_operateurs(query=""):
    """Recherche les opérateurs par nom ou prénom (pour API Select2 - conservé pour compatibilité)"""
    with get_db_cursor() as cursor:
        search_pattern = f"%{query}%"
        # Limiter à 50 résultats pour de meilleures performances
        cursor.execute("""
            SELECT TOP 50
                Matricule,
                Nom,
                Prenom,
                CONCAT(Nom, ' ', Prenom) as NomComplet
            FROM personel
            WHERE Nom LIKE ? OR Prenom LIKE ?
            ORDER BY Nom, Prenom
        """, (search_pattern, search_pattern))
        
        operateurs = []
        for row in cursor.fetchall():
            operateurs.append({
                "id": row.Matricule,
                "text": f"{row.Nom} {row.Prenom}",
                "matricule": row.Matricule,
                "nom": row.Nom,
                "prenom": row.Prenom
            })
        return operateurs

def search_postes(query=""):
    """Recherche les postes/machines par nom"""
    with get_db_cursor() as cursor:
        search_pattern = f"%{query}%"
        cursor.execute("""
            SELECT 
                ID,
                Nom as NomPoste
            FROM GP_POSTES
            WHERE Nom LIKE ?
            ORDER BY Nom
        """, (search_pattern,))
        
        postes = []
        for row in cursor.fetchall():
            postes.append({
                "id": row.ID,
                "text": row.NomPoste,
                "nom_poste": row.NomPoste
            })
        return postes

def get_articles_disponibles():
    """Récupère la liste de tous les articles disponibles (types 2 et 8 uniquement)"""
    with get_db_cursor() as cursor:
        cursor.execute("""
            SELECT 
                a.ID,
                a.Designation
            FROM GS_ARTICLES a
            INNER JOIN GS_FAMILLES f ON a.ID_FAMILLE = f.ID
            INNER JOIN GS_TYPES_ARTICLE t ON f.ID_TYPE_ARTICLE = t.ID
            WHERE t.ID IN (2, 8)
                AND a.ID IS NOT NULL
            ORDER BY a.Designation
        """)
        
        articles = []
        for row in cursor.fetchall():
            articles.append({
                "id": row.ID,
                "designation": row.Designation
            })
        
        return articles

def search_articles(query=""):
    """Recherche les articles/pièces détachées (types 2 et 8 uniquement)"""
    with get_db_cursor() as cursor:
        search_pattern = f"%{query}%"
        cursor.execute("""
            SELECT 
                a.ID,
                a.Designation
            FROM GS_ARTICLES a
            INNER JOIN GS_FAMILLES f ON a.ID_FAMILLE = f.ID
            INNER JOIN GS_TYPES_ARTICLE t ON f.ID_TYPE_ARTICLE = t.ID
            WHERE t.ID IN (2, 8)
                AND a.Designation LIKE ?
                AND a.ID IS NOT NULL
            ORDER BY a.Designation
        """, (search_pattern,))
        
        articles = []
        for row in cursor.fetchall():
            articles.append({
                "id": row.Designation,
                "text": row.Designation
            })
        return articles

def get_operateur_by_id(matricule):
    """Récupère un opérateur par son matricule"""
    with get_db_cursor() as cursor:
        cursor.execute("""
            SELECT 
                Matricule,
                Nom,
                Prenom
            FROM personel
            WHERE Matricule = ?
        """, (matricule,))
        
        row = cursor.fetchone()
        if row:
            return {
                "matricule": row.Matricule,
                "nom": row.Nom,
                "prenom": row.Prenom,
                "nom_complet": f"{row.Nom} {row.Prenom}"
            }
        return None

def create_demande_intervention(data):
    """
    Crée une nouvelle demande d'intervention (maintenance corrective)
    """
    with get_db_cursor() as cursor:
        # Récupérer le nom complet de l'opérateur
        cursor.execute("""
            SELECT CONCAT(Nom, ' ', Prenom) as NomComplet
            FROM personel
            WHERE Matricule = ?
        """, (data.get('matr_op_dem'),))
        
        oper_row = cursor.fetchone()
        oper_dem = oper_row.NomComplet if oper_row else None
        
        # Le nom de la machine vient directement du formulaire (PostesReel)
        postes_reel = data.get('postes_reel', '')
        
        # ID_EMach contient l'état de la machine (0=Sans Arrêt, 1=Avec Arrêt)
        # référence à WEB_GMAO_EMach
        id_emach = int(data.get('id_emach', 0))
        
        # Insérer la demande d'intervention
        cursor.execute("""
            INSERT INTO WEB_GMAO (
                Code,
                DteDemIn,
                MatrOpDem,
                OperDem,
                ID_EMach,
                PostesReel,
                DemIn,
                ID_StatDemIn,
                DateCreation,
                DateModification
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, 0, GETDATE(), GETDATE())
        """, (
            'C',  # Code = 'C' pour Corrective
            convert_datetime_for_sql(data.get('dte_dem_in')),
            data.get('matr_op_dem'),
            oper_dem,
            id_emach,  # 0=Sans Arrêt, 1=Avec Arrêt
            postes_reel,
            data.get('dem_in', '')
        ))
        
        # Récupérer l'ID de la demande créée
        cursor.execute("SELECT @@IDENTITY as ID")
        result = cursor.fetchone()
        cursor.connection.commit()
        return result.ID if result else None

def update_demande_intervention(demande_id, data):
    """
    Met à jour une demande d'intervention existante
    """
    with get_db_cursor() as cursor:
        # Récupérer le nom complet de l'opérateur
        cursor.execute("""
            SELECT CONCAT(Nom, ' ', Prenom) as NomComplet
            FROM personel
            WHERE Matricule = ?
        """, (data.get('matr_op_dem'),))
        
        oper_row = cursor.fetchone()
        oper_dem = oper_row.NomComplet if oper_row else None
        
        # Le nom de la machine vient directement du formulaire
        postes_reel = data.get('postes_reel', '')
        
        # ID_EMach contient l'état de la machine (0=Sans Arrêt, 1=Avec Arrêt)
        id_emach = int(data.get('id_emach', 0))
        
        # Mettre à jour la demande d'intervention
        cursor.execute("""
            UPDATE WEB_GMAO SET
                DteDemIn = ?,
                MatrOpDem = ?,
                OperDem = ?,
                ID_EMach = ?,
                PostesReel = ?,
                DemIn = ?,
                DateModification = GETDATE()
            WHERE ID = ?
        """, (
            convert_datetime_for_sql(data.get('dte_dem_in')),
            data.get('matr_op_dem'),
            oper_dem,
            id_emach,  # 0=Sans Arrêt, 1=Avec Arrêt
            postes_reel,
            data.get('dem_in', ''),
            demande_id
        ))
        
        cursor.connection.commit()
        return True

def delete_demande_intervention(demande_id):
    """
    Supprime une demande d'intervention
    """
    with get_db_cursor() as cursor:
        cursor.execute("""
            DELETE FROM WEB_GMAO
            WHERE ID = ?
        """, (demande_id,))
        
        cursor.connection.commit()
        return True

def update_reparation(demande_id, data):
    """
    Ajoute les informations de réparation à une demande existante
    """
    with get_db_cursor() as cursor:
        # Récupérer le nom de l'intervenant
        intervenant_nom = None
        if data.get('mat_inter'):
            cursor.execute("""
                SELECT CONCAT(Nom, ' ', Prenom) as NomComplet
                FROM personel
                WHERE Matricule = ?
            """, (data.get('mat_inter'),))
            
            inter_row = cursor.fetchone()
            intervenant_nom = inter_row.NomComplet if inter_row else None
        
        # Gérer DteFin selon le statut et les données fournies
        dte_fin = None
        id_stat_rep = data.get('id_stat_rep', 0)
        
        if id_stat_rep != 0:  # Pas "En cours"
            if data.get('dte_fin'):
                # Utilisateur a saisi une date de fin
                dte_fin = convert_datetime_for_sql(data.get('dte_fin'))
            elif data.get('tps_reel'):
                # Calculer DteFin à partir de TpsReel (en heures)
                from datetime import datetime, timedelta
                dte_deb_str = convert_datetime_for_sql(data.get('dte_deb'))
                try:
                    dte_deb = datetime.strptime(dte_deb_str, '%Y-%m-%d %H:%M:%S')
                    tps_reel_hours = float(data.get('tps_reel'))
                    dte_fin_calc = dte_deb + timedelta(hours=tps_reel_hours)
                    dte_fin = dte_fin_calc.strftime('%Y-%m-%d %H:%M:%S')
                except:
                    dte_fin = None
        # Si id_stat_rep = 0, dte_fin reste NULL
        # TpsReel sera calculé automatiquement par SQL Server via la colonne calculée
        
        # Mettre à jour l'enregistrement avec les infos de réparation
        cursor.execute("""
            UPDATE WEB_GMAO SET
                DteDeb = ?,
                DteFin = ?,
                MatInter = ?,
                Internvenant = ?,
                PostesReel = ?,
                Nat = ?,
                ID_StatRep = ?,
                DateModification = GETDATE()
            WHERE ID = ?
        """, (
            convert_datetime_for_sql(data.get('dte_deb')),
            dte_fin,
            data.get('mat_inter'),
            intervenant_nom,
            data.get('postes_reel', ''),
            data.get('nat', 'Mec'),
            id_stat_rep,
            demande_id
        ))
        
        cursor.connection.commit()
        return True

def create_reparation_direct(data):
    """
    Crée une réparation directe (suite à inspection, sans demande d'intervention préalable)
    """
    with get_db_cursor() as cursor:
        # Récupérer le nom de l'intervenant
        intervenant_nom = None
        if data.get('mat_inter'):
            cursor.execute("""
                SELECT CONCAT(Nom, ' ', Prenom) as NomComplet
                FROM personel
                WHERE Matricule = ?
            """, (data.get('mat_inter'),))
            
            inter_row = cursor.fetchone()
            intervenant_nom = inter_row.NomComplet if inter_row else None
        
        # Gérer DteFin selon le statut et les données fournies
        dte_fin = None
        id_stat_rep = data.get('id_stat_rep', 0)
        
        if id_stat_rep != 0:  # Pas "En cours"
            if data.get('dte_fin'):
                # Utilisateur a saisi une date de fin
                dte_fin = convert_datetime_for_sql(data.get('dte_fin'))
            elif data.get('tps_reel'):
                # Calculer DteFin à partir de TpsReel (en heures)
                from datetime import datetime, timedelta
                dte_deb_str = convert_datetime_for_sql(data.get('dte_deb'))
                try:
                    dte_deb = datetime.strptime(dte_deb_str, '%Y-%m-%d %H:%M:%S')
                    tps_reel_hours = float(data.get('tps_reel'))
                    dte_fin_calc = dte_deb + timedelta(hours=tps_reel_hours)
                    dte_fin = dte_fin_calc.strftime('%Y-%m-%d %H:%M:%S')
                except:
                    dte_fin = None
        # Si id_stat_rep = 0, dte_fin reste NULL
        # TpsReel sera calculé automatiquement par SQL Server via la colonne calculée
        
        # Insérer une nouvelle ligne avec seulement les infos de réparation
        cursor.execute("""
            INSERT INTO WEB_GMAO (
                Code, DteDeb, DteFin, MatInter, Internvenant, PostesReel, Nat,
                ID_StatRep, ID_StatDemIn, DateCreation, DateModification
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, GETDATE(), GETDATE())
        """, (
            'C',  # Code = 'C' pour Corrective (comme les demandes)
            convert_datetime_for_sql(data.get('dte_deb')),
            dte_fin,
            data.get('mat_inter'),
            intervenant_nom,
            data.get('postes_reel', ''),
            data.get('nat', 'Mec'),
            id_stat_rep,
            0  # ID_StatDemIn = 0 (pas de demande d'intervention)
        ))
        
        # Récupérer l'ID généré
        cursor.execute("SELECT @@IDENTITY AS ID")
        new_id = cursor.fetchone().ID
        
        cursor.connection.commit()
        return new_id

def get_statut_rep_id_by_designation(designation):
    """
    Récupère l'ID d'un statut de réparation depuis sa désignation
    """
    with get_db_cursor() as cursor:
        cursor.execute("""
            SELECT ID FROM WEB_GMAO_StatRep
            WHERE Designation = ?
        """, (designation,))
        
        row = cursor.fetchone()
        return row.ID if row else None

def update_reparation_status(demande_id, data):
    """
    Met à jour une réparation avec un nouveau statut
    """
    with get_db_cursor() as cursor:
        # Récupérer le nom de l'intervenant
        intervenant_nom = None
        if data.get('mat_inter'):
            cursor.execute("""
                SELECT CONCAT(Nom, ' ', Prenom) as NomComplet
                FROM personel
                WHERE Matricule = ?
            """, (data.get('mat_inter'),))
            
            inter_row = cursor.fetchone()
            intervenant_nom = inter_row.NomComplet if inter_row else None
        
        # Obtenir l'ID du statut depuis la désignation
        statut_map = {
            'cloturer': 'Cloturée',
            'en_attente': 'En Attente',
            'temporaire': 'Temporaire'
        }
        statut_designation = statut_map.get(data.get('statut'))
        id_stat_rep = None
        if statut_designation:
            id_stat_rep = get_statut_rep_id_by_designation(statut_designation)
        
        if not id_stat_rep:
            raise ValueError(f"Statut '{statut_designation}' non trouvé dans WEB_GMAO_StatRep")
        
        # Gérer DteFin selon les cas
        dte_fin = None
        if data.get('dte_fin'):
            dte_fin = convert_datetime_for_sql(data.get('dte_fin'))
        elif data.get('tps_reel'):
            # Calculer DteFin à partir de TpsReel (en heures)
            from datetime import datetime, timedelta
            dte_deb_str = convert_datetime_for_sql(data.get('dte_deb'))
            try:
                dte_deb = datetime.strptime(dte_deb_str, '%Y-%m-%d %H:%M:%S')
                tps_reel_hours = float(data.get('tps_reel'))
                dte_fin_calc = dte_deb + timedelta(hours=tps_reel_hours)
                dte_fin = dte_fin_calc.strftime('%Y-%m-%d %H:%M:%S')
            except:
                dte_fin = None
        
        # Si la réparation est clôturée (ID_StatRep = 1), la demande doit aussi être clôturée
        # Règle : ID_StatRep = 1 → ID_StatDemIn = 1 automatiquement
        id_stat_dem_in_to_set = None
        if id_stat_rep == 1:  # Cloturée
            # Obtenir l'ID correspondant à "Cloturée" dans WEB_GMAO_StatDemIn
            cursor.execute("SELECT ID FROM WEB_GMAO_StatDemIn WHERE Designation = 'Cloturée'")
            stat_dem_row = cursor.fetchone()
            if stat_dem_row:
                id_stat_dem_in_to_set = stat_dem_row.ID
        
        # Mettre à jour l'enregistrement avec les infos de réparation et le nouveau statut
        if id_stat_dem_in_to_set is not None:
            cursor.execute("""
                UPDATE WEB_GMAO SET
                    DteDeb = ?,
                    DteFin = ?,
                    MatInter = ?,
                    Internvenant = ?,
                    PostesReel = ?,
                    Nat = ?,
                    ID_StatRep = ?,
                    ID_StatDemIn = ?,
                    DateModification = GETDATE()
                WHERE ID = ?
            """, (
                convert_datetime_for_sql(data.get('dte_deb')),
                dte_fin,
                data.get('mat_inter'),
                intervenant_nom,
                data.get('postes_reel', ''),
                data.get('nat', 'Mec'),
                id_stat_rep,
                id_stat_dem_in_to_set,
                demande_id
            ))
        else:
            cursor.execute("""
                UPDATE WEB_GMAO SET
                    DteDeb = ?,
                    DteFin = ?,
                    MatInter = ?,
                    Internvenant = ?,
                    PostesReel = ?,
                    Nat = ?,
                    ID_StatRep = ?,
                    DateModification = GETDATE()
                WHERE ID = ?
            """, (
                convert_datetime_for_sql(data.get('dte_deb')),
                dte_fin,
                data.get('mat_inter'),
                intervenant_nom,
                data.get('postes_reel', ''),
                data.get('nat', 'Mec'),
                id_stat_rep,
                demande_id
            ))
        
        cursor.connection.commit()
        return True

def delete_reparation(demande_id):
    """
    Supprime les informations de réparation d'une demande
    - Si c'est une fiche "En cours" (ID_StatRep = 0) sans demande liée (ID_StatDemIn = 0), supprime complètement la fiche
    - Sinon, remet les champs de réparation à NULL
    """
    with get_db_cursor() as cursor:
        # Vérifier si c'est une fiche "En cours" sans demande liée
        cursor.execute("""
            SELECT ID_StatRep, ID_StatDemIn FROM WEB_GMAO WHERE ID = ?
        """, (demande_id,))
        
        row = cursor.fetchone()
        if row and row.ID_StatRep == 0 and (row.ID_StatDemIn == 0 or row.ID_StatDemIn is None):
            # Supprimer complètement la fiche
            cursor.execute("DELETE FROM WEB_GMAO WHERE ID = ?", (demande_id,))
        else:
            # Remettre les champs de réparation à NULL
            cursor.execute("""
                UPDATE WEB_GMAO SET
                    DteDeb = NULL,
                    DteFin = NULL,
                    MatInter = NULL,
                    Internvenant = NULL,
                    ID_StatRep = NULL,
                    DateModification = GETDATE()
                WHERE ID = ?
            """, (demande_id,))
            
            # Supprimer aussi les articles associés dans WEB_GMAO_ARTICLES
            cursor.execute("""
                DELETE FROM WEB_GMAO_ARTICLES
                WHERE ID_WEB_GMAO = ?
            """, (demande_id,))
        
        cursor.connection.commit()
        return True

def get_all_demandes():
    """Récupère toutes les demandes d'intervention avec tous les détails"""
    with get_db_cursor() as cursor:
        cursor.execute("""
            SELECT 
                g.ID,
                g.Code,
                g.DteDemIn,
                g.OperDem,
                g.MatrOpDem,
                g.PostesReel,
                g.ID_EMach,
                g.DemIn,
                g.Nat,
                g.Urg,
                g.ID_StatDemIn,
                g.ID_StatRep,
                g.DteDeb,
                g.DteFin,
                g.TpsReel,
                g.MatInter,
                g.Internvenant,
                g.DateCreation,
                g.DateModification,
                sd.Designation as StatutDemande,
                sr.Designation as StatutReparation,
                em.Designation as TypeArret
            FROM WEB_GMAO g
            LEFT JOIN WEB_GMAO_StatDemIn sd ON g.ID_StatDemIn = sd.ID
            LEFT JOIN WEB_GMAO_StatRep sr ON g.ID_StatRep = sr.ID
            LEFT JOIN WEB_GMAO_EMach em ON g.ID_EMach = em.ID
            WHERE g.Code = 'C'
            ORDER BY g.DateCreation DESC
        """)
        
        demandes = []
        for row in cursor.fetchall():
            # Formatage des dates
            dte_dem_in_str = row.DteDemIn.strftime('%Y-%m-%d %H:%M:%S') if row.DteDemIn else None
            dte_deb_str = row.DteDeb.strftime('%Y-%m-%d %H:%M:%S') if row.DteDeb else None
            dte_fin_str = row.DteFin.strftime('%Y-%m-%d %H:%M:%S') if row.DteFin else None
            date_creation_str = row.DateCreation.strftime('%Y-%m-%d %H:%M:%S') if row.DateCreation else None
            
            # Utiliser les désignations des tables de référence
            statut_demande = row.StatutDemande if row.StatutDemande else "Non Cloturée"
            # ID_StatRep = 0 signifie "En cours"
            if row.ID_StatRep == 0:
                statut_reparation = "En cours"
            else:
                statut_reparation = row.StatutReparation if row.StatutReparation else "Non démarré"
            
            demandes.append({
                "id": row.ID,
                "code": row.Code,
                "dte_dem_in": dte_dem_in_str,
                "oper_dem": row.OperDem,
                "matr_op_dem": row.MatrOpDem,
                "postes_reel": row.PostesReel,
                "id_emach": row.ID_EMach,
                "etat_machine": row.TypeArret,  # État de la machine lors de la demande (Sans Arret / Avec Arret)
                "dem_in": row.DemIn,
                "nat": row.Nat,
                "urg": row.Urg,
                "statut_demande": statut_demande,
                "statut_demande_id": row.ID_StatDemIn,
                "statut_reparation": statut_reparation,
                "statut_reparation_id": row.ID_StatRep,
                "dte_deb": dte_deb_str,
                "dte_fin": dte_fin_str,
                "tps_reel": row.TpsReel,
                "intervenant": row.Internvenant,
                "mat_inter": row.MatInter,
                "date_creation": date_creation_str
            })
        return demandes

def get_demande_by_id(demande_id):
    """Récupère une demande spécifique par son ID"""
    with get_db_cursor() as cursor:
        cursor.execute("""
            SELECT 
                g.ID, g.Code, g.DteDemIn, g.OperDem, g.MatrOpDem, g.PostesReel, g.ID_EMach, g.DemIn, g.Nat, g.Urg,
                g.ID_StatDemIn, g.ID_StatRep, g.DteDeb, g.DteFin, g.TpsReel, g.MatInter, g.Internvenant,
                em.Designation as EtatMachine,
                sr.Designation as StatutReparation
            FROM WEB_GMAO g
            LEFT JOIN WEB_GMAO_EMach em ON g.ID_EMach = em.ID
            LEFT JOIN WEB_GMAO_StatRep sr ON g.ID_StatRep = sr.ID
            WHERE g.ID = ?
        """, (demande_id,))
        
        row = cursor.fetchone()
        if not row:
            return None
        
        # Convertir TpsReel en format HH:MM pour l'affichage
        tps_reel_hhmm = None
        if row.TpsReel:
            try:
                if isinstance(row.TpsReel, str) and ':' in row.TpsReel:
                    # Déjà en format HH:MM
                    tps_reel_hhmm = row.TpsReel
                else:
                    # Convertir de heures décimales en HH:MM
                    tps_reel_hours = float(row.TpsReel)
                    hours = int(tps_reel_hours)
                    minutes = int((tps_reel_hours - hours) * 60)
                    tps_reel_hhmm = f"{hours:02d}:{minutes:02d}"
            except:
                tps_reel_hhmm = None
        
        # Déterminer le statut de réparation
        if row.ID_StatRep == 0:
            statut_reparation = "En cours"
        else:
            statut_reparation = row.StatutReparation if row.StatutReparation else "Non démarré"
        
        result = {
            "id": row.ID,
            "code": row.Code,
            "dte_dem_in": row.DteDemIn.strftime('%Y-%m-%dT%H:%M') if row.DteDemIn else '',
            "oper_dem": row.OperDem,
            "matr_op_dem": row.MatrOpDem,
            "postes_reel": row.PostesReel,
            "id_emach": row.ID_EMach,
            "etat_machine": row.EtatMachine,
            "dem_in": row.DemIn,
            "nat": row.Nat,
            "urg": row.Urg,
            "id_stat_dem_in": row.ID_StatDemIn,
            "id_stat_rep": row.ID_StatRep,
            "statut_reparation": statut_reparation,
            "dte_deb": row.DteDeb.strftime('%Y-%m-%dT%H:%M') if row.DteDeb else '',
            "dte_fin": row.DteFin.strftime('%Y-%m-%dT%H:%M') if row.DteFin else '',
            "tps_reel": tps_reel_hhmm,
            "mat_inter": row.MatInter,
            "intervenant": row.Internvenant
        }
        
        # Récupérer les articles depuis WEB_GMAO_ARTICLES
        cursor.execute("""
            SELECT 
                ID,
                ID_GS_ARTICLES,
                Designation_GS_ARTICLES,
                Designation_GS_FAMILLES,
                Designation_GS_TYPES_ARTICLE,
                Quantite
            FROM WEB_GMAO_ARTICLES
            WHERE ID_WEB_GMAO = ?
            ORDER BY ID
        """, (demande_id,))
        
        articles = []
        for art_row in cursor.fetchall():
            articles.append({
                "id": art_row.ID,
                "id_article": art_row.ID_GS_ARTICLES,
                "designation": art_row.Designation_GS_ARTICLES,
                "famille": art_row.Designation_GS_FAMILLES,
                "type": art_row.Designation_GS_TYPES_ARTICLE,
                "quantite": float(art_row.Quantite) if art_row.Quantite else 0
            })
        
        result["articles"] = articles
        return result

def add_article_to_reparation(id_web_gmao, id_gs_articles, quantite):
    """
    Ajoute un article à une fiche de réparation
    """
    with get_db_cursor() as cursor:
        cursor.execute("""
            INSERT INTO WEB_GMAO_ARTICLES (
                ID_WEB_GMAO,
                ID_GS_ARTICLES,
                Quantite
            ) VALUES (?, ?, ?)
        """, (id_web_gmao, id_gs_articles, quantite))
        
        # Récupérer l'ID généré
        cursor.execute("SELECT @@IDENTITY AS ID")
        new_id = cursor.fetchone().ID
        
        cursor.connection.commit()
        return new_id

def update_article_quantite(article_id, quantite):
    """
    Met à jour la quantité d'un article
    """
    with get_db_cursor() as cursor:
        cursor.execute("""
            UPDATE WEB_GMAO_ARTICLES
            SET Quantite = ?,
                DateModification = GETDATE()
            WHERE ID = ?
        """, (quantite, article_id))
        
        cursor.connection.commit()
        return True

def delete_article_from_reparation(article_id):
    """
    Supprime un article d'une fiche de réparation
    """
    with get_db_cursor() as cursor:
        cursor.execute("""
            DELETE FROM WEB_GMAO_ARTICLES
            WHERE ID = ?
        """, (article_id,))
        
        cursor.connection.commit()
        return True

def get_articles_by_fiche(id_web_gmao):
    """
    Récupère tous les articles d'une fiche de réparation
    """
    with get_db_cursor() as cursor:
        cursor.execute("""
            SELECT 
                ID,
                ID_GS_ARTICLES,
                Designation_GS_ARTICLES,
                Designation_GS_FAMILLES,
                Designation_GS_TYPES_ARTICLE,
                ID_GS_TYPES_ARTICLE,
                Quantite
            FROM WEB_GMAO_ARTICLES
            WHERE ID_WEB_GMAO = ?
            ORDER BY ID
        """, (id_web_gmao,))
        
        articles = []
        for row in cursor.fetchall():
            articles.append({
                "id": row.ID,
                "id_article": row.ID_GS_ARTICLES,
                "designation": row.Designation_GS_ARTICLES,
                "famille": row.Designation_GS_FAMILLES,
                "type": row.Designation_GS_TYPES_ARTICLE,
                "id_type": row.ID_GS_TYPES_ARTICLE,
                "quantite": float(row.Quantite) if row.Quantite else 0
            })
        
        return articles

def save_articles_for_fiche(id_web_gmao, articles_data):
    """
    Sauvegarde tous les articles d'une fiche et retourne les IDs
    """
    with get_db_cursor() as cursor:
        # Récupérer les articles existants
        cursor.execute("""
            SELECT ID, ID_GS_ARTICLES, Quantite
            FROM WEB_GMAO_ARTICLES
            WHERE ID_WEB_GMAO = ?
        """, (id_web_gmao,))
        
        existing_articles = {row.ID: row for row in cursor.fetchall()}
        existing_ids = set(existing_articles.keys())
        
        # IDs des articles dans la requête
        submitted_db_ids = set()
        saved_articles = []  # Pour retourner les IDs
        
        for art_data in articles_data:
            db_id = art_data.get('db_id')
            id_gs_articles = art_data.get('id_gs_articles')
            quantite = art_data.get('quantite')
            
            if db_id and int(db_id) in existing_ids:
                # Mettre à jour l'article existant
                submitted_db_ids.add(int(db_id))
                cursor.execute("""
                    UPDATE WEB_GMAO_ARTICLES
                    SET ID_GS_ARTICLES = ?,
                        Quantite = ?,
                        DateModification = GETDATE()
                    WHERE ID = ?
                """, (id_gs_articles, quantite, db_id))
                saved_articles.append({
                    'db_id': int(db_id),
                    'id_gs_articles': id_gs_articles,
                    'quantite': quantite
                })
            else:
                # Insérer un nouvel article
                cursor.execute("""
                    INSERT INTO WEB_GMAO_ARTICLES (
                        ID_WEB_GMAO,
                        ID_GS_ARTICLES,
                        Quantite
                    ) VALUES (?, ?, ?)
                """, (id_web_gmao, id_gs_articles, quantite))
                
                # Récupérer l'ID généré
                cursor.execute("SELECT @@IDENTITY AS ID")
                new_id = cursor.fetchone().ID
                
                saved_articles.append({
                    'db_id': int(new_id),
                    'id_gs_articles': id_gs_articles,
                    'quantite': quantite
                })
        
        # Supprimer les articles qui ne sont plus dans la liste
        articles_to_delete = existing_ids - submitted_db_ids
        for art_id in articles_to_delete:
            cursor.execute("DELETE FROM WEB_GMAO_ARTICLES WHERE ID = ?", (art_id,))
        
        cursor.connection.commit()
        return saved_articles

def get_machines_disponibles():
    """Récupère la liste de toutes les machines disponibles depuis GP_POSTES"""
    with get_db_cursor() as cursor:
        cursor.execute("""
            SELECT 
                ID,
                Nom
            FROM GP_POSTES
            WHERE Nom IS NOT NULL AND Archive = 0
            ORDER BY Nom
        """)
        
        machines = []
        for row in cursor.fetchall():
            machines.append({
                "id": row.ID,
                "nom": (row.Nom or '').strip()
            })
        return machines

def get_machines():
    """Récupère la liste des machines/équipements (alias pour compatibilité)"""
    return get_machines_disponibles()
