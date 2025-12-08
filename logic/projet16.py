"""
Projet 16 - GMAO (Gestion de la Maintenance Assistée par Ordinateur)
Gestion des interventions préventives et correctives
"""
from db import get_db_cursor
from datetime import datetime

def convert_datetime_for_sql(dt_str):
    """Convertit un datetime du format ISO (avec T) vers le format SQL Server"""
    if not dt_str:
        return None
    # Remplacer le 'T' par un espace et ajouter :00 pour les secondes si nécessaire
    dt_str = str(dt_str).replace('T', ' ')
    # Supprimer les millisecondes si présentes
    if '.' in dt_str:
        dt_str = dt_str.split('.')[0]
    # Ajouter les secondes si elles manquent
    if len(dt_str) == 16:  # Format 'YYYY-MM-DD HH:MM'
        dt_str += ':00'
    return dt_str

def parse_datetime_safe(dt_str):
    """Parse une date de manière robuste en essayant plusieurs formats"""
    if not dt_str:
        return None
    dt_str = str(dt_str).strip()
    # Formats à essayer
    formats = [
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%d %H:%M',
        '%Y-%m-%dT%H:%M:%S',
        '%Y-%m-%dT%H:%M',
        '%Y-%m-%d %H:%M:%S.%f',
        '%Y-%m-%dT%H:%M:%S.%f'
    ]
    for fmt in formats:
        try:
            return datetime.strptime(dt_str, fmt)
        except ValueError:
            continue
    # Si aucun format ne fonctionne, essayer avec convert_datetime_for_sql puis parser
    try:
        normalized = convert_datetime_for_sql(dt_str)
        if normalized:
            return datetime.strptime(normalized, '%Y-%m-%d %H:%M:%S')
    except:
        pass
    return None

