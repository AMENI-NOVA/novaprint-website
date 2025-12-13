"""
Routes pour le Projet 18 - Agenda semainier 2026
"""
from flask import Blueprint, render_template, make_response
from pathlib import Path
from logic.projet18 import get_semaines_2026, is_jour_ferie, get_nom_jour_ferie, get_mois_nom
from datetime import datetime, timedelta
from io import BytesIO

projet18_bp = Blueprint('projet18', __name__, url_prefix='/projet18')

@projet18_bp.route('/')
def index():
    """Page principale affichant l'agenda semainier"""
    semaines = get_semaines_2026()
    
    return render_template(
        'projet18.html',
        semaines=semaines,
        is_jour_ferie=is_jour_ferie,
        get_nom_jour_ferie=get_nom_jour_ferie,
        get_mois_nom=get_mois_nom
    )

@projet18_bp.route('/export-pdf')
def export_pdf():
    """Exporte l'agenda semainier en PDF selon le modèle Quo Vadis"""
    import json
    import traceback
    from pathlib import Path
    
    log_path = Path(__file__).parent.parent / '.cursor' / 'debug.log'
    
    try:
        # Log début
        # #region agent log
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps({
                'timestamp': datetime.now().isoformat(),
                'location': 'projet18_routes.py:export_pdf:start',
                'message': 'Debut export PDF',
                'sessionId': 'debug-session',
                'runId': 'run1',
                'hypothesisId': 'A'
            }) + '\n')
        # #endregion
        
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm, mm
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
        from calendar import monthrange
        
        semaines = get_semaines_2026()
        # Limiter à 52 semaines
        semaines = semaines[:52]
        
        # Log nombre de semaines
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps({
                'timestamp': datetime.now().isoformat(),
                'location': 'projet18_routes.py:export_pdf:semaines',
                'message': 'Nombre de semaines',
                'data': {'nb_semaines': len(semaines)},
                'sessionId': 'debug-session',
                'runId': 'run1'
            }) + '\n')
        
        buffer = BytesIO()
        # Format A4 portrait
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,  # Portrait au lieu de landscape
            rightMargin=0.5*cm,
            leftMargin=0.5*cm,
            topMargin=0.5*cm,
            bottomMargin=0.5*cm
        )
        
        styles = getSampleStyleSheet()
        
        # Styles selon le modèle Quo Vadis
        base_style = ParagraphStyle(
            'Base',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#000000'),
            fontName='Helvetica',
            leading=10
        )
        
        # Style pour les noms de jours (anglais/français)
        jour_nom_style = ParagraphStyle(
            'JourNom',
            parent=base_style,
            fontSize=9,
            fontName='Helvetica',
            alignment=TA_LEFT
        )
        
        # Style pour les dates (grand, gras, noir selon l'image)
        date_style = ParagraphStyle(
            'Date',
            parent=base_style,
            fontSize=12,
            fontName='Helvetica-Bold',
            textColor=colors.HexColor('#000000'),  # Noir au lieu de bleu
            alignment=TA_RIGHT
        )
        
        # Style pour les numéros d'heures (gris clair, petit)
        # Utiliser un style qui ne coupe pas les nombres
        heure_style = ParagraphStyle(
            'Heure',
            parent=base_style,
            fontSize=7,
            textColor=colors.HexColor('#999999'),
            alignment=TA_LEFT,
            leading=14
        )
        
        # Style pour les lignes horaires (gris clair)
        ligne_horaire_style = ParagraphStyle(
            'LigneHoraire',
            parent=base_style,
            fontSize=8,
            textColor=colors.HexColor('#CCCCCC'),
            leading=10
        )
        
        # Style pour Dimanche
        dimanche_nom_style = ParagraphStyle(
            'DimancheNom',
            parent=base_style,
            fontSize=9,
            fontName='Helvetica',
            alignment=TA_LEFT
        )
        
        dimanche_date_style = ParagraphStyle(
            'DimancheDate',
            parent=base_style,
            fontSize=12,
            fontName='Helvetica-Bold',
            textColor=colors.HexColor('#000000'),  # Noir au lieu de bleu
            alignment=TA_RIGHT
        )
        
        # Style pour les lignes de notes Dimanche
        ligne_note_style = ParagraphStyle(
            'LigneNote',
            parent=base_style,
            fontSize=8,
            textColor=colors.HexColor('#CCCCCC'),
            leading=14
        )
        
        # Style pour jours fériés
        ferie_style = ParagraphStyle(
            'Ferie',
            parent=base_style,
            fontSize=9,
            textColor=colors.HexColor('#FF0000'),
            fontName='Helvetica-Bold'
        )
        
        # Style pour le mini-calendrier
        cal_header_style = ParagraphStyle(
            'CalHeader',
            parent=base_style,
            fontSize=10,
            fontName='Helvetica-Bold',
            alignment=TA_CENTER
        )
        
        cal_semaine_style = ParagraphStyle(
            'CalSemaine',
            parent=base_style,
            fontSize=7,
            textColor=colors.HexColor('#999999'),
            alignment=TA_LEFT,
            leading=10
        )
        
        cal_date_style = ParagraphStyle(
            'CalDate',
            parent=base_style,
            fontSize=8,
            alignment=TA_CENTER,
            leading=10
        )
        
        elements = []
        
        # Heures de 8h à 20h (13 lignes)
        heures = list(range(8, 21))  # 8, 9, 10, ..., 20
        
        # Générer chaque semaine (2 pages par semaine)
        for semaine in semaines:
            # Calculer le mois de référence pour le mini-calendrier
            date_ref = semaine['jeudi'] if semaine['jeudi'] is not None else semaine['vendredi']
            if date_ref is None:
                date_ref = semaine['samedi'] if semaine['samedi'] is not None else datetime(2026, 1, 1)
            mois_ref = date_ref.month if date_ref else 1
            annee_ref = date_ref.year if date_ref else 2026
            
            # ========== PAGE 1 : LUNDI / MARDI / MERCREDI + DIMANCHE ==========
            page1_data = []
            
            # En-têtes des 3 colonnes (Lundi, Mardi, Mercredi)
            header_row = []
            jours_page1 = [
                ('lundi', 'Monday', 'Lundi'),
                ('mardi', 'Tuesday', 'Mardi'),
                ('mercredi', 'Wednesday', 'Mercredi')
            ]
            
            for jour_key, jour_en, jour_fr in jours_page1:
                date_jour = semaine[jour_key]
                if date_jour is not None:
                    # En-tête : jour à gauche, date à droite sur la même ligne (ex: "lundi 29")
                    # Format avec zéro devant si < 10 (01, 02, 03, 04)
                    date_formatee = f"{date_jour.day:02d}"
                    # Créer un tableau avec jour à gauche et date à droite
                    # #region agent log
                    with open(log_path, 'a', encoding='utf-8') as f:
                        f.write(json.dumps({
                            'timestamp': datetime.now().isoformat(),
                            'location': 'projet18_routes.py:export_pdf:before_header_table_page2',
                            'message': 'Avant creation header_table page2',
                            'data': {'jour': jour_fr, 'date': date_formatee},
                            'sessionId': 'debug-session',
                            'runId': 'run1',
                            'hypothesisId': 'A'
                        }) + '\n')
                    # #endregion
                    try:
                        header_table = Table([
                            [Paragraph(jour_fr, ParagraphStyle(
                                'HeaderJour',
                                parent=base_style,
                                fontSize=15,
                                fontName='Helvetica-Bold',
                                alignment=TA_LEFT
                            )), 
                             Paragraph(date_formatee, ParagraphStyle(
                                'HeaderDate',
                                parent=base_style,
                                fontSize=18,
                                fontName='Helvetica-Bold',
                                textColor=colors.HexColor('#0066CC'),  # Bleu comme dans l'image
                                alignment=TA_RIGHT
                            ))]
                        ], colWidths=[3.5*cm, 2*cm])
                        header_table.setStyle(TableStyle([
                            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
                            ('LEFTPADDING', (0, 0), (-1, -1), 2),
                            ('RIGHTPADDING', (0, 0), (-1, -1), 2),
                            ('TOPPADDING', (0, 0), (-1, -1), 4),
                            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                        ]))
                        # #region agent log
                        with open(log_path, 'a', encoding='utf-8') as f:
                            f.write(json.dumps({
                                'timestamp': datetime.now().isoformat(),
                                'location': 'projet18_routes.py:export_pdf:after_header_table_page2',
                                'message': 'Apres creation header_table page2',
                                'data': {'success': True},
                                'sessionId': 'debug-session',
                                'runId': 'run1',
                                'hypothesisId': 'A'
                            }) + '\n')
                        # #endregion
                    except Exception as e_header:
                        # #region agent log
                        with open(log_path, 'a', encoding='utf-8') as f:
                            f.write(json.dumps({
                                'timestamp': datetime.now().isoformat(),
                                'location': 'projet18_routes.py:export_pdf:error_header_table_page2',
                                'message': 'Erreur creation header_table page2',
                                'data': {'error': str(e_header)},
                                'sessionId': 'debug-session',
                                'runId': 'run1',
                                'hypothesisId': 'A'
                            }) + '\n')
                        # #endregion
                        raise
                    # Créer une table avec header_table (jour+date) et jour férié éventuel
                    # Utiliser une structure qui préserve la disposition horizontale de header_table
                    jour_ferie = is_jour_ferie(date_jour)
                    if jour_ferie:
                        nom_ferie = get_nom_jour_ferie(date_jour)
                        ferie_para = Paragraph(
                            f"<font color='#FF0000'>{nom_ferie}</font>",
                            ferie_style
                        )
                        # Table avec 2 lignes : header_table en haut, jour férié en bas
                        header_cell = Table(
                            [[header_table], [ferie_para]],
                            colWidths=[5.5*cm]
                        )
                    else:
                        # Table avec seulement header_table
                        header_cell = Table(
                            [[header_table]],
                            colWidths=[5.5*cm]
                        )
                    
                    header_cell.setStyle(TableStyle([
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('LEFTPADDING', (0, 0), (-1, -1), 2),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 2),
                        ('TOPPADDING', (0, 0), (-1, -1), 8),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                    ]))
                    header_row.append(header_cell)
                else:
                    header_row.append(Paragraph("", base_style))
            
            page1_data.append(header_row)
            
            # 13 lignes horaires pour chaque colonne (8h-20h)
            for heure in heures:
                ligne_row = []
                for jour_key, jour_en, jour_fr in jours_page1:
                    date_jour = semaine[jour_key]
                    if date_jour is not None:
                        # Ligne avec numéro d'heure à gauche et deux lignes grises identiques
                        # Créer deux lignes distinctes avec exactement le même nombre de caractères pour garantir une longueur uniforme
                        # Utiliser un nombre de caractères fixe (42) pour remplir la largeur disponible sans retour à la ligne
                        # Créer exactement 2 lignes de longueur adaptée sans retour à la ligne
                        # Utiliser un nombre de caractères réduit pour éviter tout retour à la ligne dans le Paragraph
                        # Environ 30-32 caractères pour une largeur de 4.7cm avec fontSize=8 pour éviter tout débordement
                        ligne_underscore = "_" * 26  # Nombre de caractères très réduit pour garantir qu'il n'y a pas de retour à la ligne et éviter toute ligne supplémentaire
                        # Créer un style spécifique pour empêcher les retours à la ligne
                        ligne_horaire_style_no_wrap = ParagraphStyle(
                            'LigneHoraireNoWrap',
                            parent=ligne_horaire_style,
                            leading=12,  # Leading exactement égal à rowHeights pour garantir exactement 2 lignes sans débordement
                            spaceBefore=0,
                            spaceAfter=0
                        )
                        # Style pour le numéro d'heure aligné avec la première ligne
                        # Utiliser exactement le même leading que la ligne pour un alignement parfait
                        heure_num_style = ParagraphStyle(
                            'HeureNum',
                            parent=base_style,
                            fontSize=7,
                            textColor=colors.HexColor('#999999'),
                            alignment=TA_LEFT,
                            leading=12,  # Exactement le même leading que ligne_horaire_style_no_wrap
                            spaceBefore=0,
                            spaceAfter=0,
                            firstLineIndent=0,
                            leftIndent=0,
                            rightIndent=0
                        )
                        heure_cell = Table(
                            [
                                [Paragraph(str(heure), heure_num_style), Paragraph(ligne_underscore, ligne_horaire_style_no_wrap)],
                                [Paragraph("", base_style), Paragraph(ligne_underscore, ligne_horaire_style_no_wrap)]
                            ],
                            colWidths=[0.6*cm, 4.9*cm],  # Réduire la largeur de la colonne du numéro pour le rapprocher
                            rowHeights=[12, 12]  # Hauteur exactement égale au leading pour garantir exactement 2 lignes sans ligne supplémentaire
                        )
                        heure_cell.setStyle(TableStyle([
                            ('ALIGN', (0, 0), (0, 0), 'RIGHT'),  # Alignement à droite pour le numéro (plus proche de la ligne)
                            ('ALIGN', (1, 0), (1, -1), 'LEFT'),  # Alignement à gauche pour les lignes
                            ('VALIGN', (0, 0), (0, 0), 'TOP'),  # Alignement en haut pour permettre le décalage avec TOPPADDING
                            ('VALIGN', (1, 0), (1, 0), 'BOTTOM'),  # Aligner la première ligne sur sa ligne de base
                            ('VALIGN', (1, 1), (1, 1), 'TOP'),  # Alignement en haut pour la deuxième ligne
                            ('LEFTPADDING', (0, 0), (0, 0), 5),  # Padding à gauche encore augmenté pour décaler davantage le numéro vers la droite
                            ('RIGHTPADDING', (0, 0), (0, 0), 0),  # Pas de padding à droite pour le numéro (très proche de la ligne)
                            ('LEFTPADDING', (1, 0), (1, -1), 0),  # Pas de padding à gauche pour les lignes (très proche du numéro)
                            ('RIGHTPADDING', (1, 0), (1, -1), 2),
                            ('TOPPADDING', (0, 0), (0, 0), 2),  # Padding en haut légèrement augmenté pour descendre très légèrement le numéro
                            ('TOPPADDING', (1, 0), (-1, -1), 0),  # Pas de padding en haut pour les lignes
                            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),  # Pas de padding en bas
                            ('BOTTOMPADDING', (1, 1), (1, 1), 0),  # Pas de padding en bas de la dernière ligne
                        ]))
                        ligne_row.append(heure_cell)
                    else:
                        ligne_row.append(Paragraph("", base_style))
                page1_data.append(ligne_row)
            
            # Mini-calendrier du mois (déplacé de la page 2 vers la page 1)
            # Créer le mini-calendrier avec numéros de semaine
            _, nb_jours_mois = monthrange(annee_ref, mois_ref)
            premier_jour_mois = datetime(annee_ref, mois_ref, 1)
            jour_semaine_premier = premier_jour_mois.weekday()
            
            # Construire le mini-calendrier comme une grille horizontale
            # Structure : une table avec plusieurs lignes
            cal_table_rows = []
            
            # Ligne 1 : En-tête mois/année (sur 8 colonnes : fusionnées)
            cal_table_rows.append([
                Paragraph(f"{get_mois_nom(mois_ref)} {annee_ref}", cal_header_style),
                Paragraph("", base_style), Paragraph("", base_style), Paragraph("", base_style),
                Paragraph("", base_style), Paragraph("", base_style), Paragraph("", base_style), Paragraph("", base_style)
            ])
            
            # Ligne 2 : Abréviations des jours ("lu ma me je ve sa di")
            jours_abrev = ["lu", "ma", "me", "je", "ve", "sa", "di"]
            cal_jours_abrev_row = [Paragraph("", base_style)]  # Espace pour numéro semaine
            for abrev in jours_abrev:
                cal_jours_abrev_row.append(Paragraph(
                    abrev,
                    ParagraphStyle(
                        'CalJoursAbrev',
                        parent=base_style,
                        fontSize=7,
                        alignment=TA_CENTER,
                        leading=10
                    )
                ))
            cal_table_rows.append(cal_jours_abrev_row)
            
            # Créer la grille du calendrier avec numéros de semaine
            semaine_cal = []
            jours_cal = []
            semaine_num_cal = []
            
            # Trouver le numéro de semaine pour chaque jour
            def get_semaine_num_for_date(date_cible):
                for s in semaines:
                    jours_semaine_list = [s['lundi'], s['mardi'], s['mercredi'], s['jeudi'], s['vendredi'], s['samedi'], s['dimanche']]
                    for d in jours_semaine_list:
                        if d and d.date() == date_cible.date():
                            return s['numero']
                return None
            
            # Calculer correctement le positionnement du premier jour du mois
            # Le premier jour doit être à la position jour_semaine_premier (0=lundi, 3=jeudi, etc.)
            
            # Ajouter les dates de décembre avant janvier (si mois_ref == 1)
            if mois_ref == 1:
                mois_precedent = 12
                annee_precedente = annee_ref - 1
                _, nb_jours_decembre = monthrange(annee_precedente, mois_precedent)
                
                # Ajouter les 3 derniers jours de décembre (29, 30, 31)
                for jour_dec in range(29, 32):
                    date_dec = datetime(annee_precedente, mois_precedent, jour_dec)
                    semaine_num = get_semaine_num_for_date(date_dec)
                    semaine_num_cal.append(str(semaine_num) if semaine_num else "")
                    jours_cal.append(f"{jour_dec:02d}")
                
                # Après avoir ajouté 29, 30, 31, on a 3 éléments dans jours_cal
                # Le 29 décembre 2025 est un lundi (weekday=0), donc :
                # - Position 0: 29 (lundi)
                # - Position 1: 30 (mardi)  
                # - Position 2: 31 (mercredi)
                # Le 1er janvier 2026 est un jeudi (weekday=3), donc il doit être à la position 3
                # Comme on a déjà 3 éléments, la prochaine position est 3, ce qui est correct
                # Donc pas besoin d'espaces supplémentaires
                nb_espaces_a_ajouter = 0
                # #region agent log
                with open(log_path, 'a', encoding='utf-8') as f:
                    f.write(json.dumps({
                        'timestamp': datetime.now().isoformat(),
                        'location': 'projet18_routes.py:export_pdf:cal_decembre',
                        'message': 'Jours decembre ajoutes',
                        'data': {
                            'nb_jours_decembre': len(jours_cal),
                            'jour_semaine_premier': jour_semaine_premier,
                            'nb_espaces': nb_espaces_a_ajouter,
                            'jours_cal': jours_cal,
                            'position_apres_decembre': len(jours_cal)
                        },
                        'sessionId': 'debug-session',
                        'runId': 'run1',
                        'hypothesisId': 'F'
                    }) + '\n')
                # #endregion
            else:
                # Pour les autres mois, ajouter simplement les espaces nécessaires
                nb_espaces_a_ajouter = jour_semaine_premier
            
            # Ajouter les espaces nécessaires
            for _ in range(nb_espaces_a_ajouter):
                if len(jours_cal) < 7:  # Ne pas dépasser 7 jours par semaine
                    semaine_num_cal.append("")
                    jours_cal.append("")
            
            # Ajouter les jours du mois courant avec numéro de semaine
            jour_courant = 1
            premier_jour_position = None  # Position du premier jour du mois dans la ligne
            while jour_courant <= nb_jours_mois:
                jour_date = datetime(annee_ref, mois_ref, jour_courant)
                semaine_num = get_semaine_num_for_date(jour_date)
                
                semaine_num_cal.append(str(semaine_num) if semaine_num else "")
                # Format avec zéro devant si < 10
                jours_cal.append(f"{jour_courant:02d}")
                
                # Marquer la position du premier jour du mois dans la ligne actuelle
                if jour_courant == 1:
                    premier_jour_position = len(jours_cal) - 1
                    # #region agent log
                    with open(log_path, 'a', encoding='utf-8') as f:
                        f.write(json.dumps({
                            'timestamp': datetime.now().isoformat(),
                            'location': 'projet18_routes.py:export_pdf:cal_premier_jour',
                            'message': 'Premier jour du mois ajoute',
                            'data': {
                                'jour': jour_courant,
                                'position_dans_ligne': premier_jour_position,
                                'jour_semaine_attendu': jour_semaine_premier,
                                'jours_cal': jours_cal,
                                'len_jours_cal': len(jours_cal)
                            },
                            'sessionId': 'debug-session',
                            'runId': 'run1',
                            'hypothesisId': 'F'
                        }) + '\n')
                    # #endregion
                
                jour_courant += 1
                
                if len(jours_cal) == 7:
                    # Trouver le numéro de semaine pour cette ligne (prendre le premier non vide)
                    semaine_num_ligne = None
                    for sn in semaine_num_cal:
                        if sn:
                            semaine_num_ligne = sn
                            break
                    
                    # Créer une ligne avec numéro de semaine à gauche et dates à droite
                    cal_row_cells = []
                    # Numéro de semaine à gauche (petit, gris)
                    cal_row_cells.append(Paragraph(
                        semaine_num_ligne if semaine_num_ligne else "",
                        cal_semaine_style
                    ))
                    
                    # Dates à droite (7 colonnes)
                    for idx, jour_str in enumerate(jours_cal):
                        # Highlight bleu clair pour le premier jour du mois (01) du mois courant
                        if idx == premier_jour_position and jour_str == "01":
                            # C'est le premier jour du mois courant
                            cal_row_cells.append(Paragraph(
                                jour_str,
                                ParagraphStyle(
                                    'CalDateHighlight',
                                    parent=base_style,
                                    fontSize=8,
                                    textColor=colors.HexColor('#0066CC'),
                                    backColor=colors.HexColor('#E6F3FF'),  # Bleu clair
                                    alignment=TA_CENTER,
                                    leading=10
                                )
                            ))
                            premier_jour_position = None  # Ne highlight qu'une fois
                        else:
                            cal_row_cells.append(Paragraph(jour_str, cal_date_style))
                    
                    # Ajouter la ligne directement à cal_table_rows
                    cal_table_rows.append(cal_row_cells)
                    
                    semaine_cal = []
                    jours_cal = []
                    semaine_num_cal = []
            
            # Compléter la dernière semaine avec le début de février (si nécessaire)
            if len(jours_cal) > 0 and len(jours_cal) < 7:
                mois_suivant = mois_ref + 1 if mois_ref < 12 else 1
                annee_suivante = annee_ref if mois_ref < 12 else annee_ref + 1
                jour_fevrier = 1
                while len(jours_cal) < 7:
                    date_fev = datetime(annee_suivante, mois_suivant, jour_fevrier)
                    semaine_num = get_semaine_num_for_date(date_fev)
                    semaine_num_cal.append(str(semaine_num) if semaine_num else "")
                    jours_cal.append(f"{jour_fevrier:02d}")
                    jour_fevrier += 1
                
                # Créer la dernière ligne avec numéro de semaine à gauche
                # Trouver le numéro de semaine pour cette ligne
                semaine_num_ligne = None
                for sn in semaine_num_cal:
                    if sn:
                        semaine_num_ligne = sn
                        break
                
                cal_row_cells = []
                # Numéro de semaine à gauche
                cal_row_cells.append(Paragraph(
                    semaine_num_ligne if semaine_num_ligne else "",
                    cal_semaine_style
                ))
                
                # Dates à droite
                for jour_str in jours_cal:
                    cal_row_cells.append(Paragraph(jour_str, cal_date_style))
                
                cal_table_rows.append(cal_row_cells)
            
            # Limiter à 6 lignes de dates (en plus de l'en-tête et des abréviations)
            # Total : 1 en-tête + 1 abréviations + 6 lignes dates = 8 lignes max
            if len(cal_table_rows) > 8:
                cal_table_rows = cal_table_rows[:8]
            
            # Créer le tableau du mini-calendrier comme une grille horizontale
            # #region agent log
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps({
                    'timestamp': datetime.now().isoformat(),
                    'location': 'projet18_routes.py:export_pdf:before_cal_table',
                    'message': 'Avant creation cal_table',
                    'data': {'nb_rows': len(cal_table_rows)},
                    'sessionId': 'debug-session',
                    'runId': 'run1',
                    'hypothesisId': 'D'
                }) + '\n')
            # #endregion
            try:
                cal_table = Table(
                    cal_table_rows,
                    colWidths=[0.6*cm] + [0.7*cm] * 7  # Numéro semaine (ajusté) + 7 dates = 8 colonnes
                )
                cal_table.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (0, 0), 'CENTER'),  # En-tête mois centré sur toutes les colonnes
                    ('SPAN', (0, 0), (-1, 0)),  # Fusionner les colonnes pour l'en-tête
                    ('ALIGN', (0, 1), (0, -1), 'LEFT'),  # Numéros de semaine à gauche
                    ('ALIGN', (1, 1), (-1, -1), 'CENTER'),  # Dates et abréviations centrées
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 2),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 2),
                    ('TOPPADDING', (0, 0), (-1, -1), 2),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CCCCCC')),
                ]))
                # #region agent log
                with open(log_path, 'a', encoding='utf-8') as f:
                    f.write(json.dumps({
                        'timestamp': datetime.now().isoformat(),
                        'location': 'projet18_routes.py:export_pdf:after_cal_table',
                        'message': 'Apres creation cal_table',
                        'data': {'success': True},
                        'sessionId': 'debug-session',
                        'runId': 'run1',
                        'hypothesisId': 'D'
                    }) + '\n')
                # #endregion
            except Exception as e_cal_table:
                # #region agent log
                with open(log_path, 'a', encoding='utf-8') as f:
                    f.write(json.dumps({
                        'timestamp': datetime.now().isoformat(),
                        'location': 'projet18_routes.py:export_pdf:error_cal_table',
                        'message': 'Erreur creation cal_table',
                        'data': {'error': str(e_cal_table), 'nb_rows': len(cal_table_rows)},
                        'sessionId': 'debug-session',
                        'runId': 'run1',
                        'hypothesisId': 'D'
                    }) + '\n')
                # #endregion
                raise
            
            # Ajouter la ligne avec mini-calendrier à gauche
            cal_row = [
                cal_table,  # Mini-calendrier colonne 1 (à gauche)
                Paragraph("", base_style),  # Espace vide colonne 2
                Paragraph("", base_style)  # Espace vide colonne 3
            ]
            page1_data.append(cal_row)
            
            # Trouver l'index de la ligne du mini-calendrier (dernière ligne)
            cal_row_index = len(page1_data) - 1
            
            # Créer le tableau pour la page 1 (format portrait - colonnes plus étroites)
            page1_table = Table(page1_data, colWidths=[5.5*cm, 5.5*cm, 5.5*cm])
            page1_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CCCCCC')),  # Bordures grises fines
                ('LINEBELOW', (0, 0), (-1, 0), 1, colors.HexColor('#CCCCCC')),  # Ligne sous les en-têtes
                # Supprimer la ligne verticale entre Mardi (colonne 1) et Mercredi (colonne 2) uniquement pour la ligne du mini-calendrier
                ('LINEAFTER', (1, cal_row_index), (1, cal_row_index), 0, colors.white),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ]))
            
            elements.append(page1_table)
            elements.append(PageBreak())
            
            # ========== PAGE 2 : JEUDI / VENDREDI / SAMEDI + DIMANCHE ==========
            page2_data = []
            
            # En-têtes des 3 colonnes (Jeudi, Vendredi, Samedi)
            header_row2 = []
            jours_page2 = [
                ('jeudi', 'Thursday', 'Jeudi'),
                ('vendredi', 'Friday', 'Vendredi'),
                ('samedi', 'Saturday', 'Samedi')
            ]
            
            for jour_key, jour_en, jour_fr in jours_page2:
                date_jour = semaine[jour_key]
                if date_jour is not None:
                    # En-tête : jour à gauche, date à droite sur la même ligne (ex: "jeudi 01")
                    # Format avec zéro devant si < 10 (01, 02, 03, 04)
                    date_formatee = f"{date_jour.day:02d}"
                    # Créer un tableau avec jour à gauche et date à droite
                    # #region agent log
                    with open(log_path, 'a', encoding='utf-8') as f:
                        f.write(json.dumps({
                            'timestamp': datetime.now().isoformat(),
                            'location': 'projet18_routes.py:export_pdf:before_header_table_page2',
                            'message': 'Avant creation header_table page2',
                            'data': {'jour': jour_fr, 'date': date_formatee},
                            'sessionId': 'debug-session',
                            'runId': 'run1',
                            'hypothesisId': 'A'
                        }) + '\n')
                    # #endregion
                    try:
                        header_table = Table([
                            [Paragraph(jour_fr, ParagraphStyle(
                                'HeaderJour',
                                parent=base_style,
                                fontSize=15,
                                fontName='Helvetica-Bold',
                                alignment=TA_LEFT
                            )), 
                             Paragraph(date_formatee, ParagraphStyle(
                                'HeaderDate',
                                parent=base_style,
                                fontSize=18,
                                fontName='Helvetica-Bold',
                                textColor=colors.HexColor('#0066CC'),  # Bleu comme dans l'image
                                alignment=TA_RIGHT
                            ))]
                        ], colWidths=[3.5*cm, 2*cm])
                        header_table.setStyle(TableStyle([
                            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
                            ('LEFTPADDING', (0, 0), (-1, -1), 2),
                            ('RIGHTPADDING', (0, 0), (-1, -1), 2),
                            ('TOPPADDING', (0, 0), (-1, -1), 4),
                            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                        ]))
                        # #region agent log
                        with open(log_path, 'a', encoding='utf-8') as f:
                            f.write(json.dumps({
                                'timestamp': datetime.now().isoformat(),
                                'location': 'projet18_routes.py:export_pdf:after_header_table_page2',
                                'message': 'Apres creation header_table page2',
                                'data': {'success': True},
                                'sessionId': 'debug-session',
                                'runId': 'run1',
                                'hypothesisId': 'A'
                            }) + '\n')
                        # #endregion
                    except Exception as e_header:
                        # #region agent log
                        with open(log_path, 'a', encoding='utf-8') as f:
                            f.write(json.dumps({
                                'timestamp': datetime.now().isoformat(),
                                'location': 'projet18_routes.py:export_pdf:error_header_table_page2',
                                'message': 'Erreur creation header_table page2',
                                'data': {'error': str(e_header)},
                                'sessionId': 'debug-session',
                                'runId': 'run1',
                                'hypothesisId': 'A'
                            }) + '\n')
                        # #endregion
                        raise
                    # Créer une table avec header_table (jour+date) et jour férié éventuel
                    # Utiliser une structure qui préserve la disposition horizontale de header_table
                    jour_ferie = is_jour_ferie(date_jour)
                    if jour_ferie:
                        nom_ferie = get_nom_jour_ferie(date_jour)
                        ferie_para = Paragraph(
                            f"<font color='#FF0000'>{nom_ferie}</font>",
                            ferie_style
                        )
                        # Table avec 2 lignes : header_table en haut, jour férié en bas
                        header_cell = Table(
                            [[header_table], [ferie_para]],
                            colWidths=[5.5*cm]
                        )
                    else:
                        # Table avec seulement header_table
                        header_cell = Table(
                            [[header_table]],
                            colWidths=[5.5*cm]
                        )
                    
                    header_cell.setStyle(TableStyle([
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('LEFTPADDING', (0, 0), (-1, -1), 2),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 2),
                        ('TOPPADDING', (0, 0), (-1, -1), 8),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                    ]))
                    header_row2.append(header_cell)
                else:
                    header_row2.append(Paragraph("", base_style))
            
            page2_data.append(header_row2)
            
            # 13 lignes horaires pour chaque colonne (8h-20h)
            for heure in heures:
                ligne_row = []
                for jour_key, jour_en, jour_fr in jours_page2:
                    date_jour = semaine[jour_key]
                    if date_jour is not None:
                        # Ligne avec numéro d'heure à gauche et deux lignes grises identiques
                        # Créer deux lignes distinctes avec exactement le même nombre de caractères pour garantir une longueur uniforme
                        # Utiliser un nombre de caractères fixe (42) pour remplir la largeur disponible sans retour à la ligne
                        # Créer exactement 2 lignes de longueur adaptée sans retour à la ligne
                        # Utiliser un nombre de caractères réduit pour éviter tout retour à la ligne dans le Paragraph
                        # Environ 30-32 caractères pour une largeur de 4.7cm avec fontSize=8 pour éviter tout débordement
                        ligne_underscore = "_" * 26  # Nombre de caractères très réduit pour garantir qu'il n'y a pas de retour à la ligne et éviter toute ligne supplémentaire
                        # Créer un style spécifique pour empêcher les retours à la ligne
                        ligne_horaire_style_no_wrap = ParagraphStyle(
                            'LigneHoraireNoWrap',
                            parent=ligne_horaire_style,
                            leading=12,  # Leading exactement égal à rowHeights pour garantir exactement 2 lignes sans débordement
                            spaceBefore=0,
                            spaceAfter=0
                        )
                        # Style pour le numéro d'heure aligné avec la première ligne
                        # Utiliser exactement le même leading que la ligne pour un alignement parfait
                        heure_num_style = ParagraphStyle(
                            'HeureNum',
                            parent=base_style,
                            fontSize=7,
                            textColor=colors.HexColor('#999999'),
                            alignment=TA_LEFT,
                            leading=12,  # Exactement le même leading que ligne_horaire_style_no_wrap
                            spaceBefore=0,
                            spaceAfter=0,
                            firstLineIndent=0,
                            leftIndent=0,
                            rightIndent=0
                        )
                        heure_cell = Table(
                            [
                                [Paragraph(str(heure), heure_num_style), Paragraph(ligne_underscore, ligne_horaire_style_no_wrap)],
                                [Paragraph("", base_style), Paragraph(ligne_underscore, ligne_horaire_style_no_wrap)]
                            ],
                            colWidths=[0.6*cm, 4.9*cm],  # Réduire la largeur de la colonne du numéro pour le rapprocher
                            rowHeights=[12, 12]  # Hauteur exactement égale au leading pour garantir exactement 2 lignes sans ligne supplémentaire
                        )
                        heure_cell.setStyle(TableStyle([
                            ('ALIGN', (0, 0), (0, 0), 'RIGHT'),  # Alignement à droite pour le numéro (plus proche de la ligne)
                            ('ALIGN', (1, 0), (1, -1), 'LEFT'),  # Alignement à gauche pour les lignes
                            ('VALIGN', (0, 0), (0, 0), 'TOP'),  # Alignement en haut pour permettre le décalage avec TOPPADDING
                            ('VALIGN', (1, 0), (1, 0), 'BOTTOM'),  # Aligner la première ligne sur sa ligne de base
                            ('VALIGN', (1, 1), (1, 1), 'TOP'),  # Alignement en haut pour la deuxième ligne
                            ('LEFTPADDING', (0, 0), (0, 0), 5),  # Padding à gauche encore augmenté pour décaler davantage le numéro vers la droite
                            ('RIGHTPADDING', (0, 0), (0, 0), 0),  # Pas de padding à droite pour le numéro (très proche de la ligne)
                            ('LEFTPADDING', (1, 0), (1, -1), 0),  # Pas de padding à gauche pour les lignes (très proche du numéro)
                            ('RIGHTPADDING', (1, 0), (1, -1), 2),
                            ('TOPPADDING', (0, 0), (0, 0), 2),  # Padding en haut légèrement augmenté pour descendre très légèrement le numéro
                            ('TOPPADDING', (1, 0), (-1, -1), 0),  # Pas de padding en haut pour les lignes
                            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),  # Pas de padding en bas
                            ('BOTTOMPADDING', (1, 1), (1, 1), 0),  # Pas de padding en bas de la dernière ligne
                        ]))
                        ligne_row.append(heure_cell)
                    else:
                        ligne_row.append(Paragraph("", base_style))
                page2_data.append(ligne_row)
            
            # Zone Dimanche : en-tête dans colonne 1, lignes grises dans colonnes 2 et 3 (déplacé de la page 1 vers la page 2)
            dimanche_row = []
            if semaine['dimanche'] is not None:
                jour_ferie = is_jour_ferie(semaine['dimanche'])
                nom_ferie = get_nom_jour_ferie(semaine['dimanche']) if jour_ferie else ""
                
                # Contenu Dimanche : jour + date sur une ligne (ex: "Dimanche 04")
                # Format avec zéro devant si < 10
                date_dimanche_formatee = f"{semaine['dimanche'].day:02d}"
                # Créer un tableau avec jour à gauche et date à droite
                dimanche_header_table = Table([
                    [Paragraph("Dimanche", ParagraphStyle(
                        'DimancheJour',
                        parent=base_style,
                        fontSize=15,
                        fontName='Helvetica-Bold',
                        alignment=TA_LEFT
                    )), 
                     Paragraph(date_dimanche_formatee, ParagraphStyle(
                        'DimancheDate',
                        parent=base_style,
                        fontSize=18,
                        fontName='Helvetica-Bold',
                        textColor=colors.HexColor('#0066CC'),  # Bleu comme dans l'image
                        alignment=TA_RIGHT
                    ))]
                ], colWidths=[3.5*cm, 2*cm])
                dimanche_header_table.setStyle(TableStyle([
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                    ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 2),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 2),
                    ('TOPPADDING', (0, 0), (-1, -1), 4),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ]))
                
                # Colonne 1 : En-tête Dimanche + date (et jour férié si applicable)
                dimanche_header_rows = [[dimanche_header_table]]
                if jour_ferie:
                    dimanche_header_rows.append([Paragraph(
                        f"<b><font color='#FF0000'>{nom_ferie}</font></b>",
                        ferie_style
                    )])
                
                dimanche_header_cell = Table(
                    dimanche_header_rows,
                    colWidths=[5.5*cm]
                )
                dimanche_header_cell.setStyle(TableStyle([
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 2),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 2),
                    ('TOPPADDING', (0, 0), (0, 0), 12),  # Padding pour l'en-tête Dimanche
                    ('BOTTOMPADDING', (0, 0), (0, 0), 12),
                    ('TOPPADDING', (1, 0), (-1, -1), 2),  # Padding pour le jour férié
                    ('BOTTOMPADDING', (1, 0), (-1, -1), 2),
                ]))
                
                # Colonnes 2 et 3 : 5 lignes grises (fusionnées sur 2 colonnes)
                dimanche_notes_rows = []
                for i in range(5):
                    dimanche_notes_rows.append([Paragraph("_" * 60, ligne_note_style)])
                
                dimanche_notes_cell = Table(
                    dimanche_notes_rows,
                    colWidths=[11*cm]  # Largeur de 2 colonnes (5.5cm + 5.5cm)
                )
                dimanche_notes_cell.setStyle(TableStyle([
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 2),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 2),
                    ('TOPPADDING', (0, 0), (-1, -1), 2),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
                ]))
                
                # Structure finale : colonne 0 = en-tête, colonnes 1-2 = lignes grises (fusionnées)
                # Le contenu doit être dans la première colonne du SPAN (colonne 1)
                dimanche_row.append(dimanche_header_cell)  # Colonne 0 (Jeudi)
                dimanche_row.append(dimanche_notes_cell)  # Colonne 1 (Vendredi) - sera fusionnée avec colonne 2
                dimanche_row.append(Paragraph("", base_style))  # Colonne 2 (Samedi) - sera fusionnée avec colonne 1
            else:
                dimanche_row = [Paragraph("", base_style)] * 3
            
            page2_data.append(dimanche_row)
            
            # Créer le tableau pour la page 2 (format portrait - colonnes plus étroites)
            page2_table = Table(page2_data, colWidths=[5.5*cm, 5.5*cm, 5.5*cm])
            # Trouver l'index de la ligne Dimanche (dernière ligne)
            dimanche_row_index = len(page2_data) - 1
            page2_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CCCCCC')),  # Bordures grises fines
                ('LINEBELOW', (0, 0), (-1, 0), 1, colors.HexColor('#CCCCCC')),  # Ligne sous les en-têtes
                # Fusionner les colonnes 1 et 2 (Vendredi et Samedi) pour les lignes grises du Dimanche
                ('SPAN', (1, dimanche_row_index), (2, dimanche_row_index)),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ]))
            
            elements.append(page2_table)
            
            # Log pour debug
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps({
                    'timestamp': datetime.now().isoformat(),
                    'location': 'projet18_routes.py:export_pdf:semaine',
                    'message': 'Semaine generee',
                    'data': {
                        'semaine_num': semaine['numero'],
                        'has_lundi': semaine['lundi'] is not None,
                        'has_jeudi': semaine['jeudi'] is not None,
                        'has_dimanche': semaine['dimanche'] is not None
                    },
                    'sessionId': 'debug-session',
                    'runId': 'run1'
                }) + '\n')
            
            # Saut de page entre les semaines (sauf pour la dernière)
            if semaine != semaines[-1]:
                elements.append(PageBreak())
        
        # Générer le PDF
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps({
                'timestamp': datetime.now().isoformat(),
                'location': 'projet18_routes.py:export_pdf:before_build',
                'message': 'Avant doc.build',
                'data': {'nb_elements': len(elements)},
                'sessionId': 'debug-session',
                'runId': 'run1'
            }) + '\n')
        
        doc.build(elements)
        buffer.seek(0)
        
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps({
                'timestamp': datetime.now().isoformat(),
                'location': 'projet18_routes.py:export_pdf:after_build',
                'message': 'Apres doc.build',
                'data': {'buffer_size': len(buffer.getvalue())},
                'sessionId': 'debug-session',
                'runId': 'run1'
            }) + '\n')
        
        response = make_response(buffer.read())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=agenda_semainier_2026_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
        
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps({
                'timestamp': datetime.now().isoformat(),
                'location': 'projet18_routes.py:export_pdf:success',
                'message': 'PDF genere avec succes',
                'sessionId': 'debug-session',
                'runId': 'run1'
            }) + '\n')
        
        return response
    
    except Exception as e:
        error_msg = str(e)
        error_trace = traceback.format_exc()
        
        # #region agent log
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps({
                'timestamp': datetime.now().isoformat(),
                'location': 'projet18_routes.py:export_pdf:error',
                'message': 'Erreur generation PDF',
                'data': {'error': error_msg, 'traceback': error_trace},
                'sessionId': 'debug-session',
                'runId': 'run1',
                'hypothesisId': 'E'
            }) + '\n')
        # #endregion
        
        raise