def parse_tpsreel_to_hours(tps_reel_str):
    """
    Parse TpsReel au format hh:mm ou heures décimales et retourne le nombre d'heures décimales
    Exemples:
    - "2:30" -> 2.5
    - "0:25" -> 0.416666...
    - "2.5" -> 2.5
    """
    if not tps_reel_str:
        return None
    tps_reel_str = str(tps_reel_str).strip()
    
    # Si c'est au format hh:mm
    if ':' in tps_reel_str:
        try:
            parts = tps_reel_str.split(':')
            if len(parts) == 2:
                hours = int(parts[0])
                minutes = int(parts[1])
                return hours + (minutes / 60.0)
        except (ValueError, IndexError):
            pass
    
    # Sinon, essayer de convertir en float (heures décimales)
    try:
        return float(tps_reel_str)
    except ValueError:
        return None

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
        
        # Insérer la demande d'intervention avec ou sans Suffixe selon l'existence de la colonne
        try:
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
                    Suffixe,
                    DateCreation,
                    DateModification
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, 0, 0, GETDATE(), GETDATE())
            """, (
                'C',  # Code = 'C' pour Corrective
                convert_datetime_for_sql(data.get('dte_dem_in')),
                data.get('matr_op_dem'),
                oper_dem,
                id_emach,  # 0=Sans Arrêt, 1=Avec Arrêt
                postes_reel,
                data.get('dem_in', '')
            ))
        except Exception as e:
            # Si la colonne Suffixe n'existe pas, faire l'INSERT sans Suffixe
            print(f"[WARNING] Colonne Suffixe non trouvée, INSERT sans Suffixe: {e}")
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
        
        # Vérifier si la colonne Suffixe existe et l'incrémenter si elle existe
        try:
            cursor.execute("SELECT ISNULL(Suffixe, 0) as Suffixe FROM WEB_GMAO WHERE ID = ?", (demande_id,))
            suffixe_row = cursor.fetchone()
            nouveau_suffixe = (suffixe_row.Suffixe if suffixe_row else 0) + 1
            
            # Mettre à jour la demande d'intervention avec incrémentation du Suffixe
            cursor.execute("""
                UPDATE WEB_GMAO SET
                    DteDemIn = ?,
                    MatrOpDem = ?,
                    OperDem = ?,
                    ID_EMach = ?,
                    PostesReel = ?,
                    DemIn = ?,
                    Suffixe = ?,
                    DateModification = GETDATE()
                WHERE ID = ?
            """, (
                convert_datetime_for_sql(data.get('dte_dem_in')),
                data.get('matr_op_dem'),
                oper_dem,
                id_emach,  # 0=Sans Arrêt, 1=Avec Arrêt
                postes_reel,
                data.get('dem_in', ''),
                nouveau_suffixe,
                demande_id
            ))
        except Exception as e:
            # Si la colonne Suffixe n'existe pas, faire l'UPDATE sans Suffixe
            print(f"[WARNING] Colonne Suffixe non trouvée, UPDATE sans Suffixe: {e}")
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
    Règles de calcul :
    - Si DteFin est saisi manuellement → TpsReel = DteFin - DteDeb
    - Si TpsReel est saisi manuellement et DteFin n'est pas renseigné → DteFin = DteDeb + TpsReel
    - Si DteFin et TpsReel sont tous les deux saisis → prioriser DteFin et recalculer TpsReel
    """
    with get_db_cursor() as cursor:
        # Vérifier que la demande existe dans WEB_GMAO (réparation liée à une demande)
        # ou dans WEB_GMAO_REPARATION (réparation directe)
        cursor.execute("SELECT ID FROM WEB_GMAO WHERE ID = ?", (demande_id,))
        demande_exists = cursor.fetchone()
        
        if not demande_exists:
            # Vérifier si c'est une réparation directe dans WEB_GMAO_REPARATION
            cursor.execute("SELECT ID FROM WEB_GMAO_REPARATION WHERE ID = ?", (demande_id,))
            reparation_directe = cursor.fetchone()
            if not reparation_directe:
                raise ValueError(f"La demande d'ID {demande_id} n'existe pas")
        
        # Récupérer le nom de l'intervenant
        intervenant_nom = None
        mat_inter = data.get('mat_inter')
        # Normaliser mat_inter : chaîne vide -> None
        if mat_inter and str(mat_inter).strip():
            try:
                cursor.execute("""
                    SELECT CONCAT(Nom, ' ', Prenom) as NomComplet
                    FROM personel
                    WHERE Matricule = ?
                """, (str(mat_inter).strip(),))
                
                inter_row = cursor.fetchone()
                intervenant_nom = inter_row.NomComplet if inter_row else None
            except Exception as e:
                print(f"[ERREUR] Erreur lors de la récupération de l'intervenant: {e}")
                intervenant_nom = None
        else:
            mat_inter = None
        
        from datetime import datetime, timedelta
        
        dte_deb_str = convert_datetime_for_sql(data.get('dte_deb'))
        dte_fin_str = data.get('dte_fin')
        tps_reel_value = data.get('tps_reel')
        
        # Normaliser les valeurs vides (chaînes vides -> None)
        if dte_fin_str == '' or (dte_fin_str and not dte_fin_str.strip()):
            dte_fin_str = None
        if tps_reel_value == '' or (tps_reel_value is not None and str(tps_reel_value).strip() == ''):
            tps_reel_value = None
        
        dte_fin = None
        tps_reel = None
        
        # Vérifier que dte_deb_str est valide avant de faire les calculs
        if not dte_deb_str:
            raise ValueError("DteDeb est obligatoire pour mettre à jour une réparation")
        
        # Règle 1 : Si DteFin est saisi manuellement, calculer TpsReel = DteFin - DteDeb
        if dte_fin_str and dte_fin_str.strip():
            dte_fin = convert_datetime_for_sql(dte_fin_str)
            # Calculer TpsReel à partir de DteFin et DteDeb
            if dte_fin:
                try:
                    dte_deb = parse_datetime_safe(dte_deb_str)
                    dte_fin_dt = parse_datetime_safe(dte_fin)
                    if dte_deb and dte_fin_dt and dte_fin_dt > dte_deb:
                        diff = dte_fin_dt - dte_deb
                        tps_reel = diff.total_seconds() / 3600  # En heures décimales
                    else:
                        tps_reel = None
                except Exception as e:
                    print(f"[ERREUR] Erreur lors du calcul de TpsReel à partir de DteFin: {e}")
                    import traceback
                    traceback.print_exc()
                    tps_reel = None
        # Règle 2 : Si TpsReel est saisi et DteFin n'est pas renseigné, calculer DteFin = DteDeb + TpsReel
        elif tps_reel_value and str(tps_reel_value).strip():
            try:
                tps_reel = parse_tpsreel_to_hours(tps_reel_value)
                if tps_reel and tps_reel > 0:
                    dte_deb = parse_datetime_safe(dte_deb_str)
                    if dte_deb:
                        dte_fin_dt = dte_deb + timedelta(hours=tps_reel)
                        dte_fin = dte_fin_dt.strftime('%Y-%m-%d %H:%M:%S')
                    else:
                        tps_reel = None
                        dte_fin = None
                else:
                    tps_reel = None
            except Exception as e:
                print(f"[ERREUR] Erreur lors du calcul de DteFin à partir de TpsReel: {e}")
                import traceback
                traceback.print_exc()
                tps_reel = None
                dte_fin = None
        
        id_stat_rep = data.get('id_stat_rep', 0)
        
        # Déterminer si c'est une réparation liée à une demande ou une réparation directe
        is_reparation_directe = not demande_exists
        
        # Déterminer PostesReel : si ID_WEB_GMAO_Dem_In est renseigné, copier depuis WEB_GMAO, sinon utiliser la valeur saisie
        postes_reel_value = data.get('postes_reel', '')
        if demande_exists:
            # Si c'est une réparation liée à une demande, copier PostesReel depuis WEB_GMAO
            cursor.execute("SELECT PostesReel FROM WEB_GMAO WHERE ID = ?", (demande_id,))
            demande_row = cursor.fetchone()
            if demande_row and demande_row.PostesReel:
                postes_reel_value = demande_row.PostesReel
        
        print(f"[DEBUG] Valeurs avant UPDATE: dte_deb_str={dte_deb_str}, dte_fin={dte_fin}, mat_inter={data.get('mat_inter')}, intervenant_nom={intervenant_nom}, postes_reel={postes_reel_value}, nat={data.get('nat')}, id_stat_rep={id_stat_rep}, tps_reel={tps_reel}, is_reparation_directe={is_reparation_directe}")
        
        if is_reparation_directe:
            # C'est une réparation directe : mettre à jour directement dans WEB_GMAO_REPARATION par ID
            cursor.execute("SELECT ID FROM WEB_GMAO_REPARATION WHERE ID = ?", (demande_id,))
            reparation_existante = cursor.fetchone()
            
            if reparation_existante:
                # Mettre à jour la réparation directe existante
                try:
                    cursor.execute("""
                        UPDATE WEB_GMAO_REPARATION SET
                            DteDeb = ?,
                            DteFin = ?,
                            MatInter = ?,
                            Intervenant = ?,
                            PostesReel = ?,
                            Nat = ?,
                            ID_StatRep = ?,
                            DateModification = GETDATE()
                        WHERE ID = ?
                    """, (
                        dte_deb_str,
                        dte_fin,
                        mat_inter,
                        intervenant_nom,
                        postes_reel_value,
                        data.get('nat', 'Mec'),
                        id_stat_rep,
                        demande_id
                    ))
                    print(f"[DEBUG] UPDATE réparation directe dans WEB_GMAO_REPARATION exécuté avec succès")
                except Exception as e:
                    print(f"[ERREUR] Erreur lors de l'UPDATE réparation directe dans WEB_GMAO_REPARATION: {e}")
                    import traceback
                    traceback.print_exc()
                    raise
            else:
                raise ValueError(f"La réparation directe d'ID {demande_id} n'existe pas dans WEB_GMAO_REPARATION")
        else:
            # C'est une réparation liée à une demande : chercher par ID_WEB_GMAO_Dem_In
            cursor.execute("SELECT ID FROM WEB_GMAO_REPARATION WHERE ID_WEB_GMAO_Dem_In = ?", (demande_id,))
            reparation_existante = cursor.fetchone()
            
            if reparation_existante:
                # Mettre à jour la réparation existante dans WEB_GMAO_REPARATION
                try:
                    cursor.execute("""
                        UPDATE WEB_GMAO_REPARATION SET
                            DteDeb = ?,
                            DteFin = ?,
                            MatInter = ?,
                            Intervenant = ?,
                            PostesReel = ?,
                            Nat = ?,
                            ID_StatRep = ?,
                            DateModification = GETDATE()
                        WHERE ID_WEB_GMAO_Dem_In = ?
                    """, (
                        dte_deb_str,
                        dte_fin,
                        mat_inter,
                        intervenant_nom,
                        postes_reel_value,
                        data.get('nat', 'Mec'),
                        id_stat_rep,
                        demande_id
                    ))
                    print(f"[DEBUG] UPDATE dans WEB_GMAO_REPARATION exécuté avec succès")
                except Exception as e:
                    print(f"[ERREUR] Erreur lors de l'UPDATE dans WEB_GMAO_REPARATION: {e}")
                    import traceback
                    traceback.print_exc()
                    raise
            else:
                # Créer une nouvelle réparation dans WEB_GMAO_REPARATION
                try:
                    cursor.execute("""
                        INSERT INTO WEB_GMAO_REPARATION (
                            DteDeb, DteFin, MatInter, Intervenant, PostesReel, Nat, ID_StatRep,
                            ID_WEB_GMAO_Dem_In, DateCreation, DateModification
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, GETDATE(), GETDATE())
                    """, (
                        dte_deb_str,
                        dte_fin,
                        mat_inter,
                        intervenant_nom,
                        postes_reel_value,
                        data.get('nat', 'Mec'),
                        id_stat_rep,
                        demande_id
                    ))
                    print(f"[DEBUG] INSERT dans WEB_GMAO_REPARATION exécuté avec succès")
                except Exception as e:
                    print(f"[ERREUR] Erreur lors de l'INSERT dans WEB_GMAO_REPARATION: {e}")
                    import traceback
                    traceback.print_exc()
                    raise
        
        # Note: TpsReel est une colonne calculée dans SQL Server, elle sera automatiquement
        # calculée à partir de DteDeb et DteFin. Pas besoin de la mettre à jour manuellement.
        
        try:
            cursor.connection.commit()
            print(f"[DEBUG] Commit réussi")
        except Exception as e:
            print(f"[ERREUR] Erreur lors du commit: {e}")
            import traceback
            traceback.print_exc()
            raise
        
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
        
        # Gérer DteFin et TpsReel selon les règles :
        # - Si DteFin est saisi manuellement → TpsReel = DteFin - DteDeb
        # - Si TpsReel est saisi manuellement et DteFin n'est pas renseigné → DteFin = DteDeb + TpsReel
        # - Si DteFin et TpsReel sont tous les deux saisis → prioriser DteFin et recalculer TpsReel
        from datetime import datetime, timedelta
        
        dte_deb_str = convert_datetime_for_sql(data.get('dte_deb'))
        dte_fin_str = data.get('dte_fin')
        tps_reel_value = data.get('tps_reel')
        
        dte_fin = None
        tps_reel = None
        
        # Règle 1 : Si DteFin est saisi manuellement, calculer TpsReel = DteFin - DteDeb
        if dte_fin_str and dte_fin_str.strip():
            dte_fin = convert_datetime_for_sql(dte_fin_str)
            # Calculer TpsReel à partir de DteFin et DteDeb
            try:
                dte_deb = parse_datetime_safe(dte_deb_str)
                dte_fin_dt = parse_datetime_safe(dte_fin)
                if dte_deb and dte_fin_dt and dte_fin_dt > dte_deb:
                    diff = dte_fin_dt - dte_deb
                    tps_reel = diff.total_seconds() / 3600  # En heures décimales
                else:
                    tps_reel = None
            except Exception as e:
                print(f"[ERREUR] Erreur lors du calcul de TpsReel à partir de DteFin dans create_reparation_direct: {e}")
                import traceback
                traceback.print_exc()
                tps_reel = None
        # Règle 2 : Si TpsReel est saisi et DteFin n'est pas renseigné, calculer DteFin = DteDeb + TpsReel
        elif tps_reel_value:
            try:
                tps_reel = float(tps_reel_value)
                dte_deb = parse_datetime_safe(dte_deb_str)
                if dte_deb:
                    dte_fin_dt = dte_deb + timedelta(hours=tps_reel)
                    dte_fin = dte_fin_dt.strftime('%Y-%m-%d %H:%M:%S')
                else:
                    tps_reel = None
                    dte_fin = None
            except Exception as e:
                print(f"[ERREUR] Erreur lors du calcul de DteFin à partir de TpsReel dans create_reparation_direct: {e}")
                import traceback
                traceback.print_exc()
                tps_reel = None
                dte_fin = None
        
        id_stat_rep = data.get('id_stat_rep', 0)
        
        # Pour les réparations directes, NE PAS créer de ligne dans WEB_GMAO
        # Insérer directement dans WEB_GMAO_REPARATION avec ID_WEB_GMAO_Dem_In = NULL
        cursor.execute("""
            INSERT INTO WEB_GMAO_REPARATION (
                DteDeb, DteFin, MatInter, Intervenant, PostesReel, Nat, ID_StatRep,
                ID_WEB_GMAO_Dem_In, DateCreation, DateModification
            ) VALUES (?, ?, ?, ?, ?, ?, ?, NULL, GETDATE(), GETDATE())
        """, (
            dte_deb_str,
            dte_fin,
            data.get('mat_inter'),
            intervenant_nom,
            data.get('postes_reel', ''),
            data.get('nat', 'Mec'),
            id_stat_rep
        ))
        
        # Récupérer l'ID généré dans WEB_GMAO_REPARATION
        cursor.execute("SELECT @@IDENTITY AS ID")
        reparation_id = cursor.fetchone().ID
        
        # Retourner l'ID de WEB_GMAO_REPARATION pour que les articles puissent y être liés
        # via ID_WEB_GMAO_REPARATION
        new_id = reparation_id
        
        # Note: TpsReel est une colonne calculée dans SQL Server, elle sera automatiquement
        # calculée à partir de DteDeb et DteFin. Pas besoin de la mettre à jour manuellement.
        
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
        
        # Gérer DteFin et TpsReel selon les règles :
        # - Si DteFin est saisi manuellement → TpsReel = DteFin - DteDeb
        # - Si TpsReel est saisi manuellement et DteFin n'est pas renseigné → DteFin = DteDeb + TpsReel
        # - Si DteFin et TpsReel sont tous les deux saisis → prioriser DteFin et recalculer TpsReel
        from datetime import datetime, timedelta
        
        dte_deb_str = convert_datetime_for_sql(data.get('dte_deb'))
        dte_fin_str = data.get('dte_fin')
        tps_reel_value = data.get('tps_reel')
        
        dte_fin = None
        tps_reel = None
        
        # Règle 1 : Si DteFin est saisi manuellement, calculer TpsReel = DteFin - DteDeb
        if dte_fin_str and dte_fin_str.strip():
            dte_fin = convert_datetime_for_sql(dte_fin_str)
            # Calculer TpsReel à partir de DteFin et DteDeb
            try:
                dte_deb = parse_datetime_safe(dte_deb_str)
                dte_fin_dt = parse_datetime_safe(dte_fin)
                if dte_deb and dte_fin_dt and dte_fin_dt > dte_deb:
                    diff = dte_fin_dt - dte_deb
                    tps_reel = diff.total_seconds() / 3600  # En heures décimales
                else:
                    tps_reel = None
            except Exception as e:
                print(f"[ERREUR] Erreur lors du calcul de TpsReel à partir de DteFin dans update_reparation_status: {e}")
                import traceback
                traceback.print_exc()
                tps_reel = None
        # Règle 2 : Si TpsReel est saisi et DteFin n'est pas renseigné, calculer DteFin = DteDeb + TpsReel
        elif tps_reel_value:
            try:
                tps_reel = float(tps_reel_value)
                dte_deb = parse_datetime_safe(dte_deb_str)
                if dte_deb:
                    dte_fin_dt = dte_deb + timedelta(hours=tps_reel)
                    dte_fin = dte_fin_dt.strftime('%Y-%m-%d %H:%M:%S')
                else:
                    tps_reel = None
                    dte_fin = None
            except Exception as e:
                print(f"[ERREUR] Erreur lors du calcul de DteFin à partir de TpsReel dans update_reparation_status: {e}")
                import traceback
                traceback.print_exc()
                tps_reel = None
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
        
        # Vérifier si c'est une demande dans WEB_GMAO ou une réparation directe dans WEB_GMAO_REPARATION
        cursor.execute("SELECT ID FROM WEB_GMAO WHERE ID = ?", (demande_id,))
        demande_exists = cursor.fetchone()
        
        is_reparation_directe = not demande_exists
        
        # Déterminer PostesReel : si ID_WEB_GMAO_Dem_In est renseigné, copier depuis WEB_GMAO, sinon utiliser la valeur saisie
        postes_reel_value = data.get('postes_reel', '')
        if demande_exists:
            cursor.execute("SELECT PostesReel FROM WEB_GMAO WHERE ID = ?", (demande_id,))
            demande_row = cursor.fetchone()
            if demande_row and demande_row.PostesReel:
                postes_reel_value = demande_row.PostesReel
        
        if is_reparation_directe:
            # C'est une réparation directe : mettre à jour directement dans WEB_GMAO_REPARATION par ID
            cursor.execute("SELECT ID FROM WEB_GMAO_REPARATION WHERE ID = ?", (demande_id,))
            reparation_existante = cursor.fetchone()
            
            if reparation_existante:
                # Mettre à jour la réparation directe existante
                cursor.execute("""
                    UPDATE WEB_GMAO_REPARATION SET
                        DteDeb = ?,
                        DteFin = ?,
                        MatInter = ?,
                        Intervenant = ?,
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
                    postes_reel_value,
                    data.get('nat', 'Mec'),
                    id_stat_rep,
                    demande_id
                ))
            else:
                raise ValueError(f"La réparation directe d'ID {demande_id} n'existe pas dans WEB_GMAO_REPARATION")
        else:
            # C'est une réparation liée à une demande : chercher par ID_WEB_GMAO_Dem_In
            cursor.execute("SELECT ID FROM WEB_GMAO_REPARATION WHERE ID_WEB_GMAO_Dem_In = ?", (demande_id,))
            reparation_existante = cursor.fetchone()
            
            if reparation_existante:
                # Mettre à jour la réparation existante dans WEB_GMAO_REPARATION
                if id_stat_dem_in_to_set is not None:
                    # Mettre à jour aussi le statut de la demande dans WEB_GMAO
                    cursor.execute("""
                        UPDATE WEB_GMAO SET ID_StatDemIn = ? WHERE ID = ?
                    """, (id_stat_dem_in_to_set, demande_id))
                
                cursor.execute("""
                    UPDATE WEB_GMAO_REPARATION SET
                        DteDeb = ?,
                        DteFin = ?,
                        MatInter = ?,
                        Intervenant = ?,
                        PostesReel = ?,
                        Nat = ?,
                        ID_StatRep = ?,
                        DateModification = GETDATE()
                    WHERE ID_WEB_GMAO_Dem_In = ?
                """, (
                    convert_datetime_for_sql(data.get('dte_deb')),
                    dte_fin,
                    data.get('mat_inter'),
                    intervenant_nom,
                    postes_reel_value,
                    data.get('nat', 'Mec'),
                    id_stat_rep,
                    demande_id
                ))
            else:
                # Créer une nouvelle réparation dans WEB_GMAO_REPARATION
                if id_stat_dem_in_to_set is not None:
                    # Mettre à jour aussi le statut de la demande dans WEB_GMAO
                    cursor.execute("""
                        UPDATE WEB_GMAO SET ID_StatDemIn = ? WHERE ID = ?
                    """, (id_stat_dem_in_to_set, demande_id))
                
                cursor.execute("""
                    INSERT INTO WEB_GMAO_REPARATION (
                        DteDeb, DteFin, MatInter, Intervenant, PostesReel, Nat, ID_StatRep,
                        ID_WEB_GMAO_Dem_In, DateCreation, DateModification
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, GETDATE(), GETDATE())
                """, (
                    convert_datetime_for_sql(data.get('dte_deb')),
                    dte_fin,
                    data.get('mat_inter'),
                    intervenant_nom,
                    postes_reel_value,
                    data.get('nat', 'Mec'),
                    id_stat_rep,
                    demande_id
                ))
        
        # Note: TpsReel est une colonne calculée dans SQL Server, elle sera automatiquement
        # calculée à partir de DteDeb et DteFin. Pas besoin de la mettre à jour manuellement.
        
        cursor.connection.commit()
        return True

def delete_reparation(demande_id):
    """
    Supprime les informations de réparation d'une demande
    RÈGLE IMPORTANTE : Ne JAMAIS supprimer une fiche qui contient des données de demande d'intervention.
    - Si la fiche contient des données de demande d'intervention (OperDem, MatrOpDem, DteDemIn), 
      on remet SEULEMENT les champs de réparation à NULL
    - Si c'est une fiche "En cours" (ID_StatRep = 0) SANS aucune donnée de demande d'intervention, 
      alors on peut supprimer complètement la fiche
    """
    with get_db_cursor() as cursor:
        # Vérifier si la fiche contient des données de demande d'intervention
        cursor.execute("""
            SELECT ID_StatRep, ID_StatDemIn, OperDem, MatrOpDem, DteDemIn, DemIn
            FROM WEB_GMAO 
            WHERE ID = ?
        """, (demande_id,))
        
        row = cursor.fetchone()
        if not row:
            return False  # La fiche n'existe pas
        
        # Vérifier si la fiche contient des données de demande d'intervention
        has_demande_data = (
            row.OperDem is not None and row.OperDem != '' or
            row.MatrOpDem is not None and row.MatrOpDem != '' or
            row.DteDemIn is not None or
            (row.DemIn is not None and row.DemIn != '')
        )
        
        # Vérifier si la table WEB_GMAO_REPARATION existe
        try:
            cursor.execute("""
                SELECT COUNT(*) as table_exists
                FROM INFORMATION_SCHEMA.TABLES
                WHERE TABLE_NAME = 'WEB_GMAO_REPARATION'
            """)
            reparation_table_exists = cursor.fetchone().table_exists > 0
        except Exception as e:
            print(f"[WARNING] Erreur lors de la vérification de la table WEB_GMAO_REPARATION: {e}")
            reparation_table_exists = False
        
        # Si la fiche contient des données de demande d'intervention, on ne supprime JAMAIS la ligne
        # On supprime seulement la réparation depuis WEB_GMAO_REPARATION
        if has_demande_data:
            if reparation_table_exists:
                # Supprimer la réparation depuis WEB_GMAO_REPARATION
                cursor.execute("""
                    DELETE FROM WEB_GMAO_REPARATION
                    WHERE ID_WEB_GMAO_Dem_In = ?
                """, (demande_id,))
            else:
                # Fallback : comportement ancien
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
        else:
            # C'est une réparation directe (sans demande d'intervention)
            if reparation_table_exists:
                # Vérifier si c'est une réparation directe dans WEB_GMAO_REPARATION (ID_WEB_GMAO_Dem_In = NULL)
                cursor.execute("""
                    SELECT ID FROM WEB_GMAO_REPARATION 
                    WHERE ID_WEB_GMAO_Dem_In IS NULL AND ID = ?
                """, (demande_id,))
                reparation_directe = cursor.fetchone()
                
                if reparation_directe:
                    # Supprimer la réparation directe depuis WEB_GMAO_REPARATION
                    cursor.execute("""
                        DELETE FROM WEB_GMAO_REPARATION
                        WHERE ID = ?
                    """, (demande_id,))
                else:
                    # Chercher par ID_WEB_GMAO_Dem_In si la réparation est liée
                    cursor.execute("""
                        DELETE FROM WEB_GMAO_REPARATION
                        WHERE ID_WEB_GMAO_Dem_In = ?
                    """, (demande_id,))
                
                # Supprimer les articles (chercher dans ID_WEB_GMAO_REPARATION pour les réparations directes)
                cursor.execute("""
                    DELETE FROM WEB_GMAO_ARTICLES
                    WHERE ID_WEB_GMAO_REPARATION = ?
                """, (demande_id,))
            else:
                # Fallback : comportement ancien
                if row.ID_StatRep == 0:
                    cursor.execute("""
                        DELETE FROM WEB_GMAO_ARTICLES
                        WHERE ID_WEB_GMAO = ?
                    """, (demande_id,))
                    cursor.execute("DELETE FROM WEB_GMAO WHERE ID = ?", (demande_id,))
                else:
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
                    cursor.execute("""
                        DELETE FROM WEB_GMAO_ARTICLES
                        WHERE ID_WEB_GMAO = ?
                    """, (demande_id,))
        
        cursor.connection.commit()
        return True

def get_all_demandes():
    """Récupère toutes les demandes d'intervention avec tous les détails"""
    with get_db_cursor() as cursor:
        # Vérifier si la colonne Suffixe existe
        try:
            cursor.execute("""
                SELECT COUNT(*) as col_exists
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_NAME = 'WEB_GMAO' AND COLUMN_NAME = 'Suffixe'
            """)
            suffixe_exists = cursor.fetchone().col_exists > 0
        except Exception as e:
            print(f"[WARNING] Erreur lors de la vérification de la colonne Suffixe: {e}")
            suffixe_exists = False
        
        # Vérifier si la table WEB_GMAO_REPARATION existe
        try:
            cursor.execute("""
                SELECT COUNT(*) as table_exists
                FROM INFORMATION_SCHEMA.TABLES
                WHERE TABLE_NAME = 'WEB_GMAO_REPARATION'
            """)
            reparation_table_exists = cursor.fetchone().table_exists > 0
        except Exception as e:
            print(f"[WARNING] Erreur lors de la vérification de la table WEB_GMAO_REPARATION: {e}")
            reparation_table_exists = False
        
        # Construire la requête avec ou sans Suffixe et avec ou sans WEB_GMAO_REPARATION
        if suffixe_exists and reparation_table_exists:
            cursor.execute("""
                SELECT 
                    g.ID,
                    g.Code,
                    g.Suffixe,
                    g.DteDemIn,
                    g.OperDem,
                    g.MatrOpDem,
                    COALESCE(r.PostesReel, g.PostesReel) as PostesReel,
                    g.ID_EMach,
                    g.DemIn,
                    r.Nat as Nat,
                    g.Urg,
                    g.ID_StatDemIn,
                    r.ID_StatRep as ID_StatRep,
                    r.DteDeb as DteDeb,
                    r.DteFin as DteFin,
                    r.TpsReel as TpsReel,
                    r.MatInter as MatInter,
                    r.Intervenant as Internvenant,
                    g.DateCreation,
                    g.DateModification,
                    sd.Designation as StatutDemande,
                    sr.Designation as StatutReparation,
                    em.Designation as TypeArret
                FROM WEB_GMAO g
                LEFT JOIN WEB_GMAO_REPARATION r ON r.ID_WEB_GMAO_Dem_In = g.ID
                LEFT JOIN WEB_GMAO_StatDemIn sd ON g.ID_StatDemIn = sd.ID
                LEFT JOIN WEB_GMAO_StatRep sr ON r.ID_StatRep = sr.ID
                LEFT JOIN WEB_GMAO_EMach em ON g.ID_EMach = em.ID
                WHERE g.Code = 'C'
                ORDER BY g.DateCreation DESC
            """)
        elif suffixe_exists:
            cursor.execute("""
                SELECT 
                    g.ID,
                    g.Code,
                    g.Suffixe,
                    g.DteDemIn,
                    g.OperDem,
                    g.MatrOpDem,
                    g.PostesReel,
                    g.ID_EMach,
                    g.DemIn,
                    r.Nat,
                    g.Urg,
                    g.ID_StatDemIn,
                    r.ID_StatRep,
                    r.DteDeb,
                    r.DteFin,
                    r.TpsReel,
                    r.MatInter,
                    r.Intervenant,
                    g.DateCreation,
                    g.DateModification,
                    sd.Designation as StatutDemande,
                    sr.Designation as StatutReparation,
                    em.Designation as TypeArret
                FROM WEB_GMAO g
                LEFT JOIN WEB_GMAO_StatDemIn sd ON g.ID_StatDemIn = sd.ID
                LEFT JOIN WEB_GMAO_StatRep sr ON r.ID_StatRep = sr.ID
                LEFT JOIN WEB_GMAO_EMach em ON g.ID_EMach = em.ID
                WHERE g.Code = 'C'
                ORDER BY g.DateCreation DESC
            """)
        elif reparation_table_exists:
            cursor.execute("""
                SELECT 
                    g.ID,
                    g.Code,
                    0 as Suffixe,
                    g.DteDemIn,
                    g.OperDem,
                    g.MatrOpDem,
                    COALESCE(r.PostesReel, g.PostesReel) as PostesReel,
                    g.ID_EMach,
                    g.DemIn,
                    r.Nat as Nat,
                    g.Urg,
                    g.ID_StatDemIn,
                    r.ID_StatRep as ID_StatRep,
                    r.DteDeb as DteDeb,
                    r.DteFin as DteFin,
                    r.TpsReel as TpsReel,
                    r.MatInter as MatInter,
                    r.Intervenant as Internvenant,
                    g.DateCreation,
                    g.DateModification,
                    sd.Designation as StatutDemande,
                    sr.Designation as StatutReparation,
                    em.Designation as TypeArret
                FROM WEB_GMAO g
                LEFT JOIN WEB_GMAO_REPARATION r ON r.ID_WEB_GMAO_Dem_In = g.ID
                LEFT JOIN WEB_GMAO_StatDemIn sd ON g.ID_StatDemIn = sd.ID
                LEFT JOIN WEB_GMAO_StatRep sr ON r.ID_StatRep = sr.ID
                LEFT JOIN WEB_GMAO_EMach em ON g.ID_EMach = em.ID
                WHERE g.Code = 'C'
                ORDER BY g.DateCreation DESC
            """)
        else:
            # Si WEB_GMAO_REPARATION existe, utiliser cette table
            if reparation_table_exists:
                cursor.execute("""
                    SELECT 
                        g.ID,
                        g.Code,
                        0 as Suffixe,
                        g.DteDemIn,
                        g.OperDem,
                        g.MatrOpDem,
                        COALESCE(r.PostesReel, g.PostesReel) as PostesReel,
                        g.ID_EMach,
                        g.DemIn,
                        r.Nat as Nat,
                        g.Urg,
                        g.ID_StatDemIn,
                        r.ID_StatRep as ID_StatRep,
                        r.DteDeb as DteDeb,
                        r.DteFin as DteFin,
                        r.TpsReel as TpsReel,
                        r.MatInter as MatInter,
                        r.Intervenant as Internvenant,
                        g.DateCreation,
                        g.DateModification,
                        sd.Designation as StatutDemande,
                        sr.Designation as StatutReparation,
                        em.Designation as TypeArret
                    FROM WEB_GMAO g
                    LEFT JOIN WEB_GMAO_REPARATION r ON r.ID_WEB_GMAO_Dem_In = g.ID
                    LEFT JOIN WEB_GMAO_StatDemIn sd ON g.ID_StatDemIn = sd.ID
                    LEFT JOIN WEB_GMAO_StatRep sr ON r.ID_StatRep = sr.ID
                    LEFT JOIN WEB_GMAO_EMach em ON g.ID_EMach = em.ID
                    WHERE g.Code = 'C'
                    ORDER BY g.DateCreation DESC
                """)
            else:
                # Les colonnes ont été supprimées, WEB_GMAO_REPARATION doit exister
                print("⚠️ ERREUR: WEB_GMAO_REPARATION n'existe pas mais les colonnes ont été supprimées de WEB_GMAO!")
                return []
        
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
                "suffixe": row.Suffixe if hasattr(row, 'Suffixe') else 0,
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
        # Vérifier si la colonne Suffixe existe
        try:
            cursor.execute("""
                SELECT COUNT(*) as col_exists
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_NAME = 'WEB_GMAO' AND COLUMN_NAME = 'Suffixe'
            """)
            suffixe_exists = cursor.fetchone().col_exists > 0
        except Exception as e:
            print(f"[WARNING] Erreur lors de la vérification de la colonne Suffixe: {e}")
            suffixe_exists = False
        
        # Vérifier si la table WEB_GMAO_REPARATION existe
        try:
            cursor.execute("""
                SELECT COUNT(*) as table_exists
                FROM INFORMATION_SCHEMA.TABLES
                WHERE TABLE_NAME = 'WEB_GMAO_REPARATION'
            """)
            reparation_table_exists = cursor.fetchone().table_exists > 0
        except Exception as e:
            print(f"[WARNING] Erreur lors de la vérification de la table WEB_GMAO_REPARATION: {e}")
            reparation_table_exists = False
        
        # Construire la requête avec ou sans Suffixe et avec ou sans WEB_GMAO_REPARATION
        if suffixe_exists and reparation_table_exists:
            cursor.execute("""
                SELECT 
                    g.ID, g.Code, g.DteDemIn, g.OperDem, g.MatrOpDem, g.PostesReel, g.ID_EMach, g.DemIn, g.Urg,
                    g.ID_StatDemIn, g.Suffixe,
                    r.DteDeb as DteDeb,
                    r.DteFin as DteFin,
                    r.TpsReel as TpsReel,
                    r.Nat as Nat,
                    r.ID_StatRep as ID_StatRep,
                    r.MatInter as MatInter,
                    r.Intervenant as Internvenant,
                    em.Designation as EtatMachine,
                    sr.Designation as StatutReparation
                FROM WEB_GMAO g
                LEFT JOIN WEB_GMAO_REPARATION r ON r.ID_WEB_GMAO_Dem_In = g.ID
                LEFT JOIN WEB_GMAO_EMach em ON g.ID_EMach = em.ID
                LEFT JOIN WEB_GMAO_StatRep sr ON r.ID_StatRep = sr.ID
                WHERE g.ID = ?
            """, (demande_id,))
        elif suffixe_exists:
            if reparation_table_exists:
                cursor.execute("""
                    SELECT 
                        g.ID, g.Code, g.DteDemIn, g.OperDem, g.MatrOpDem, g.PostesReel, g.ID_EMach, g.DemIn, g.Urg,
                        g.ID_StatDemIn, g.Suffixe,
                        r.DteDeb, r.DteFin, r.TpsReel, r.Nat, r.ID_StatRep, r.MatInter, r.Intervenant,
                        em.Designation as EtatMachine,
                        sr.Designation as StatutReparation
                    FROM WEB_GMAO g
                    LEFT JOIN WEB_GMAO_REPARATION r ON r.ID_WEB_GMAO_Dem_In = g.ID
                    LEFT JOIN WEB_GMAO_EMach em ON g.ID_EMach = em.ID
                    LEFT JOIN WEB_GMAO_StatRep sr ON r.ID_StatRep = sr.ID
                    WHERE g.ID = ?
                """, (demande_id,))
            else:
                # Fallback si WEB_GMAO_REPARATION n'existe pas encore (ne devrait plus être utilisé)
                # Retourner None car les colonnes n'existent plus dans WEB_GMAO
                print("⚠️ ATTENTION: WEB_GMAO_REPARATION n'existe pas mais les colonnes ont été supprimées de WEB_GMAO!")
                return None
        elif reparation_table_exists:
            cursor.execute("""
                SELECT 
                    g.ID, g.Code, g.DteDemIn, g.OperDem, g.MatrOpDem, g.PostesReel, g.ID_EMach, g.DemIn, g.Urg,
                    g.ID_StatDemIn, 0 as Suffixe,
                    r.DteDeb as DteDeb,
                    r.DteFin as DteFin,
                    r.TpsReel as TpsReel,
                    r.Nat as Nat,
                    r.ID_StatRep as ID_StatRep,
                    r.MatInter as MatInter,
                    r.Intervenant as Internvenant,
                    em.Designation as EtatMachine,
                    sr.Designation as StatutReparation
                FROM WEB_GMAO g
                LEFT JOIN WEB_GMAO_REPARATION r ON r.ID_WEB_GMAO_Dem_In = g.ID
                LEFT JOIN WEB_GMAO_EMach em ON g.ID_EMach = em.ID
                LEFT JOIN WEB_GMAO_StatRep sr ON r.ID_StatRep = sr.ID
                WHERE g.ID = ?
            """, (demande_id,))
        else:
            if reparation_table_exists:
                cursor.execute("""
                    SELECT 
                        g.ID, g.Code, g.DteDemIn, g.OperDem, g.MatrOpDem, g.PostesReel, g.ID_EMach, g.DemIn, g.Urg,
                        g.ID_StatDemIn, 0 as Suffixe,
                        r.DteDeb, r.DteFin, r.TpsReel, r.Nat, r.ID_StatRep, r.MatInter, r.Intervenant,
                        em.Designation as EtatMachine,
                        sr.Designation as StatutReparation
                    FROM WEB_GMAO g
                    LEFT JOIN WEB_GMAO_REPARATION r ON r.ID_WEB_GMAO_Dem_In = g.ID
                    LEFT JOIN WEB_GMAO_EMach em ON g.ID_EMach = em.ID
                    LEFT JOIN WEB_GMAO_StatRep sr ON r.ID_StatRep = sr.ID
                    WHERE g.ID = ?
                """, (demande_id,))
            else:
                # Fallback si WEB_GMAO_REPARATION n'existe pas encore (ne devrait plus être utilisé)
                # Retourner None car les colonnes n'existent plus dans WEB_GMAO
                print("⚠️ ATTENTION: WEB_GMAO_REPARATION n'existe pas mais les colonnes ont été supprimées de WEB_GMAO!")
                return None
        
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
            "suffixe": row.Suffixe if hasattr(row, 'Suffixe') else 0,
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
        # Chercher dans ID_WEB_GMAO (réparations liées à une demande) ou ID_WEB_GMAO_REPARATION (réparations directes)
        cursor.execute("""
            SELECT 
                ID,
                ID_GS_ARTICLES,
                Designation_GS_ARTICLES,
                Designation_GS_FAMILLES,
                Designation_GS_TYPES_ARTICLE,
                Quantite
            FROM WEB_GMAO_ARTICLES
            WHERE ID_WEB_GMAO = ? OR ID_WEB_GMAO_REPARATION IN (
                SELECT ID FROM WEB_GMAO_REPARATION WHERE ID_WEB_GMAO_Dem_In = ?
            )
            ORDER BY ID
        """, (demande_id, demande_id))
        
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

def add_article_to_reparation(id_web_gmao=None, id_web_gmao_reparation=None, id_gs_articles=None, quantite=None):
    """
    Ajoute un article à une fiche de réparation
    Soit id_web_gmao (réparation liée à une demande) soit id_web_gmao_reparation (réparation directe) doit être fourni
    """
    if not id_web_gmao and not id_web_gmao_reparation:
        raise ValueError("Soit id_web_gmao soit id_web_gmao_reparation doit être fourni")
    if not id_gs_articles or quantite is None:
        raise ValueError("id_gs_articles et quantite sont obligatoires")
    
    with get_db_cursor() as cursor:
        if id_web_gmao_reparation:
            # Réparation directe : utiliser ID_WEB_GMAO_REPARATION
            cursor.execute("""
                INSERT INTO WEB_GMAO_ARTICLES (
                    ID_WEB_GMAO_REPARATION,
                    ID_GS_ARTICLES,
                    Quantite
                ) VALUES (?, ?, ?)
            """, (id_web_gmao_reparation, id_gs_articles, quantite))
        else:
            # Réparation liée à une demande : utiliser ID_WEB_GMAO
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

def get_articles_by_fiche(id_web_gmao=None, id_web_gmao_reparation=None):
    """
    Récupère tous les articles d'une fiche de réparation
    Soit id_web_gmao (réparation liée à une demande) soit id_web_gmao_reparation (réparation directe) doit être fourni
    """
    if not id_web_gmao and not id_web_gmao_reparation:
        raise ValueError("Soit id_web_gmao soit id_web_gmao_reparation doit être fourni")
    
    with get_db_cursor() as cursor:
        if id_web_gmao_reparation:
            # Réparation directe : chercher dans ID_WEB_GMAO_REPARATION
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
                WHERE ID_WEB_GMAO_REPARATION = ?
                ORDER BY ID
            """, (id_web_gmao_reparation,))
        else:
            # Réparation liée à une demande : chercher dans ID_WEB_GMAO
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

def save_articles_for_fiche(id_web_gmao=None, id_web_gmao_reparation=None, articles_data=None):
    """
    Sauvegarde tous les articles d'une fiche et retourne les IDs
    Soit id_web_gmao (réparation liée à une demande) soit id_web_gmao_reparation (réparation directe) doit être fourni
    """
    if not id_web_gmao and not id_web_gmao_reparation:
        raise ValueError("Soit id_web_gmao soit id_web_gmao_reparation doit être fourni")
    if not articles_data:
        articles_data = []
    
    with get_db_cursor() as cursor:
        # Récupérer les articles existants
        if id_web_gmao_reparation:
            cursor.execute("""
                SELECT ID, ID_GS_ARTICLES, Quantite
                FROM WEB_GMAO_ARTICLES
                WHERE ID_WEB_GMAO_REPARATION = ?
            """, (id_web_gmao_reparation,))
        else:
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
                if id_web_gmao_reparation:
                    cursor.execute("""
                        INSERT INTO WEB_GMAO_ARTICLES (
                            ID_WEB_GMAO_REPARATION,
                            ID_GS_ARTICLES,
                            Quantite
                        ) VALUES (?, ?, ?)
                    """, (id_web_gmao_reparation, id_gs_articles, quantite))
                else:
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