@projet18_bp.route('/export-pdf-multilang')
def export_pdf_multilang():
    """Exporte l'agenda semainier en PDF version multilingue (arabe et anglais) - À développer séparément"""
    # NOTE: Cette fonction est une copie indépendante de export_pdf()
    # Elle peut être modifiée pour la version multilingue sans affecter export_pdf()
    # Pour l'instant, elle génère le même PDF que export_pdf() mais avec un nom de fichier différent
    import json
    import traceback
    from pathlib import Path
    
    log_path = Path(__file__).parent.parent / '.cursor' / 'debug.log'
    
    try:
        # Log début
        # #region agent log
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps({
                'timestamp': datetime.now().isoformat(),
                'location': 'projet18_routes.py:export_pdf_multilang:start',
                'message': 'Debut export PDF multilingue',
                'sessionId': 'debug-session',
                'runId': 'run1',
                'hypothesisId': 'A'
            }) + '\n')
        # #endregion
        
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm, mm
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
        from calendar import monthrange
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        import os
        
        # Fonction pour corriger l'ordre du texte arabe (RTL) en préservant les connexions entre lettres
        def fix_arabic_text(text):
            """Corrige l'ordre du texte arabe pour l'affichage RTL dans ReportLab en préservant les connexions"""
            if not text:
                return text
            
            # #region agent log
            try:
                with open(log_path, 'a', encoding='utf-8') as f:
                    f.write(json.dumps({
                        'timestamp': datetime.now().isoformat(),
                        'location': 'projet18_routes.py:fix_arabic_text:start',
                        'message': 'Correction texte arabe',
                        'data': {'text_original': text, 'text_length': len(text)},
                        'sessionId': 'debug-session',
                        'runId': 'run1',
                        'hypothesisId': 'A'
                    }) + '\n')
            except:
                pass
            # #endregion
            
            try:
                # Solution correcte pour ReportLab : reshaper puis inverser pour l'ordre visuel
                # ReportLab affiche le texte dans l'ordre logique (de gauche à droite)
                # Pour l'arabe, il faut inverser l'ordre après le reshaping pour obtenir l'ordre visuel correct
                import arabic_reshaper
                
                # Étape 1: Reshaper pour obtenir les bonnes formes contextuelles (lettres attachées)
                reshaper = arabic_reshaper.ArabicReshaper()
                reshaped_text = reshaper.reshape(text)
                
                # Étape 2: Inverser l'ordre des caractères pour l'affichage visuel RTL
                # ReportLab affiche de gauche à droite, donc on inverse pour obtenir l'ordre RTL correct
                visual_text = reshaped_text[::-1]
                
                # Retourner le texte visual sans marqueur RTL (qui cause des carrés)
                result = visual_text
                
                # #region agent log
                try:
                    with open(log_path, 'a', encoding='utf-8') as f:
                        f.write(json.dumps({
                            'timestamp': datetime.now().isoformat(),
                            'location': 'projet18_routes.py:fix_arabic_text:success',
                            'message': 'Utilise reshape puis inversion (ordre visuel correct pour ReportLab)',
                            'data': {
                                'text_original': text,
                                'text_reshaped': reshaped_text,
                                'text_visual': visual_text,
                                'text_result': result,
                                'length_original': len(text),
                                'length_reshaped': len(reshaped_text),
                                'length_visual': len(visual_text),
                                'length_result': len(result)
                            },
                            'sessionId': 'debug-session',
                            'runId': 'run1',
                            'hypothesisId': 'A'
                        }) + '\n')
                except:
                    pass
                # #endregion
                return result
            except ImportError as e:
                # #region agent log
                try:
                    with open(log_path, 'a', encoding='utf-8') as f:
                        f.write(json.dumps({
                            'timestamp': datetime.now().isoformat(),
                            'location': 'projet18_routes.py:fix_arabic_text:import_error',
                            'message': 'Erreur import bidi/reshaper',
                            'data': {'error': str(e)},
                            'sessionId': 'debug-session',
                            'runId': 'run1',
                            'hypothesisId': 'B'
                        }) + '\n')
                except:
                    pass
                # #endregion
                # Si arabic_reshaper n'est pas disponible, utiliser le texte original
                # La police TTF devrait gérer les formes contextuelles de base
                pass
                
            # Si arabic_reshaper n'est pas disponible, utiliser le texte original sans modification
            # La police TTF devrait gérer les formes contextuelles de base
            has_arabic = any('\u0600' <= c <= '\u06FF' or '\u0750' <= c <= '\u077F' or 
                            '\u08A0' <= c <= '\u08FF' or '\uFB50' <= c <= '\uFDFF' or 
                            '\uFE70' <= c <= '\uFEFF' for c in text)
            if has_arabic:
                # Retourner le texte original sans marqueur RTL (qui cause des carrés)
                # La police TTF (Arial Unicode MS, Tahoma, etc.) devrait gérer les formes contextuelles
                result = text
                # #region agent log
                try:
                    with open(log_path, 'a', encoding='utf-8') as f:
                        f.write(json.dumps({
                            'timestamp': datetime.now().isoformat(),
                            'location': 'projet18_routes.py:fix_arabic_text:fallback',
                            'message': 'Utilise texte original (arabic_reshaper non disponible)',
                            'data': {'text_result': result, 'has_arabic': has_arabic},
                            'sessionId': 'debug-session',
                            'runId': 'run1',
                            'hypothesisId': 'B'
                        }) + '\n')
                except:
                    pass
                # #endregion
                return result
            # #region agent log
            try:
                with open(log_path, 'a', encoding='utf-8') as f:
                    f.write(json.dumps({
                        'timestamp': datetime.now().isoformat(),
                        'location': 'projet18_routes.py:fix_arabic_text:no_arabic',
                        'message': 'Pas de caractères arabes',
                        'data': {'text': text},
                        'sessionId': 'debug-session',
                        'runId': 'run1',
                        'hypothesisId': 'C'
                    }) + '\n')
            except:
                pass
            # #endregion
            return text
        
        # Charger la police Square721 BT (Regular et Bold) pour le texte latin/chiffres
        # ET une police qui supporte l'arabe pour le texte arabe
        square721_font_name = 'Helvetica'  # Par défaut en cas d'erreur
        square721_bold_font_name = 'Helvetica-Bold'  # Par défaut en cas d'erreur
        arabic_font_name = 'Helvetica'  # Par défaut (ne supporte pas l'arabe)
        
        # D'abord charger une police qui supporte l'arabe (priorité)
        try:
            # Essayer Arial Unicode MS (souvent disponible sur Windows et supporte l'arabe)
            arial_unicode_paths = [
                'C:/Windows/Fonts/ARIALUNI.TTF',
                'C:/Windows/Fonts/arialuni.ttf',
                'C:/Windows/Fonts/ARIALUNI.OTF',
            ]
            for path in arial_unicode_paths:
                if os.path.exists(path):
                    try:
                        pdfmetrics.registerFont(TTFont('ArialUnicodeMS', path))
                        arabic_font_name = 'ArialUnicodeMS'
                        break
                    except Exception as e:
                        try:
                            with open(log_path, 'a', encoding='utf-8') as f:
                                f.write(json.dumps({
                                    'timestamp': datetime.now().isoformat(),
                                    'location': 'projet18_routes.py:export_pdf_multilang:arial_unicode_error',
                                    'message': f'Erreur chargement Arial Unicode: {str(e)}',
                                    'path': path,
                                    'sessionId': 'debug-session',
                                    'runId': 'run1'
                                }) + '\n')
                        except:
                            pass
                        pass
            
            # Si Arial Unicode MS n'est pas disponible, essayer Tahoma (supporte l'arabe)
            if arabic_font_name == 'Helvetica':
                tahoma_paths = [
                    'C:/Windows/Fonts/tahoma.ttf',
                    'C:/Windows/Fonts/Tahoma.ttf',
                ]
                for path in tahoma_paths:
                    if os.path.exists(path):
                        try:
                            pdfmetrics.registerFont(TTFont('Tahoma', path))
                            arabic_font_name = 'Tahoma'
                            break
                        except:
                            pass
            
            # Si Tahoma n'est pas disponible, essayer DejaVuSans (supporte l'arabe)
            if arabic_font_name == 'Helvetica':
                dejavu_paths = [
                    'C:/Windows/Fonts/DejaVuSans.ttf',
                    'C:/Windows/Fonts/dejavu-sans.ttf',
                    '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
                    '/usr/share/fonts/TTF/DejaVuSans.ttf'
                ]
                for path in dejavu_paths:
                    if os.path.exists(path):
                        try:
                            pdfmetrics.registerFont(TTFont('DejaVuSans', path))
                            arabic_font_name = 'DejaVuSans'
                            break
                        except:
                            pass
        except Exception as e:
            # En cas d'erreur, utiliser Helvetica (texte arabe ne s'affichera pas correctement)
            arabic_font_name = 'Helvetica'
        
        # Ensuite charger Square721 BT (pour le texte latin/chiffres)
        try:
            # Chemins possibles pour Square721 BT (chercher dans tous les dossiers possibles)
            # Bitstream est l'éditeur de Square721 BT, donc chercher aussi sous ce nom
            square721_paths = [
                'C:/Windows/Fonts/SQUA721N.TTF',  # Square721 BT Normal
                'C:/Windows/Fonts/squa721n.ttf',
                'C:/Windows/Fonts/SQUA721R.TTF',  # Square721 BT Regular
                'C:/Windows/Fonts/squa721r.ttf',
                'C:/Windows/Fonts/SQUA721.TTF',
                'C:/Windows/Fonts/squa721.ttf',
                'C:/Windows/Fonts/SQUA721N.OTF',
                'C:/Windows/Fonts/squa721n.otf',
                # Variantes possibles
                'C:/Windows/Fonts/SQUARE721.TTF',
                'C:/Windows/Fonts/square721.ttf',
                'C:/Windows/Fonts/SQUARE721N.TTF',
                'C:/Windows/Fonts/square721n.ttf',
            ]
            square721_bold_paths = [
                'C:/Windows/Fonts/SQUA721B.TTF',  # Square721 BT Bold
                'C:/Windows/Fonts/squa721b.ttf',
                'C:/Windows/Fonts/SQUA721D.TTF',  # Square721 BT Demi
                'C:/Windows/Fonts/squa721d.ttf',
                'C:/Windows/Fonts/SQUA721B.OTF',
                'C:/Windows/Fonts/squa721b.otf',
                # Variantes possibles
                'C:/Windows/Fonts/SQUARE721B.TTF',
                'C:/Windows/Fonts/square721b.ttf',
                'C:/Windows/Fonts/SQUARE721D.TTF',
                'C:/Windows/Fonts/square721d.ttf',
            ]
            
            # Recherche dynamique dans le dossier Fonts si les chemins standards ne fonctionnent pas
            if square721_font_name == 'Helvetica':
                try:
                    fonts_dir = 'C:/Windows/Fonts'
                    if os.path.exists(fonts_dir):
                        for font_file in os.listdir(fonts_dir):
                            font_lower = font_file.lower()
                            if ('square' in font_lower or 'squa' in font_lower or '721' in font_lower) and (font_lower.endswith('.ttf') or font_lower.endswith('.otf')):
                                if 'bold' not in font_lower and 'demi' not in font_lower and 'b' not in font_lower[-5:]:
                                    font_path = os.path.join(fonts_dir, font_file)
                                    try:
                                        pdfmetrics.registerFont(TTFont('Square721BT', font_path))
                                        square721_font_name = 'Square721BT'
                                        break
                                    except:
                                        pass
                except:
                    pass
            
            if square721_bold_font_name == 'Helvetica-Bold':
                try:
                    fonts_dir = 'C:/Windows/Fonts'
                    if os.path.exists(fonts_dir):
                        for font_file in os.listdir(fonts_dir):
                            font_lower = font_file.lower()
                            if ('square' in font_lower or 'squa' in font_lower or '721' in font_lower) and (font_lower.endswith('.ttf') or font_lower.endswith('.otf')):
                                if 'bold' in font_lower or 'demi' in font_lower or font_lower[-5:-4] == 'b' or font_lower[-5:-4] == 'd':
                                    font_path = os.path.join(fonts_dir, font_file)
                                    try:
                                        pdfmetrics.registerFont(TTFont('Square721BT-Bold', font_path))
                                        square721_bold_font_name = 'Square721BT-Bold'
                                        break
                                    except:
                                        pass
                except:
                    pass
            
            # Charger Square721 BT Regular
            for path in square721_paths:
                if os.path.exists(path):
                    try:
                        pdfmetrics.registerFont(TTFont('Square721BT', path))
                        square721_font_name = 'Square721BT'
                        break
                    except Exception as e:
                        # Log l'erreur pour debug
                        try:
                            with open(log_path, 'a', encoding='utf-8') as f:
                                f.write(json.dumps({
                                    'timestamp': datetime.now().isoformat(),
                                    'location': 'projet18_routes.py:export_pdf_multilang:square721_error',
                                    'message': f'Erreur chargement Square721 BT: {str(e)}',
                                    'path': path,
                                    'sessionId': 'debug-session',
                                    'runId': 'run1'
                                }) + '\n')
                        except:
                            pass
                        pass
            
            # Charger Square721 BT Bold
            for path in square721_bold_paths:
                if os.path.exists(path):
                    try:
                        pdfmetrics.registerFont(TTFont('Square721BT-Bold', path))
                        square721_bold_font_name = 'Square721BT-Bold'
                        break
                    except:
                        pass
            
            # Si Bold n'est pas trouvé, utiliser la même police que Regular
            if square721_bold_font_name == 'Helvetica-Bold' and square721_font_name != 'Helvetica':
                square721_bold_font_name = square721_font_name
        except Exception as e:
            # En cas d'erreur, utiliser la police arabe comme fallback
            if square721_font_name == 'Helvetica':
                square721_font_name = arabic_font_name
            if square721_bold_font_name == 'Helvetica-Bold':
                square721_bold_font_name = arabic_font_name
        
        # Si Square721 BT n'est pas trouvé, utiliser la police arabe pour tout
        # (la police arabe supporte aussi le latin, donc c'est acceptable)
        # Mais on essaie d'abord de créer une version Bold de la police arabe
        if square721_font_name == 'Helvetica':
            square721_font_name = arabic_font_name
            # Essayer de créer une version Bold de la police arabe
            if arabic_font_name == 'ArialUnicodeMS':
                try:
                    # Arial Unicode MS n'a pas de version Bold séparée, utiliser la même
                    square721_bold_font_name = arabic_font_name
                except:
                    square721_bold_font_name = arabic_font_name
            elif arabic_font_name == 'Tahoma':
                try:
                    # Essayer Tahoma Bold
                    tahoma_bold_paths = [
                        'C:/Windows/Fonts/tahomabd.ttf',
                        'C:/Windows/Fonts/TahomaBd.ttf',
                    ]
                    for path in tahoma_bold_paths:
                        if os.path.exists(path):
                            try:
                                pdfmetrics.registerFont(TTFont('Tahoma-Bold', path))
                                square721_bold_font_name = 'Tahoma-Bold'
                                break
                            except:
                                pass
                    if square721_bold_font_name == 'Helvetica-Bold':
                        square721_bold_font_name = arabic_font_name
                except:
                    square721_bold_font_name = arabic_font_name
            else:
                square721_bold_font_name = arabic_font_name
        elif square721_bold_font_name == 'Helvetica-Bold':
            square721_bold_font_name = square721_font_name
        
        # Log les polices chargées
        try:
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps({
                    'timestamp': datetime.now().isoformat(),
                    'location': 'projet18_routes.py:export_pdf_multilang:fonts_loaded',
                    'message': 'Polices chargees',
                    'data': {
                        'square721_font': square721_font_name,
                        'square721_bold_font': square721_bold_font_name,
                        'arabic_font': arabic_font_name
                    },
                    'sessionId': 'debug-session',
                    'runId': 'run1'
                }) + '\n')
        except:
            pass
        
        semaines = get_semaines_2026()
        # Limiter à 52 semaines
        semaines = semaines[:52]
        
        # Log nombre de semaines
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps({
                'timestamp': datetime.now().isoformat(),
                'location': 'projet18_routes.py:export_pdf_multilang:semaines',
                'message': 'Nombre de semaines',
                'data': {'nb_semaines': len(semaines)},
                'sessionId': 'debug-session',
                'runId': 'run1'
            }) + '\n')
        
        buffer = BytesIO()
        # Format A4 portrait
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,  # Portrait au lieu de landscape
            rightMargin=0.5*cm,
            leftMargin=0.5*cm,
            topMargin=0.5*cm,
            bottomMargin=0.5*cm
        )
        
        styles = getSampleStyleSheet()
        
        # Styles selon le modèle Quo Vadis
        base_style = ParagraphStyle(
            'Base',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#000000'),
            fontName=square721_font_name,
            leading=10
        )
        
        # Style pour les noms de jours (anglais/français)
        jour_nom_style = ParagraphStyle(
            'JourNom',
            parent=base_style,
            fontSize=9,
            fontName=square721_font_name,
            alignment=TA_LEFT
        )
        
        # Style pour les dates (grand, gras, noir selon l'image)
        date_style = ParagraphStyle(
            'Date',
            parent=base_style,
            fontSize=12,
            fontName=square721_bold_font_name,
            textColor=colors.HexColor('#000000'),  # Noir au lieu de bleu
            alignment=TA_RIGHT
        )
        
        # Style pour les numéros d'heures (gris clair, petit)
        # Utiliser un style qui ne coupe pas les nombres
        heure_style = ParagraphStyle(
            'Heure',
            parent=base_style,
            fontSize=7,
            textColor=colors.HexColor('#999999'),
            alignment=TA_LEFT,
            leading=14
        )
        
        # Style pour les lignes horaires (gris clair)
        # Utiliser un leading strictement égal à la hauteur de ligne pour garantir exactement 2 lignes
        ligne_horaire_style = ParagraphStyle(
            'LigneHoraire',
            parent=base_style,
            fontSize=8,
            textColor=colors.HexColor('#CCCCCC'),
            leading=8,  # Leading égal à la hauteur de ligne pour garantir exactement 2 lignes sans débordement
            spaceBefore=0,
            spaceAfter=0,
            leftIndent=0,
            rightIndent=0,
            firstLineIndent=0
        )
        
        # Style pour Dimanche
        dimanche_nom_style = ParagraphStyle(
            'DimancheNom',
            parent=base_style,
            fontSize=9,
            fontName=square721_font_name,
            alignment=TA_LEFT
        )
        
        dimanche_date_style = ParagraphStyle(
            'DimancheDate',
            parent=base_style,
            fontSize=12,
            fontName=square721_bold_font_name,
            textColor=colors.HexColor('#000000'),  # Noir au lieu de bleu
            alignment=TA_RIGHT
        )
        
        # Style pour les lignes de notes Dimanche
        ligne_note_style = ParagraphStyle(
            'LigneNote',
            parent=base_style,
            fontSize=8,
            textColor=colors.HexColor('#CCCCCC'),
            leading=14
        )
        
        # Style pour jours fériés
        ferie_style = ParagraphStyle(
            'Ferie',
            parent=base_style,
            fontSize=9,
            textColor=colors.HexColor('#FF0000'),
            fontName=square721_font_name,
            alignment=TA_CENTER
        )
        
        # Style pour le mini-calendrier
        cal_header_style = ParagraphStyle(
            'CalHeader',
            parent=base_style,
            fontSize=10,
            fontName=square721_bold_font_name,
            alignment=TA_CENTER
        )
        
        cal_semaine_style = ParagraphStyle(
            'CalSemaine',
            parent=base_style,
            fontSize=7,
            textColor=colors.HexColor('#999999'),
            alignment=TA_LEFT,
            leading=10
        )
        
        cal_date_style = ParagraphStyle(
            'CalDate',
            parent=base_style,
            fontSize=8,
            alignment=TA_CENTER,
            leading=10
        )
        
        # Style Bold dédié pour le numéro de semaine
        # Utiliser un style avec la police Bold directement (sans balise HTML)
        # Même leading que les autres pour un alignement parfait
        semaine_num_bold_style = ParagraphStyle(
            'SemaineNumBold',
            parent=base_style,
            fontSize=10,  # Légèrement plus grand pour plus de visibilité
            fontName=square721_bold_font_name,  # Police Bold directement dans le style
            textColor=colors.HexColor('#0066CC'),
            alignment=TA_LEFT,
            leading=14,  # Même leading que les autres styles
            spaceBefore=0,
            spaceAfter=0,
            firstLineIndent=0,
            leftIndent=0,
            rightIndent=0
        )
        
        # Style pour le texte "Semaine Week"
        # Même leading que le numéro pour un alignement parfait
        semaine_text_style = ParagraphStyle(
            'SemaineText',
            parent=base_style,
            fontSize=9,
            fontName=square721_font_name,
            alignment=TA_LEFT,
            leading=14,  # Même leading que le numéro
            spaceBefore=0,
            spaceAfter=0,
            firstLineIndent=0,
            leftIndent=0,
            rightIndent=0
        )
        
        # Style pour le texte arabe
        # Même leading que les autres pour un alignement parfait
        semaine_arabic_style = ParagraphStyle(
            'SemaineArabic',
            parent=base_style,
            fontSize=9,
            fontName=arabic_font_name,
            alignment=TA_LEFT,
            leading=14,  # Même leading que les autres
            spaceBefore=0,
            spaceAfter=0,
            firstLineIndent=0,
            leftIndent=0,
            rightIndent=0
        )
        
        elements = []
        
        # Dictionnaire des traductions des jours en arabe (pour version multilingue)
        jours_arabe = {
            'lundi': 'الإثنين',
            'mardi': 'الثلاثاء',
            'mercredi': 'الأربعاء',
            'jeudi': 'الخميس',
            'vendredi': 'الجمعة',
            'samedi': 'السبت',
            'dimanche': 'الأحد'
        }
        
        # Heures de 8h à 20h (13 lignes)
        heures = list(range(8, 21))  # 8, 9, 10, ..., 20
        
        # Générer chaque semaine (2 pages par semaine)
        for semaine in semaines:
            # Calculer le mois de référence pour le mini-calendrier
            date_ref = semaine['jeudi'] if semaine['jeudi'] is not None else semaine['vendredi']
            if date_ref is None:
                date_ref = semaine['samedi'] if semaine['samedi'] is not None else datetime(2026, 1, 1)
            mois_ref = date_ref.month if date_ref else 1
            annee_ref = date_ref.year if date_ref else 2026
            
            # ========== PAGE 1 : LUNDI / MARDI / MERCREDI + MINI-CALENDRIER ==========
            page1_data = []
            
            # Ligne avec texte de la semaine en haut à gauche
            # Utiliser un seul Paragraph avec des balises font pour tout mettre sur une seule ligne
            semaine_num_formate1 = f"{semaine['numero']:02d}"
            semaine_ar1 = 'الأسبوع'
            # Un seul Paragraph avec des balises font pour changer les polices et le style
            # Le numéro utilise la police Bold directement dans la balise font
            semaine_row1 = [
                Paragraph(
                    f"<font face='{square721_font_name}'>Semaine Week </font><font face='{square721_bold_font_name}' color='#0066CC' size='10'>{semaine_num_formate1}</font><font face='{arabic_font_name}'> {fix_arabic_text(semaine_ar1)}</font>",
                    ParagraphStyle(
                        'SemaineHeader',
                        parent=base_style,
                        fontSize=9,
                        fontName=arabic_font_name,  # Police de base
                        alignment=TA_LEFT,
                        leading=14,
                        spaceBefore=0,
                        spaceAfter=0
                    )
                ),
                Paragraph("", base_style),  # Colonne vide
                Paragraph("", base_style)   # Colonne vide
            ]
            page1_data.append(semaine_row1)
            
            # En-têtes des 3 colonnes (Lundi, Mardi, Mercredi) - Version multilingue
            header_row = []
            jours_page1 = [
                ('lundi', 'Monday', 'Lundi'),
                ('mardi', 'Tuesday', 'Mardi'),
                ('mercredi', 'Wednesday', 'Mercredi')
            ]
            
            for jour_key, jour_en, jour_fr in jours_page1:
                date_jour = semaine[jour_key]
                if date_jour is not None:
                    # Format avec zéro devant si < 10 (01, 02, 03, 04)
                    date_formatee = f"{date_jour.day:02d}"
                    jour_ar = jours_arabe.get(jour_key, '')
                    
                    # Structure : Date en haut (grande), jours en bas (3 langues)
                    # Créer un tableau avec date en haut et jours en bas
                    try:
                        # Ligne 1 : Date (grande, centrée en haut)
                        # Ligne 2 : Français, Anglais, Arabe (en bas)
                        # Utiliser Square721 BT Bold pour les dates (chiffres uniquement)
                        # Utiliser la police arabe pour le texte mixte (contient de l'arabe)
                        header_table = Table([
                            [Paragraph(date_formatee, ParagraphStyle(
                                'HeaderDateMultilang',
                                parent=base_style,
                                fontSize=24,  # Plus grande que la version standard
                                fontName=square721_bold_font_name,  # Square721 BT Bold pour les dates (chiffres)
                                textColor=colors.HexColor('#0066CC'),
                                alignment=TA_CENTER,
                                leading=30  # Augmenter leading pour éviter superposition
                            ))],  # Ligne 1 : Date seule (chiffres uniquement)
                            [Paragraph(
                                f"<font face='{square721_font_name}'>{jour_fr}</font> / <font face='{square721_font_name}'>{jour_en}</font> / <font face='{arabic_font_name}'>{fix_arabic_text(jour_ar)}</font>",
                                ParagraphStyle(
                                    'HeaderJourMultilang',
                                    parent=base_style,
                                    fontSize=9,
                                    fontName=arabic_font_name,  # Police de base (arabe) pour le Paragraph
                                    alignment=TA_CENTER,
                                    leading=16  # Augmenter leading pour l'espacement
                                )
                            )]  # Ligne 2 : Trois langues (contient de l'arabe)
                        ], colWidths=[5.5*cm], rowHeights=[1.2*cm, 0.8*cm])  # Hauteurs explicites pour éviter superposition
                        header_table.setStyle(TableStyle([
                            ('VALIGN', (0, 0), (0, 0), 'MIDDLE'),  # Date centrée verticalement dans sa ligne
                            ('VALIGN', (0, 1), (0, 1), 'MIDDLE'),  # Jours centrés verticalement dans leur ligne
                            ('ALIGN', (0, 0), (0, 0), 'CENTER'),  # Date centrée
                            ('ALIGN', (0, 1), (0, 1), 'CENTER'),  # Jours centrés
                            ('LEFTPADDING', (0, 0), (-1, -1), 2),
                            ('RIGHTPADDING', (0, 0), (-1, -1), 2),
                            ('TOPPADDING', (0, 0), (0, 0), 8),  # Padding pour la date
                            ('BOTTOMPADDING', (0, 0), (0, 0), 4),  # Espacement entre date et jours
                            ('TOPPADDING', (0, 1), (0, 1), 4),  # Espacement entre date et jours
                            ('BOTTOMPADDING', (0, 1), (0, 1), 8),  # Padding pour les jours
                        ]))
                    except Exception as e_header:
                        raise
                    # Créer une table avec header_table (date+jours) et jour férié éventuel
                    # Toujours utiliser 2 lignes pour uniformiser la hauteur
                    jour_ferie = is_jour_ferie(date_jour)
                    if jour_ferie:
                        nom_ferie = get_nom_jour_ferie(date_jour)
                        # Réduire le BOTTOMPADDING de la ligne des jours dans header_table quand il y a un jour férié
                        header_table.setStyle(TableStyle([
                            ('VALIGN', (0, 0), (0, 0), 'MIDDLE'),  # Date centrée verticalement dans sa ligne
                            ('VALIGN', (0, 1), (0, 1), 'MIDDLE'),  # Jours centrés verticalement dans leur ligne
                            ('ALIGN', (0, 0), (0, 0), 'CENTER'),  # Date centrée
                            ('ALIGN', (0, 1), (0, 1), 'CENTER'),  # Jours centrés
                            ('LEFTPADDING', (0, 0), (-1, -1), 2),
                            ('RIGHTPADDING', (0, 0), (-1, -1), 2),
                            ('TOPPADDING', (0, 0), (0, 0), 8),  # Padding pour la date
                            ('BOTTOMPADDING', (0, 0), (0, 0), 4),  # Espacement entre date et jours
                            ('TOPPADDING', (0, 1), (0, 1), 4),  # Espacement entre date et jours
                            ('BOTTOMPADDING', (0, 1), (0, 1), 0),  # Pas de padding en bas des jours quand il y a un jour férié
                        ]))
                        ferie_para = Paragraph(
                            f"<font color='#FF0000'>{nom_ferie}</font>",
                            ferie_style
                        )
                    else:
                        # Paragraph vide pour maintenir la même hauteur
                        ferie_para = Paragraph("", base_style)
                    
                    # Table avec toujours 2 lignes : header_table en haut, jour férié (ou vide) en bas
                    # Hauteurs fixes : header_table (2.0cm) + ligne férié (0.4cm) = 2.4cm total
                    header_cell = Table(
                        [[header_table], [ferie_para]],
                        colWidths=[5.5*cm],
                        rowHeights=[2.0*cm, 0.4*cm]  # Hauteurs fixes pour uniformiser
                    )
                    
                    header_cell.setStyle(TableStyle([
                        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('LEFTPADDING', (0, 0), (-1, -1), 2),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 2),
                        ('TOPPADDING', (0, 0), (-1, -1), 8),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                        # Réduire l'espacement entre header_table (ligne 0) et jour férié (ligne 1)
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 0),  # Pas de padding en bas de header_table
                        ('TOPPADDING', (0, 1), (-1, 1), 0),  # Pas de padding en haut du jour férié
                    ]))
                    header_row.append(header_cell)
                else:
                    header_row.append(Paragraph("", base_style))
            
            page1_data.append(header_row)
            
            # Ligne vide pour séparer les en-têtes des jours des champs de saisie
            page1_data.append([Paragraph("", base_style), Paragraph("", base_style), Paragraph("", base_style)])
            
            # 13 lignes horaires pour chaque colonne (8h-20h)
            for heure in heures:
                ligne_row = []
                for jour_key, jour_en, jour_fr in jours_page1:
                    date_jour = semaine[jour_key]
                    if date_jour is not None:
                        # Ligne avec numéro d'heure à gauche et deux lignes grises identiques
                        # Créer deux lignes distinctes avec exactement le même nombre de caractères pour garantir une longueur uniforme
                        # Utiliser un nombre de caractères fixe (42) pour remplir la largeur disponible sans retour à la ligne
                        # Créer exactement 2 lignes de longueur adaptée sans retour à la ligne
                        # Utiliser un nombre de caractères réduit pour éviter tout retour à la ligne dans le Paragraph
                        # Environ 30-32 caractères pour une largeur de 4.7cm avec fontSize=8 pour éviter tout débordement
                        ligne_underscore = "_" * 26  # Nombre de caractères très réduit pour garantir qu'il n'y a pas de retour à la ligne et éviter toute ligne supplémentaire
                        # Créer un style spécifique pour empêcher les retours à la ligne
                        ligne_horaire_style_no_wrap = ParagraphStyle(
                            'LigneHoraireNoWrap',
                            parent=ligne_horaire_style,
                            leading=12,  # Leading exactement égal à rowHeights pour garantir exactement 2 lignes sans débordement
                            spaceBefore=0,
                            spaceAfter=0
                        )
                        # Style pour le numéro d'heure aligné avec la première ligne
                        # Utiliser exactement le même leading que la ligne pour un alignement parfait
                        heure_num_style = ParagraphStyle(
                            'HeureNum',
                            parent=base_style,
                            fontSize=7,
                            textColor=colors.HexColor('#999999'),
                            alignment=TA_LEFT,
                            leading=12,  # Exactement le même leading que ligne_horaire_style_no_wrap
                            spaceBefore=0,
                            spaceAfter=0,
                            firstLineIndent=0,
                            leftIndent=0,
                            rightIndent=0
                        )
                        heure_cell = Table(
                            [
                                [Paragraph(str(heure), heure_num_style), Paragraph(ligne_underscore, ligne_horaire_style_no_wrap)],
                                [Paragraph("", base_style), Paragraph(ligne_underscore, ligne_horaire_style_no_wrap)]
                            ],
                            colWidths=[0.6*cm, 4.9*cm],  # Réduire la largeur de la colonne du numéro pour le rapprocher
                            rowHeights=[12, 12]  # Hauteur exactement égale au leading pour garantir exactement 2 lignes sans ligne supplémentaire
                        )
                        heure_cell.setStyle(TableStyle([
                            ('ALIGN', (0, 0), (0, 0), 'RIGHT'),  # Alignement à droite pour le numéro (plus proche de la ligne)
                            ('ALIGN', (1, 0), (1, -1), 'LEFT'),  # Alignement à gauche pour les lignes
                            ('VALIGN', (0, 0), (0, 0), 'TOP'),  # Alignement en haut pour permettre le décalage avec TOPPADDING
                            ('VALIGN', (1, 0), (1, 0), 'BOTTOM'),  # Aligner la première ligne sur sa ligne de base
                            ('VALIGN', (1, 1), (1, 1), 'TOP'),  # Alignement en haut pour la deuxième ligne
                            ('LEFTPADDING', (0, 0), (0, 0), 5),  # Padding à gauche encore augmenté pour décaler davantage le numéro vers la droite
                            ('RIGHTPADDING', (0, 0), (0, 0), 0),  # Pas de padding à droite pour le numéro (très proche de la ligne)
                            ('LEFTPADDING', (1, 0), (1, -1), 0),  # Pas de padding à gauche pour les lignes (très proche du numéro)
                            ('RIGHTPADDING', (1, 0), (1, -1), 2),
                            ('TOPPADDING', (0, 0), (0, 0), 2),  # Padding en haut légèrement augmenté pour descendre très légèrement le numéro
                            ('TOPPADDING', (1, 0), (-1, -1), 0),  # Pas de padding en haut pour les lignes
                            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),  # Pas de padding en bas
                            ('BOTTOMPADDING', (1, 1), (1, 1), 0),  # Pas de padding en bas de la dernière ligne
                        ]))
                        ligne_row.append(heure_cell)
                    else:
                        ligne_row.append(Paragraph("", base_style))
                page1_data.append(ligne_row)
            
            # Mini-calendrier du mois (déplacé de la page 2 vers la page 1)
            # Créer le mini-calendrier avec numéros de semaine
            _, nb_jours_mois = monthrange(annee_ref, mois_ref)
            premier_jour_mois = datetime(annee_ref, mois_ref, 1)
            jour_semaine_premier = premier_jour_mois.weekday()
            
            # Construire le mini-calendrier comme une grille horizontale
            # Structure : une table avec plusieurs lignes
            cal_table_rows = []
            
            # Ligne 1 : En-tête mois/année (sur 8 colonnes : fusionnées)
            cal_table_rows.append([
                Paragraph(f"{get_mois_nom(mois_ref)} {annee_ref}", cal_header_style),
                Paragraph("", base_style), Paragraph("", base_style), Paragraph("", base_style),
                Paragraph("", base_style), Paragraph("", base_style), Paragraph("", base_style), Paragraph("", base_style)
            ])
            
            # Ligne 2 : Abréviations des jours ("lu ma me je ve sa di")
            jours_abrev = ["lu", "ma", "me", "je", "ve", "sa", "di"]
            cal_jours_abrev_row = [Paragraph("", base_style)]  # Espace pour numéro semaine
            for abrev in jours_abrev:
                cal_jours_abrev_row.append(Paragraph(
                    abrev,
                    ParagraphStyle(
                        'CalJoursAbrev',
                        parent=base_style,
                        fontSize=7,
                        alignment=TA_CENTER,
                        leading=10
                    )
                ))
            cal_table_rows.append(cal_jours_abrev_row)
            
            # Créer la grille du calendrier avec numéros de semaine
            semaine_cal = []
            jours_cal = []
            semaine_num_cal = []
            
            # Trouver le numéro de semaine pour chaque jour
            def get_semaine_num_for_date(date_cible):
                for s in semaines:
                    jours_semaine_list = [s['lundi'], s['mardi'], s['mercredi'], s['jeudi'], s['vendredi'], s['samedi'], s['dimanche']]
                    for d in jours_semaine_list:
                        if d and d.date() == date_cible.date():
                            return s['numero']
                return None
            
            # Calculer correctement le positionnement du premier jour du mois
            # Le premier jour doit être à la position jour_semaine_premier (0=lundi, 3=jeudi, etc.)
            
            # Ajouter les dates de décembre avant janvier (si mois_ref == 1)
            if mois_ref == 1:
                mois_precedent = 12
                annee_precedente = annee_ref - 1
                _, nb_jours_decembre = monthrange(annee_precedente, mois_precedent)
                
                # Ajouter les 3 derniers jours de décembre (29, 30, 31)
                for jour_dec in range(29, 32):
                    date_dec = datetime(annee_precedente, mois_precedent, jour_dec)
                    semaine_num = get_semaine_num_for_date(date_dec)
                    semaine_num_cal.append(str(semaine_num) if semaine_num else "")
                    jours_cal.append(f"{jour_dec:02d}")
                
                # Après avoir ajouté 29, 30, 31, on a 3 éléments dans jours_cal
                # Le 29 décembre 2025 est un lundi (weekday=0), donc :
                # - Position 0: 29 (lundi)
                # - Position 1: 30 (mardi)  
                # - Position 2: 31 (mercredi)
                # Le 1er janvier 2026 est un jeudi (weekday=3), donc il doit être à la position 3
                # Comme on a déjà 3 éléments, la prochaine position est 3, ce qui est correct
                # Donc pas besoin d'espaces supplémentaires
                nb_espaces_a_ajouter = 0
            else:
                # Pour les autres mois, ajouter simplement les espaces nécessaires
                nb_espaces_a_ajouter = jour_semaine_premier
            
            # Ajouter les espaces nécessaires
            for _ in range(nb_espaces_a_ajouter):
                if len(jours_cal) < 7:  # Ne pas dépasser 7 jours par semaine
                    semaine_num_cal.append("")
                    jours_cal.append("")
            
            # Ajouter les jours du mois courant avec numéro de semaine
            jour_courant = 1
            premier_jour_position = None  # Position du premier jour du mois dans la ligne
            while jour_courant <= nb_jours_mois:
                jour_date = datetime(annee_ref, mois_ref, jour_courant)
                semaine_num = get_semaine_num_for_date(jour_date)
                
                semaine_num_cal.append(str(semaine_num) if semaine_num else "")
                # Format avec zéro devant si < 10
                jours_cal.append(f"{jour_courant:02d}")
                
                # Marquer la position du premier jour du mois dans la ligne actuelle
                if jour_courant == 1:
                    premier_jour_position = len(jours_cal) - 1
                
                jour_courant += 1
                
                if len(jours_cal) == 7:
                    # Trouver le numéro de semaine pour cette ligne (prendre le premier non vide)
                    semaine_num_ligne = None
                    for sn in semaine_num_cal:
                        if sn:
                            semaine_num_ligne = sn
                            break
                    
                    # Créer une ligne avec numéro de semaine à gauche et dates à droite
                    cal_row_cells = []
                    # Numéro de semaine à gauche (petit, gris)
                    cal_row_cells.append(Paragraph(
                        semaine_num_ligne if semaine_num_ligne else "",
                        cal_semaine_style
                    ))
                    
                    # Dates à droite (7 colonnes)
                    for idx, jour_str in enumerate(jours_cal):
                        # Highlight bleu clair pour le premier jour du mois (01) du mois courant
                        if idx == premier_jour_position and jour_str == "01":
                            # C'est le premier jour du mois courant
                            cal_row_cells.append(Paragraph(
                                jour_str,
                                ParagraphStyle(
                                    'CalDateHighlight',
                                    parent=base_style,
                                    fontSize=8,
                                    textColor=colors.HexColor('#0066CC'),
                                    backColor=colors.HexColor('#E6F3FF'),  # Bleu clair
                                    alignment=TA_CENTER,
                                    leading=10
                                )
                            ))
                            premier_jour_position = None  # Ne highlight qu'une fois
                        else:
                            cal_row_cells.append(Paragraph(jour_str, cal_date_style))
                    
                    # Ajouter la ligne directement à cal_table_rows
                    cal_table_rows.append(cal_row_cells)
                    
                    semaine_cal = []
                    jours_cal = []
                    semaine_num_cal = []
            
            # Compléter la dernière semaine avec le début de février (si nécessaire)
            if len(jours_cal) > 0 and len(jours_cal) < 7:
                mois_suivant = mois_ref + 1 if mois_ref < 12 else 1
                annee_suivante = annee_ref if mois_ref < 12 else annee_ref + 1
                jour_fevrier = 1
                while len(jours_cal) < 7:
                    date_fev = datetime(annee_suivante, mois_suivant, jour_fevrier)
                    semaine_num = get_semaine_num_for_date(date_fev)
                    semaine_num_cal.append(str(semaine_num) if semaine_num else "")
                    jours_cal.append(f"{jour_fevrier:02d}")
                    jour_fevrier += 1
                
                # Créer la dernière ligne avec numéro de semaine à gauche
                # Trouver le numéro de semaine pour cette ligne
                semaine_num_ligne = None
                for sn in semaine_num_cal:
                    if sn:
                        semaine_num_ligne = sn
                        break
                
                cal_row_cells = []
                # Numéro de semaine à gauche
                cal_row_cells.append(Paragraph(
                    semaine_num_ligne if semaine_num_ligne else "",
                    cal_semaine_style
                ))
                
                # Dates à droite
                for jour_str in jours_cal:
                    cal_row_cells.append(Paragraph(jour_str, cal_date_style))
                
                cal_table_rows.append(cal_row_cells)
            
            # Limiter à 6 lignes de dates (en plus de l'en-tête et des abréviations)
            # Total : 1 en-tête + 1 abréviations + 6 lignes dates = 8 lignes max
            if len(cal_table_rows) > 8:
                cal_table_rows = cal_table_rows[:8]
            
            # Créer le tableau du mini-calendrier comme une grille horizontale
            try:
                cal_table = Table(
                    cal_table_rows,
                    colWidths=[0.6*cm] + [0.7*cm] * 7  # Numéro semaine (ajusté) + 7 dates = 8 colonnes
                )
                cal_table.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (0, 0), 'CENTER'),  # En-tête mois centré sur toutes les colonnes
                    ('SPAN', (0, 0), (-1, 0)),  # Fusionner les colonnes pour l'en-tête
                    ('ALIGN', (0, 1), (0, -1), 'LEFT'),  # Numéros de semaine à gauche
                    ('ALIGN', (1, 1), (-1, -1), 'CENTER'),  # Dates et abréviations centrées
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 2),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 2),
                    ('TOPPADDING', (0, 0), (-1, -1), 2),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CCCCCC')),
                ]))
            except Exception as e_cal_table:
                raise
            
            # Ajouter la ligne avec mini-calendrier à gauche
            cal_row = [
                cal_table,  # Mini-calendrier colonne 1 (à gauche)
                Paragraph("", base_style),  # Espace vide colonne 2
                Paragraph("", base_style)  # Espace vide colonne 3
            ]
            page1_data.append(cal_row)
            
            # Trouver l'index de la ligne du mini-calendrier (dernière ligne)
            cal_row_index = len(page1_data) - 1
            
            # Trouver l'index de la ligne des en-têtes (après la ligne de la semaine)
            header_row_index = 1  # La ligne de la semaine est à l'index 0, les en-têtes sont à l'index 1
            semaine_row_index = 0  # La ligne de la semaine est à l'index 0
            ligne_vide_index = 2  # La ligne vide est à l'index 2 (après la semaine et les en-têtes)
            
            # Trouver l'index de la dernière ligne horaire (20h)
            # Il y a 1 ligne vide + 13 lignes horaires (8h-20h), donc la dernière est à l'index ligne_vide_index + 13
            derniere_ligne_horaire_index = ligne_vide_index + len(heures)  # ligne_vide_index (2) + 13 lignes horaires = 15
            
            # Créer le tableau pour la page 1 (format portrait - colonnes plus étroites)
            # Calculer les hauteurs de lignes : ligne semaine (fixe), ligne en-tête (fixe), autres lignes (auto)
            # Hauteur ligne semaine : identique à la page 2 (0.7cm) pour que les tableaux commencent au même niveau
            # Hauteur ligne en-tête : header_cell (2.4cm) + TOPPADDING (0.3cm) = 2.7cm
            page1_row_heights = [None] * len(page1_data)  # None = hauteur automatique
            page1_row_heights[semaine_row_index] = 0.7*cm  # Hauteur fixe pour la ligne de la semaine (identique à page 2)
            page1_row_heights[header_row_index] = 2.7*cm  # Hauteur fixe pour la ligne d'en-tête
            # Hauteur de la ligne vide = même hauteur que les lignes horaires (2 lignes de 12 points chacune = 24 points ≈ 0.85cm)
            page1_row_heights[ligne_vide_index] = 24  # Même hauteur que les lignes horaires (2 lignes de 12 points)
            page1_table = Table(page1_data, colWidths=[5.5*cm, 5.5*cm, 5.5*cm], rowHeights=page1_row_heights)
            page1_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                # Bordures pour toutes les lignes sauf la ligne de la semaine
                ('GRID', (0, 1), (-1, -1), 0.5, colors.HexColor('#CCCCCC')),  # Bordures grises fines (à partir de la ligne 1)
                # Supprimer toutes les bordures de la ligne de la semaine (ligne 0)
                ('LINEABOVE', (0, semaine_row_index), (-1, semaine_row_index), 0, colors.white),  # Pas de bordure au-dessus
                ('LINEBELOW', (0, semaine_row_index), (-1, semaine_row_index), 0, colors.white),  # Pas de bordure en-dessous
                ('LINEBEFORE', (0, semaine_row_index), (0, semaine_row_index), 0, colors.white),  # Pas de bordure à gauche
                ('LINEAFTER', (-1, semaine_row_index), (-1, semaine_row_index), 0, colors.white),  # Pas de bordure à droite
                ('LINEBELOW', (0, header_row_index), (-1, header_row_index), 1, colors.HexColor('#CCCCCC')),  # Ligne sous les en-têtes
                # Supprimer la ligne verticale entre Mardi (colonne 1) et Mercredi (colonne 2) uniquement pour la ligne du mini-calendrier
                ('LINEAFTER', (1, cal_row_index), (1, cal_row_index), 0, colors.white),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                # Ajouter un espacement en haut de la ligne des en-têtes pour décaler le reste du tableau vers le bas (identique à la page 2)
                ('TOPPADDING', (0, header_row_index), (-1, header_row_index), 0.3*cm),
            ]))
            
            elements.append(page1_table)
            elements.append(PageBreak())
            
            # ========== PAGE 2 : JEUDI / VENDREDI / SAMEDI + DIMANCHE ==========
            page2_data = []
            
            # Ligne avec texte de la semaine en haut à gauche et "2026" en haut à droite
            semaine_num_formate2 = f"{semaine['numero']:02d}"
            semaine_ar2 = 'الأسبوع'
            # Utiliser un seul Paragraph avec des balises font pour tout mettre sur une seule ligne (même approche que page 1)
            # Le numéro utilise la police Bold directement dans la balise font
            semaine_row2 = [
                Paragraph(
                    f"<font face='{square721_font_name}'>Semaine Week </font><font face='{square721_bold_font_name}' color='#0066CC' size='10'>{semaine_num_formate2}</font><font face='{arabic_font_name}'> {fix_arabic_text(semaine_ar2)}</font>",
                    ParagraphStyle(
                        'SemaineHeader',
                        parent=base_style,
                        fontSize=9,
                        fontName=arabic_font_name,  # Police de base
                        alignment=TA_LEFT,
                        leading=14,
                        spaceBefore=0,
                        spaceAfter=0
                    )
                ),
                Paragraph("", base_style),  # Colonne vide
                Paragraph("2026", ParagraphStyle(
                    'AnneePage2',
                    parent=base_style,
                    fontSize=18,
                    fontName=square721_bold_font_name,
                    textColor=colors.HexColor('#0066CC'),
                    alignment=TA_RIGHT,
                    leading=20
                ))
            ]
            page2_data.append(semaine_row2)
            
            # En-têtes des 3 colonnes (Jeudi, Vendredi, Samedi) - Version multilingue
            header_row2 = []
            jours_page2 = [
                ('jeudi', 'Thursday', 'Jeudi'),
                ('vendredi', 'Friday', 'Vendredi'),
                ('samedi', 'Saturday', 'Samedi')
            ]
            
            for jour_key, jour_en, jour_fr in jours_page2:
                date_jour = semaine[jour_key]
                if date_jour is not None:
                    # Format avec zéro devant si < 10 (01, 02, 03, 04)
                    date_formatee = f"{date_jour.day:02d}"
                    jour_ar = jours_arabe.get(jour_key, '')
                    
                    # Structure : Date en haut (grande), jours en bas (3 langues)
                    # Créer un tableau avec date en haut et jours en bas
                    try:
                        # Ligne 1 : Date (grande, centrée en haut)
                        # Ligne 2 : Français, Anglais, Arabe (en bas)
                        # Utiliser Square721 BT Bold pour les dates (chiffres uniquement)
                        # Utiliser la police arabe pour le texte mixte (contient de l'arabe)
                        header_table = Table([
                            [Paragraph(date_formatee, ParagraphStyle(
                                'HeaderDateMultilang',
                                parent=base_style,
                                fontSize=24,  # Plus grande que la version standard
                                fontName=square721_bold_font_name,  # Square721 BT Bold pour les dates (chiffres)
                                textColor=colors.HexColor('#0066CC'),
                                alignment=TA_CENTER,
                                leading=30  # Augmenter leading pour éviter superposition
                            ))],  # Ligne 1 : Date seule (chiffres uniquement)
                            [Paragraph(
                                f"<font face='{square721_font_name}'>{jour_fr}</font> / <font face='{square721_font_name}'>{jour_en}</font> / <font face='{arabic_font_name}'>{fix_arabic_text(jour_ar)}</font>",
                                ParagraphStyle(
                                    'HeaderJourMultilang',
                                    parent=base_style,
                                    fontSize=9,
                                    fontName=arabic_font_name,  # Police de base (arabe) pour le Paragraph
                                    alignment=TA_CENTER,
                                    leading=16  # Augmenter leading pour l'espacement
                                )
                            )]  # Ligne 2 : Trois langues (contient de l'arabe)
                        ], colWidths=[5.5*cm], rowHeights=[1.2*cm, 0.8*cm])  # Hauteurs explicites pour éviter superposition
                        header_table.setStyle(TableStyle([
                            ('VALIGN', (0, 0), (0, 0), 'MIDDLE'),  # Date centrée verticalement dans sa ligne
                            ('VALIGN', (0, 1), (0, 1), 'MIDDLE'),  # Jours centrés verticalement dans leur ligne
                            ('ALIGN', (0, 0), (0, 0), 'CENTER'),  # Date centrée
                            ('ALIGN', (0, 1), (0, 1), 'CENTER'),  # Jours centrés
                            ('LEFTPADDING', (0, 0), (-1, -1), 2),
                            ('RIGHTPADDING', (0, 0), (-1, -1), 2),
                            ('TOPPADDING', (0, 0), (0, 0), 8),  # Padding pour la date
                            ('BOTTOMPADDING', (0, 0), (0, 0), 4),  # Espacement entre date et jours
                            ('TOPPADDING', (0, 1), (0, 1), 4),  # Espacement entre date et jours
                            ('BOTTOMPADDING', (0, 1), (0, 1), 8),  # Padding pour les jours
                        ]))
                    except Exception as e_header:
                        raise
                    # Créer une table avec header_table (date+jours) et jour férié éventuel
                    # Toujours utiliser 2 lignes pour uniformiser la hauteur
                    jour_ferie = is_jour_ferie(date_jour)
                    if jour_ferie:
                        nom_ferie = get_nom_jour_ferie(date_jour)
                        # Réduire le BOTTOMPADDING de la ligne des jours dans header_table quand il y a un jour férié
                        header_table.setStyle(TableStyle([
                            ('VALIGN', (0, 0), (0, 0), 'MIDDLE'),  # Date centrée verticalement dans sa ligne
                            ('VALIGN', (0, 1), (0, 1), 'MIDDLE'),  # Jours centrés verticalement dans leur ligne
                            ('ALIGN', (0, 0), (0, 0), 'CENTER'),  # Date centrée
                            ('ALIGN', (0, 1), (0, 1), 'CENTER'),  # Jours centrés
                            ('LEFTPADDING', (0, 0), (-1, -1), 2),
                            ('RIGHTPADDING', (0, 0), (-1, -1), 2),
                            ('TOPPADDING', (0, 0), (0, 0), 8),  # Padding pour la date
                            ('BOTTOMPADDING', (0, 0), (0, 0), 4),  # Espacement entre date et jours
                            ('TOPPADDING', (0, 1), (0, 1), 4),  # Espacement entre date et jours
                            ('BOTTOMPADDING', (0, 1), (0, 1), 0),  # Pas de padding en bas des jours quand il y a un jour férié
                        ]))
                        ferie_para = Paragraph(
                            f"<font color='#FF0000'>{nom_ferie}</font>",
                            ferie_style
                        )
                    else:
                        # Paragraph vide pour maintenir la même hauteur
                        ferie_para = Paragraph("", base_style)
                    
                    # Table avec toujours 2 lignes : header_table en haut, jour férié (ou vide) en bas
                    # Hauteurs fixes : header_table (2.0cm) + ligne férié (0.4cm) = 2.4cm total
                    header_cell = Table(
                        [[header_table], [ferie_para]],
                        colWidths=[5.5*cm],
                        rowHeights=[2.0*cm, 0.4*cm]  # Hauteurs fixes pour uniformiser
                    )
                    
                    header_cell.setStyle(TableStyle([
                        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('LEFTPADDING', (0, 0), (-1, -1), 2),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 2),
                        ('TOPPADDING', (0, 0), (-1, -1), 8),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                        # Réduire l'espacement entre header_table (ligne 0) et jour férié (ligne 1)
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 0),  # Pas de padding en bas de header_table
                        ('TOPPADDING', (0, 1), (-1, 1), 0),  # Pas de padding en haut du jour férié
                    ]))
                    header_row2.append(header_cell)
                else:
                    header_row2.append(Paragraph("", base_style))
            
            page2_data.append(header_row2)
            
            # Ligne vide pour séparer les en-têtes des jours des champs de saisie
            page2_data.append([Paragraph("", base_style), Paragraph("", base_style), Paragraph("", base_style)])
            
            # 13 lignes horaires pour chaque colonne (8h-20h)
            for heure in heures:
                ligne_row = []
                for jour_key, jour_en, jour_fr in jours_page2:
                    date_jour = semaine[jour_key]
                    if date_jour is not None:
                        # Ligne avec numéro d'heure à gauche et deux lignes grises identiques
                        # Créer deux lignes distinctes avec exactement le même nombre de caractères pour garantir une longueur uniforme
                        # Utiliser un nombre de caractères fixe (42) pour remplir la largeur disponible sans retour à la ligne
                        # Créer exactement 2 lignes de longueur adaptée sans retour à la ligne
                        # Utiliser un nombre de caractères réduit pour éviter tout retour à la ligne dans le Paragraph
                        # Environ 30-32 caractères pour une largeur de 4.7cm avec fontSize=8 pour éviter tout débordement
                        ligne_underscore = "_" * 26  # Nombre de caractères très réduit pour garantir qu'il n'y a pas de retour à la ligne et éviter toute ligne supplémentaire
                        # Créer un style spécifique pour empêcher les retours à la ligne
                        ligne_horaire_style_no_wrap = ParagraphStyle(
                            'LigneHoraireNoWrap',
                            parent=ligne_horaire_style,
                            leading=12,  # Leading exactement égal à rowHeights pour garantir exactement 2 lignes sans débordement
                            spaceBefore=0,
                            spaceAfter=0
                        )
                        # Style pour le numéro d'heure aligné avec la première ligne
                        # Utiliser exactement le même leading que la ligne pour un alignement parfait
                        heure_num_style = ParagraphStyle(
                            'HeureNum',
                            parent=base_style,
                            fontSize=7,
                            textColor=colors.HexColor('#999999'),
                            alignment=TA_LEFT,
                            leading=12,  # Exactement le même leading que ligne_horaire_style_no_wrap
                            spaceBefore=0,
                            spaceAfter=0,
                            firstLineIndent=0,
                            leftIndent=0,
                            rightIndent=0
                        )
                        heure_cell = Table(
                            [
                                [Paragraph(str(heure), heure_num_style), Paragraph(ligne_underscore, ligne_horaire_style_no_wrap)],
                                [Paragraph("", base_style), Paragraph(ligne_underscore, ligne_horaire_style_no_wrap)]
                            ],
                            colWidths=[0.6*cm, 4.9*cm],  # Réduire la largeur de la colonne du numéro pour le rapprocher
                            rowHeights=[12, 12]  # Hauteur exactement égale au leading pour garantir exactement 2 lignes sans ligne supplémentaire
                        )
                        heure_cell.setStyle(TableStyle([
                            ('ALIGN', (0, 0), (0, 0), 'RIGHT'),  # Alignement à droite pour le numéro (plus proche de la ligne)
                            ('ALIGN', (1, 0), (1, -1), 'LEFT'),  # Alignement à gauche pour les lignes
                            ('VALIGN', (0, 0), (0, 0), 'TOP'),  # Alignement en haut pour permettre le décalage avec TOPPADDING
                            ('VALIGN', (1, 0), (1, 0), 'BOTTOM'),  # Aligner la première ligne sur sa ligne de base
                            ('VALIGN', (1, 1), (1, 1), 'TOP'),  # Alignement en haut pour la deuxième ligne
                            ('LEFTPADDING', (0, 0), (0, 0), 5),  # Padding à gauche encore augmenté pour décaler davantage le numéro vers la droite
                            ('RIGHTPADDING', (0, 0), (0, 0), 0),  # Pas de padding à droite pour le numéro (très proche de la ligne)
                            ('LEFTPADDING', (1, 0), (1, -1), 0),  # Pas de padding à gauche pour les lignes (très proche du numéro)
                            ('RIGHTPADDING', (1, 0), (1, -1), 2),
                            ('TOPPADDING', (0, 0), (0, 0), 2),  # Padding en haut légèrement augmenté pour descendre très légèrement le numéro
                            ('TOPPADDING', (1, 0), (-1, -1), 0),  # Pas de padding en haut pour les lignes
                            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),  # Pas de padding en bas
                            ('BOTTOMPADDING', (1, 1), (1, 1), 0),  # Pas de padding en bas de la dernière ligne
                        ]))
                        ligne_row.append(heure_cell)
                    else:
                        ligne_row.append(Paragraph("", base_style))
                page2_data.append(ligne_row)
            
            # Zone Dimanche : en-tête dans colonne 1, lignes grises dans colonnes 2 et 3 (déplacé de la page 1 vers la page 2)
            dimanche_row = []
            if semaine['dimanche'] is not None:
                jour_ferie = is_jour_ferie(semaine['dimanche'])
                nom_ferie = get_nom_jour_ferie(semaine['dimanche']) if jour_ferie else ""
                
                # Contenu Dimanche : Date en haut (grande), jours en bas (3 langues)
                # Format avec zéro devant si < 10
                date_dimanche_formatee = f"{semaine['dimanche'].day:02d}"
                dimanche_ar = jours_arabe.get('dimanche', 'الأحد')
                
                # Structure : Date en haut (grande), jours en bas (3 langues)
                # Utiliser Square721 BT Bold pour les dates (chiffres uniquement, pas besoin d'arabe)
                # Utiliser Square721 BT pour tous les textes
                dimanche_header_table = Table([
                    [Paragraph(date_dimanche_formatee, ParagraphStyle(
                        'DimancheDateMultilang',
                        parent=base_style,
                        fontSize=24,  # Plus grande que la version standard
                                fontName=square721_bold_font_name,  # Square721 BT Bold pour les dates
                        textColor=colors.HexColor('#0066CC'),
                        alignment=TA_CENTER,
                        leading=30  # Augmenter leading pour éviter superposition
                    ))],  # Ligne 1 : Date seule
                    [Paragraph(
                        f"<font face='{square721_font_name}'>Dimanche</font> / <font face='{square721_font_name}'>Sunday</font> / <font face='{arabic_font_name}'>{fix_arabic_text(dimanche_ar)}</font>",
                        ParagraphStyle(
                            'DimancheJourMultilang',
                            parent=base_style,
                            fontSize=9,
                            fontName=arabic_font_name,
                            alignment=TA_CENTER,
                            leading=16  # Augmenter leading pour l'espacement
                        )
                    )]  # Ligne 2 : Trois langues
                ], colWidths=[5.5*cm], rowHeights=[1.2*cm, 0.8*cm])  # Hauteurs explicites pour éviter superposition
                dimanche_header_table.setStyle(TableStyle([
                    ('VALIGN', (0, 0), (0, 0), 'MIDDLE'),  # Date centrée verticalement dans sa ligne
                    ('VALIGN', (0, 1), (0, 1), 'MIDDLE'),  # Jours centrés verticalement dans leur ligne
                    ('ALIGN', (0, 0), (0, 0), 'CENTER'),  # Date centrée
                    ('ALIGN', (0, 1), (0, 1), 'CENTER'),  # Jours centrés
                    ('LEFTPADDING', (0, 0), (-1, -1), 2),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 2),
                    ('TOPPADDING', (0, 0), (0, 0), 8),  # Padding pour la date
                    ('BOTTOMPADDING', (0, 0), (0, 0), 4),  # Espacement entre date et jours
                    ('TOPPADDING', (0, 1), (0, 1), 4),  # Espacement entre date et jours
                    ('BOTTOMPADDING', (0, 1), (0, 1), 8),  # Padding pour les jours
                ]))
                
                # Colonne 1 : En-tête Dimanche + date (et jour férié si applicable)
                # Toujours utiliser 2 lignes pour uniformiser la hauteur
                if jour_ferie:
                    # Réduire le BOTTOMPADDING de la ligne des jours dans dimanche_header_table quand il y a un jour férié
                    dimanche_header_table.setStyle(TableStyle([
                        ('VALIGN', (0, 0), (0, 0), 'MIDDLE'),  # Date centrée verticalement dans sa ligne
                        ('VALIGN', (0, 1), (0, 1), 'MIDDLE'),  # Jours centrés verticalement dans leur ligne
                        ('ALIGN', (0, 0), (0, 0), 'CENTER'),  # Date centrée
                        ('ALIGN', (0, 1), (0, 1), 'CENTER'),  # Jours centrés
                        ('LEFTPADDING', (0, 0), (-1, -1), 2),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 2),
                        ('TOPPADDING', (0, 0), (0, 0), 8),  # Padding pour la date
                        ('BOTTOMPADDING', (0, 0), (0, 0), 4),  # Espacement entre date et jours
                        ('TOPPADDING', (0, 1), (0, 1), 4),  # Espacement entre date et jours
                        ('BOTTOMPADDING', (0, 1), (0, 1), 0),  # Pas de padding en bas des jours quand il y a un jour férié
                    ]))
                    dimanche_ferie_para = Paragraph(
                        f"<font color='#FF0000'>{nom_ferie}</font>",
                        ferie_style
                    )
                else:
                    # Paragraph vide pour maintenir la même hauteur
                    dimanche_ferie_para = Paragraph("", base_style)
                
                # Table avec toujours 2 lignes : dimanche_header_table en haut, jour férié (ou vide) en bas
                # Hauteurs fixes : dimanche_header_table (2.0cm) + ligne férié (0.4cm) = 2.4cm total
                dimanche_header_cell = Table(
                    [[dimanche_header_table], [dimanche_ferie_para]],
                    colWidths=[5.5*cm],
                    rowHeights=[2.0*cm, 0.4*cm]  # Hauteurs fixes pour uniformiser
                )
                dimanche_header_cell.setStyle(TableStyle([
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 2),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 2),
                    ('TOPPADDING', (0, 0), (0, 0), 12),  # Padding pour l'en-tête Dimanche
                    ('BOTTOMPADDING', (0, 0), (0, 0), 12),
                    # Réduire l'espacement entre dimanche_header_table (ligne 0) et jour férié (ligne 1)
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 0),  # Pas de padding en bas de dimanche_header_table
                    ('TOPPADDING', (0, 1), (-1, 1), 0),  # Pas de padding en haut du jour férié
                ]))
                
                # Colonnes 2 et 3 : 5 lignes grises (fusionnées sur 2 colonnes)
                dimanche_notes_rows = []
                for i in range(5):
                    dimanche_notes_rows.append([Paragraph("_" * 60, ligne_note_style)])
                
                dimanche_notes_cell = Table(
                    dimanche_notes_rows,
                    colWidths=[11*cm]  # Largeur de 2 colonnes (5.5cm + 5.5cm)
                )
                dimanche_notes_cell.setStyle(TableStyle([
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 2),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 2),
                    ('TOPPADDING', (0, 0), (-1, -1), 2),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
                ]))
                
                # Structure finale : colonne 0 = en-tête, colonnes 1-2 = lignes grises (fusionnées)
                # Le contenu doit être dans la première colonne du SPAN (colonne 1)
                dimanche_row.append(dimanche_header_cell)  # Colonne 0 (Jeudi)
                dimanche_row.append(dimanche_notes_cell)  # Colonne 1 (Vendredi) - sera fusionnée avec colonne 2
                dimanche_row.append(Paragraph("", base_style))  # Colonne 2 (Samedi) - sera fusionnée avec colonne 1
            else:
                dimanche_row = [Paragraph("", base_style)] * 3
            
            page2_data.append(dimanche_row)
            
            # Trouver l'index de la ligne Dimanche (dernière ligne)
            dimanche_row_index = len(page2_data) - 1
            # Trouver l'index de la ligne des en-têtes (après la ligne de la semaine)
            header_row2_index = 1  # La ligne de la semaine est à l'index 0, les en-têtes sont à l'index 1
            semaine_row2_index = 0  # La ligne de la semaine est à l'index 0
            ligne_vide2_index = 2  # La ligne vide est à l'index 2 (après la semaine et les en-têtes)
            
            # Trouver l'index de la dernière ligne horaire (20h)
            # Il y a 1 ligne vide + 13 lignes horaires (8h-20h), donc la dernière est à l'index ligne_vide2_index + 13
            derniere_ligne_horaire2_index = ligne_vide2_index + len(heures)  # ligne_vide2_index (2) + 13 lignes horaires = 15
            
            # Créer le tableau pour la page 2 (format portrait - colonnes plus étroites)
            # Calculer les hauteurs de lignes : ligne semaine (fixe), ligne en-tête (fixe), autres lignes (auto)
            # Hauteur ligne semaine : texte "2026" avec fontSize=18, leading=20 ≈ 0.7cm
            # Hauteur ligne en-tête : header_cell (2.4cm) + TOPPADDING (0.3cm) = 2.7cm
            page2_row_heights = [None] * len(page2_data)  # None = hauteur automatique
            page2_row_heights[semaine_row2_index] = 0.7*cm  # Hauteur fixe pour la ligne de la semaine (identique à page 1)
            page2_row_heights[header_row2_index] = 2.7*cm  # Hauteur fixe pour la ligne d'en-tête
            # Hauteur de la ligne vide = même hauteur que les lignes horaires (2 lignes de 12 points chacune = 24 points ≈ 0.85cm)
            page2_row_heights[ligne_vide2_index] = 24  # Même hauteur que les lignes horaires (2 lignes de 12 points)
            page2_table = Table(page2_data, colWidths=[5.5*cm, 5.5*cm, 5.5*cm], rowHeights=page2_row_heights)
            page2_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                # Bordures pour toutes les lignes sauf la ligne de la semaine
                ('GRID', (0, 1), (-1, -1), 0.5, colors.HexColor('#CCCCCC')),  # Bordures grises fines (à partir de la ligne 1)
                # Supprimer toutes les bordures de la ligne de la semaine (ligne 0)
                ('LINEABOVE', (0, semaine_row2_index), (-1, semaine_row2_index), 0, colors.white),  # Pas de bordure au-dessus
                ('LINEBELOW', (0, semaine_row2_index), (-1, semaine_row2_index), 0, colors.white),  # Pas de bordure en-dessous
                ('LINEBEFORE', (0, semaine_row2_index), (0, semaine_row2_index), 0, colors.white),  # Pas de bordure à gauche
                ('LINEAFTER', (-1, semaine_row2_index), (-1, semaine_row2_index), 0, colors.white),  # Pas de bordure à droite
                ('LINEBELOW', (0, header_row2_index), (-1, header_row2_index), 1, colors.HexColor('#CCCCCC')),  # Ligne sous les en-têtes
                # Fusionner les colonnes 1 et 2 (Vendredi et Samedi) pour les lignes grises du Dimanche
                ('SPAN', (1, dimanche_row_index), (2, dimanche_row_index)),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                # Ajouter un espacement en haut de la ligne des en-têtes pour décaler le reste du tableau vers le bas
                ('TOPPADDING', (0, header_row2_index), (-1, header_row2_index), 0.3*cm),
            ]))
            
            elements.append(page2_table)
            
            # Saut de page entre les semaines (sauf pour la dernière)
            if semaine != semaines[-1]:
                elements.append(PageBreak())
        
        # Générer le PDF
        doc.build(elements)
        buffer.seek(0)
        
        response = make_response(buffer.read())
        response.headers['Content-Type'] = 'application/pdf'
        # Nom de fichier différent pour indiquer que c'est la version multilingue
        response.headers['Content-Disposition'] = f'attachment; filename=agenda_semainier_2026_multilang_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
        
        return response
    
    except Exception as e:
        error_msg = str(e)
        error_trace = traceback.format_exc()
        
        # #region agent log
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps({
                'timestamp': datetime.now().isoformat(),
                'location': 'projet18_routes.py:export_pdf_multilang:error',
                'message': 'Erreur generation PDF multilingue',
                'data': {'error': error_msg, 'traceback': error_trace},
                'sessionId': 'debug-session',
                'runId': 'run1',
                'hypothesisId': 'E'
            }) + '\n')
        # #endregion
        
        raise

