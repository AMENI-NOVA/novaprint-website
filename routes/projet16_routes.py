"""
Routes pour le Projet 16 - GMAO
"""
from flask import Blueprint, render_template, request, jsonify, Response
import pdfkit
from datetime import datetime
from logic.projet16 import (
    get_operateurs_disponibles,
    get_machines_disponibles,
    get_articles_disponibles,
    search_operateurs,
    search_postes,
    search_articles,
    get_operateur_by_id,
    create_demande_intervention,
    update_demande_intervention,
    delete_demande_intervention,
    update_reparation,
    update_reparation_status,
    create_reparation_direct,
    delete_reparation,
    get_all_demandes,
    get_demande_by_id,
    get_machines,
    add_article_to_reparation,
    update_article_quantite,
    delete_article_from_reparation,
    get_articles_by_fiche,
    save_articles_for_fiche
)

projet16_bp = Blueprint('projet16', __name__, url_prefix='/projet16')

@projet16_bp.route('/')
def index():
    """Page principale GMAO"""
    operateurs = get_operateurs_disponibles()
    machines = get_machines_disponibles()
    articles = get_articles_disponibles()
    return render_template('projet16.html', operateurs=operateurs, machines=machines, articles=articles)

@projet16_bp.route('/api/search_operateurs')
def api_search_operateurs():
    """API pour rechercher des opérateurs (pour Select2)"""
    try:
        query = request.args.get('q', '')
        operateurs = search_operateurs(query)
        return jsonify({"results": operateurs})
    except Exception as e:
        print(f"[ERREUR API] Erreur dans api_search_operateurs: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@projet16_bp.route('/api/search_postes')
def api_search_postes():
    """API pour rechercher des postes/machines (pour Select2)"""
    try:
        query = request.args.get('q', '')
        postes = search_postes(query)
        return jsonify({"results": postes})
    except Exception as e:
        print(f"[ERREUR API] Erreur dans api_search_postes: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@projet16_bp.route('/api/search_articles')
def api_search_articles():
    """API pour rechercher des articles/pièces détachées (pour Select2)"""
    try:
        query = request.args.get('q', '')
        articles = search_articles(query)
        return jsonify({"results": articles})
    except Exception as e:
        print(f"[ERREUR API] Erreur dans api_search_articles: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@projet16_bp.route('/api/get_operateur/<int:matricule>')
def api_get_operateur(matricule):
    """API pour récupérer un opérateur par son matricule"""
    try:
        operateur = get_operateur_by_id(matricule)
        if operateur:
            return jsonify(operateur)
        return jsonify({"error": "Opérateur non trouvé"}), 404
    except Exception as e:
        print(f"[ERREUR API] Erreur dans api_get_operateur: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@projet16_bp.route('/api/create_demande', methods=['POST'])
def api_create_demande():
    """API pour créer une nouvelle demande d'intervention"""
    try:
        data = request.get_json()
        
        # Validation des champs obligatoires
        required_fields = ['dte_dem_in', 'matr_op_dem', 'postes_reel', 'id_emach']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({"error": f"Le champ {field} est obligatoire"}), 400
        
        # Créer la demande
        demande_id = create_demande_intervention(data)
        
        if demande_id:
            return jsonify({
                "success": True,
                "id": demande_id,
                "message": "Demande d'intervention créée avec succès"
            })
        else:
            return jsonify({"error": "Erreur lors de la création de la demande"}), 500
            
    except Exception as e:
        print(f"[ERREUR API] Erreur dans api_create_demande: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@projet16_bp.route('/api/update_demande/<int:demande_id>', methods=['POST'])
def api_update_demande(demande_id):
    """API pour modifier une demande d'intervention"""
    try:
        data = request.get_json()
        
        # Validation des champs obligatoires
        required_fields = ['dte_dem_in', 'matr_op_dem', 'postes_reel', 'id_emach']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({"error": f"Le champ {field} est obligatoire"}), 400
        
        # Mettre à jour la demande
        success = update_demande_intervention(demande_id, data)
        
        if success:
            return jsonify({
                "success": True,
                "message": "Demande d'intervention modifiée avec succès"
            })
        else:
            return jsonify({"error": "Erreur lors de la modification de la demande"}), 500
            
    except Exception as e:
        print(f"[ERREUR API] Erreur dans api_update_demande: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@projet16_bp.route('/api/delete_demande/<int:demande_id>', methods=['DELETE'])
def api_delete_demande(demande_id):
    """API pour supprimer une demande d'intervention"""
    try:
        success = delete_demande_intervention(demande_id)
        
        if success:
            return jsonify({
                "success": True,
                "message": "Demande d'intervention supprimée avec succès"
            })
        else:
            return jsonify({"error": "Erreur lors de la suppression de la demande"}), 500
            
    except Exception as e:
        print(f"[ERREUR API] Erreur dans api_delete_demande: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@projet16_bp.route('/api/update_reparation/<int:demande_id>', methods=['POST'])
def api_update_reparation(demande_id):
    """API pour ajouter/mettre à jour les informations de réparation"""
    try:
        data = request.get_json()
        print(f"[DEBUG API] update_reparation appelé pour demande_id={demande_id}")
        print(f"[DEBUG API] Données reçues: {data}")
        
        if not data:
            return jsonify({"error": "Aucune donnée reçue"}), 400
        
        # Validation des champs obligatoires
        required_fields = ['dte_deb', 'mat_inter', 'postes_reel', 'nat']
        for field in required_fields:
            if field not in data or not data[field]:
                print(f"[DEBUG API] Champ manquant ou vide: {field}")
                return jsonify({"error": f"Le champ {field} est obligatoire"}), 400
        
        print(f"[DEBUG API] Validation OK, appel de update_reparation...")
        # Mettre à jour la réparation
        success = update_reparation(demande_id, data)
        
        if success:
            print(f"[DEBUG API] update_reparation réussi pour demande_id={demande_id}")
            return jsonify({
                "success": True,
                "message": "Réparation enregistrée avec succès"
            })
        else:
            print(f"[DEBUG API] update_reparation a retourné False pour demande_id={demande_id}")
            return jsonify({"error": "Erreur lors de l'enregistrement de la réparation"}), 500
            
    except Exception as e:
        print(f"[ERREUR API] Erreur dans api_update_reparation pour demande_id={demande_id}: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@projet16_bp.route('/api/create_reparation_direct', methods=['POST'])
def api_create_reparation_direct():
    """API pour créer une réparation directe (sans demande d'intervention préalable)"""
    try:
        data = request.get_json()
        
        # Validation des champs obligatoires
        required_fields = ['dte_deb', 'mat_inter', 'postes_reel', 'nat']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({"error": f"Le champ {field} est obligatoire"}), 400
        
        # Créer la réparation directe
        new_id = create_reparation_direct(data)
        
        if new_id:
            return jsonify({
                "success": True,
                "message": "Réparation créée avec succès",
                "id": new_id
            })
        else:
            return jsonify({"error": "Erreur lors de la création de la réparation"}), 500
            
    except Exception as e:
        print(f"[ERREUR API] Erreur dans api_create_reparation_direct: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@projet16_bp.route('/api/update_reparation_status/<int:demande_id>', methods=['POST'])
def api_update_reparation_status(demande_id):
    """API pour mettre à jour le statut d'une réparation"""
    try:
        data = request.get_json()
        
        # Validation des champs obligatoires
        required_fields = ['dte_deb', 'mat_inter', 'postes_reel', 'nat', 'statut']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({"error": f"Le champ {field} est obligatoire"}), 400
        
        # Validation du statut
        valid_statuts = ['cloturer', 'en_attente', 'temporaire']
        if data.get('statut') not in valid_statuts:
            return jsonify({"error": f"Statut invalide. Doit être l'un de: {', '.join(valid_statuts)}"}), 400
        
        # Mettre à jour la réparation avec le nouveau statut
        success = update_reparation_status(demande_id, data)
        
        if success:
            return jsonify({
                "success": True,
                "message": "Statut de réparation mis à jour avec succès"
            })
        else:
            return jsonify({"error": "Erreur lors de la mise à jour du statut"}), 500
            
    except Exception as e:
        print(f"[ERREUR API] Erreur dans api_update_reparation_status: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@projet16_bp.route('/api/delete_reparation/<int:demande_id>', methods=['DELETE'])
def api_delete_reparation(demande_id):
    """API pour supprimer une réparation (remettre à NULL les champs de réparation)"""
    try:
        success = delete_reparation(demande_id)
        
        if success:
            return jsonify({
                "success": True,
                "message": "Réparation supprimée avec succès"
            })
        else:
            return jsonify({"error": "Erreur lors de la suppression de la réparation"}), 500
            
    except Exception as e:
        print(f"[ERREUR API] Erreur dans api_delete_reparation: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@projet16_bp.route('/api/demandes')
def api_demandes():
    """API pour récupérer toutes les demandes"""
    try:
        demandes = get_all_demandes()
        return jsonify(demandes)
    except Exception as e:
        print(f"[ERREUR API] Erreur dans api_demandes: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@projet16_bp.route('/api/demande/<int:demande_id>')
def api_demande_detail(demande_id):
    """API pour récupérer le détail d'une demande"""
    try:
        demande = get_demande_by_id(demande_id)
        if demande:
            return jsonify(demande)
        return jsonify({"error": "Demande non trouvée"}), 404
    except Exception as e:
        print(f"[ERREUR API] Erreur dans api_demande_detail: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@projet16_bp.route('/api/demande/<int:demande_id>/pdf')
def api_demande_pdf(demande_id):
    """API pour générer un PDF de la demande d'intervention avec la même mise en page que le popup"""
    try:
        demande = get_demande_by_id(demande_id)
        if not demande:
            return jsonify({"error": "Demande non trouvée"}), 404
        
        # Formater la date pour l'affichage (format: JJ/MM/AAAA HH:MM)
        date_display = '-'
        dte_dem_in = demande.get('dte_dem_in')
        if dte_dem_in:
            try:
                # Essayer différents formats de date
                if isinstance(dte_dem_in, str):
                    if 'T' in dte_dem_in:
                        date_obj = datetime.strptime(dte_dem_in, '%Y-%m-%dT%H:%M')
                    elif len(dte_dem_in) == 19:
                        date_obj = datetime.strptime(dte_dem_in, '%Y-%m-%d %H:%M:%S')
                    elif len(dte_dem_in) == 16:
                        date_obj = datetime.strptime(dte_dem_in, '%Y-%m-%d %H:%M')
                    else:
                        date_obj = datetime.strptime(dte_dem_in.split('.')[0], '%Y-%m-%d %H:%M:%S')
                    date_display = date_obj.strftime('%d/%m/%Y %H:%M')
                else:
                    date_display = str(dte_dem_in)
            except Exception as e:
                print(f"[WARNING] Erreur lors du formatage de la date: {e}, valeur: {dte_dem_in}")
                date_display = str(dte_dem_in) if dte_dem_in else '-'
        
        # Déterminer l'état de la machine
        etat_avec_arret_checked = ''
        etat_sans_arret_checked = ''
        if demande.get('id_emach') == 1:
            etat_avec_arret_checked = 'checked'
        elif demande.get('id_emach') == 0:
            etat_sans_arret_checked = 'checked'
        
        # Préparer les données pour le template
        template_data = {
            'date_display': date_display,
            'oper_dem': demande.get('oper_dem', ''),
            'postes_reel': demande.get('postes_reel', ''),
            'etat_avec_arret_checked': etat_avec_arret_checked,
            'etat_sans_arret_checked': etat_sans_arret_checked,
            'dem_in': demande.get('dem_in', '')
        }
        
        # Utiliser reportlab directement pour un meilleur contrôle du rendu
        return _generate_pdf_with_reportlab(demande, date_display, etat_avec_arret_checked, etat_sans_arret_checked)
        
    except Exception as e:
        print(f"[ERREUR API] Erreur dans api_demande_pdf pour demande_id={demande_id}: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

def _generate_pdf_with_reportlab(demande, date_display, etat_avec_arret_checked, etat_sans_arret_checked):
    """Générer PDF avec reportlab"""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_CENTER, TA_LEFT
        from io import BytesIO
    except ImportError as e:
        print(f"[ERREUR] reportlab n'est pas installé: {e}")
        raise ImportError("La bibliothèque reportlab est requise pour générer les PDF. Installez-la avec: pip install reportlab")
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, 
                            rightMargin=2.5*cm, leftMargin=2.5*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    
    styles = getSampleStyleSheet()
    # Titre: 1.8em = environ 25.2pt (base 14pt)
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'],
                                 fontSize=25.2, textColor=colors.HexColor('#e91e63'),
                                 spaceAfter=25, alignment=TA_LEFT, fontName='Helvetica-Bold')
    # Labels: 14px = 14pt
    label_style = ParagraphStyle('LabelStyle', parent=styles['Normal'],
                                 fontSize=14, fontName='Helvetica-Bold',
                                 textColor=colors.black, spaceAfter=8, leading=14)
    # Small: 12.6px = 12.6pt (0.9em de 14px)
    small_style = ParagraphStyle('SmallStyle', parent=styles['Normal'],
                                fontSize=12.6, fontName='Helvetica',
                                textColor=colors.HexColor('#666'), spaceAfter=15, leading=12.6)
    # Description/Input: 14px = 14pt
    description_style = ParagraphStyle('DescriptionStyle', parent=styles['Normal'],
                                     fontSize=14, fontName='Helvetica',
                                     textColor=colors.black, spaceAfter=15, leading=14)
    
    story = []
    
    # Afficher "Version N°Suffixe" en haut à droite si Suffixe > 0
    suffixe = demande.get('suffixe', 0) or 0
    if suffixe > 0:
        version_style = ParagraphStyle('VersionStyle', parent=styles['Normal'],
                                      fontSize=10, fontName='Helvetica',
                                      textColor=colors.HexColor('#666'),
                                      alignment=TA_CENTER)
        version_text = Paragraph(f"Version N°{suffixe}", version_style)
        # Créer une table pour positionner le titre à gauche et la version à droite
        header_table = Table([[Paragraph("📝 Fiche de Demande d'Intervention", title_style), version_text]], 
                            colWidths=[14*cm, 2*cm])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ]))
        story.append(header_table)
    else:
        story.append(Paragraph("📝 Fiche de Demande d'Intervention", title_style))
    
    story.append(Spacer(1, 0.8*cm))
    
    # Date et Heure
    story.append(Paragraph("Date et Heure *", label_style))
    date_text = date_display if date_display and date_display != '-' else ''
    date_table = Table([[Paragraph(date_text, description_style)]], colWidths=[16*cm], rowHeights=[0.8*cm])
    date_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f0f0f0')),
        ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#ddd')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 14),
    ]))
    story.append(date_table)
    story.append(Spacer(1, 0.3*cm))
    
    # Opérateur Demandeur
    story.append(Paragraph("Opérateur Demandeur *", label_style))
    oper_text = demande.get('oper_dem', '') or ''
    op_table = Table([[Paragraph(oper_text, description_style)]], colWidths=[16*cm], rowHeights=[0.8*cm])
    op_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f0f0f0')),
        ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#ddd')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 14),
    ]))
    story.append(op_table)
    story.append(Paragraph("Tapez un nom ou prénom pour rechercher", small_style))
    
    # Machine
    story.append(Paragraph("Machine *", label_style))
    machine_text = demande.get('postes_reel', '') or ''
    machine_table = Table([[Paragraph(machine_text, description_style)]], colWidths=[16*cm], rowHeights=[0.8*cm])
    machine_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f0f0f0')),
        ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#ddd')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 14),
    ]))
    story.append(machine_table)
    story.append(Paragraph("Tapez le nom de la machine pour rechercher", small_style))
    
    # État de la Machine
    story.append(Paragraph("État de la Machine *", label_style))
    
    # Créer des checkboxes avec carrés et bordures
    # Utiliser l'emoji ❌ comme dans le popup
    cross_char = '❌'
    
    # Checkbox "Avec Arrêt"
    checkbox_content_avec = Paragraph(f'<font color="#e91e63" size="18"><b>{cross_char}</b></font>', ParagraphStyle('CrossStyle', parent=styles['Normal'], alignment=TA_CENTER, fontSize=18, textColor=colors.HexColor('#e91e63'))) if etat_avec_arret_checked else Paragraph('', styles['Normal'])
    checkbox_avec_arret = Table([[checkbox_content_avec]], colWidths=[0.8*cm], rowHeights=[0.8*cm])
    checkbox_avec_arret.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.white),
        ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#e91e63') if etat_avec_arret_checked else colors.HexColor('#ddd')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ]))
    
    # Checkbox "Sans Arrêt"
    checkbox_content_sans = Paragraph(f'<font color="#e91e63" size="18"><b>{cross_char}</b></font>', ParagraphStyle('CrossStyle', parent=styles['Normal'], alignment=TA_CENTER, fontSize=18, textColor=colors.HexColor('#e91e63'))) if etat_sans_arret_checked else Paragraph('', styles['Normal'])
    checkbox_sans_arret = Table([[checkbox_content_sans]], colWidths=[0.8*cm], rowHeights=[0.8*cm])
    checkbox_sans_arret.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.white),
        ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#e91e63') if etat_sans_arret_checked else colors.HexColor('#ddd')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ]))
    
    # Créer une table avec les checkboxes et les textes
    etat_table = Table([
        [checkbox_avec_arret, Paragraph("Avec Arrêt", description_style), Spacer(1, 0.5*cm), checkbox_sans_arret, Paragraph("Sans Arrêt", description_style)]
    ], colWidths=[0.8*cm, 3*cm, 1*cm, 0.8*cm, 3*cm])
    etat_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (1, 0), (1, 0), 'LEFT'),
        ('ALIGN', (4, 0), (4, 0), 'LEFT'),
    ]))
    story.append(etat_table)
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph("Indiquez si la machine est arrêtée ou fonctionne encore", small_style))
    
    # Description
    story.append(Paragraph("Description du Problème", label_style))
    description = demande.get('dem_in', '')
    if description:
        description_text = description.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('\n', '<br/>').replace('\r', '')
        desc_para = Paragraph(description_text, description_style)
        desc_table = Table([[desc_para]], colWidths=[16*cm])
    else:
        desc_table = Table([['']], colWidths=[16*cm], rowHeights=[3*cm])
    
    desc_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f0f0f0')),
        ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#ddd')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
    ]))
    story.append(desc_table)
    
    try:
        doc.build(story)
        buffer.seek(0)
        pdf_data = buffer.getvalue()
        buffer.close()
        
        demande_id = demande.get('id', 'unknown')
        response = Response(pdf_data, mimetype='application/pdf')
        response.headers['Content-Disposition'] = f'inline; filename="fiche_demande_{demande_id}.pdf"'
        return response
    except Exception as e:
        buffer.close()
        print(f"[ERREUR] Erreur lors de la génération du PDF avec reportlab: {e}")
        import traceback
        traceback.print_exc()
        raise

@projet16_bp.route('/api/reparation/<int:reparation_id>/pdf')
def api_reparation_pdf(reparation_id):
    """API pour générer un PDF de la fiche de réparation avec la même mise en page que le popup"""
    try:
        reparation = get_demande_by_id(reparation_id)
        if not reparation:
            return jsonify({"error": "Réparation non trouvée"}), 404
        
        # Vérifier que c'est bien une réparation (a des données de réparation)
        if not reparation.get('dte_deb') and not reparation.get('mat_inter'):
            return jsonify({"error": "Cette fiche n'est pas une réparation"}), 400
        
        # Formater les dates pour l'affichage
        dte_deb_display = '-'
        dte_deb = reparation.get('dte_deb')
        if dte_deb:
            try:
                if isinstance(dte_deb, str):
                    if 'T' in dte_deb:
                        date_obj = datetime.strptime(dte_deb, '%Y-%m-%dT%H:%M')
                    elif len(dte_deb) == 19:
                        date_obj = datetime.strptime(dte_deb, '%Y-%m-%d %H:%M:%S')
                    elif len(dte_deb) == 16:
                        date_obj = datetime.strptime(dte_deb, '%Y-%m-%d %H:%M')
                    else:
                        date_obj = datetime.strptime(dte_deb.split('.')[0], '%Y-%m-%d %H:%M:%S')
                    dte_deb_display = date_obj.strftime('%d/%m/%Y %H:%M')
                else:
                    dte_deb_display = str(dte_deb)
            except Exception as e:
                print(f"[WARNING] Erreur lors du formatage de dte_deb: {e}")
                dte_deb_display = str(dte_deb) if dte_deb else '-'
        
        dte_fin_display = '-'
        dte_fin = reparation.get('dte_fin')
        if dte_fin:
            try:
                if isinstance(dte_fin, str):
                    if 'T' in dte_fin:
                        date_obj = datetime.strptime(dte_fin, '%Y-%m-%dT%H:%M')
                    elif len(dte_fin) == 19:
                        date_obj = datetime.strptime(dte_fin, '%Y-%m-%d %H:%M:%S')
                    elif len(dte_fin) == 16:
                        date_obj = datetime.strptime(dte_fin, '%Y-%m-%d %H:%M')
                    else:
                        date_obj = datetime.strptime(dte_fin.split('.')[0], '%Y-%m-%d %H:%M:%S')
                    dte_fin_display = date_obj.strftime('%d/%m/%Y %H:%M')
                else:
                    dte_fin_display = str(dte_fin)
            except Exception as e:
                print(f"[WARNING] Erreur lors du formatage de dte_fin: {e}")
                dte_fin_display = str(dte_fin) if dte_fin else '-'
        
        # Nature de la réparation
        nat = reparation.get('nat', '')
        nat_display = 'Mécanique' if nat == 'Mec' else 'Électrique' if nat == 'Elec' else nat or '-'
        
        # Générer le PDF de réparation
        return _generate_reparation_pdf(reparation, dte_deb_display, dte_fin_display, nat_display)
        
    except Exception as e:
        print(f"[ERREUR API] Erreur dans api_reparation_pdf pour reparation_id={reparation_id}: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

def _generate_reparation_pdf(reparation, dte_deb_display, dte_fin_display, nat_display):
    """Générer PDF de réparation avec reportlab"""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_CENTER, TA_LEFT
        from io import BytesIO
    except ImportError as e:
        print(f"[ERREUR] reportlab n'est pas installé: {e}")
        raise ImportError("La bibliothèque reportlab est requise pour générer les PDF. Installez-la avec: pip install reportlab")
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, 
                            rightMargin=2.5*cm, leftMargin=2.5*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    
    styles = getSampleStyleSheet()
    # Titre avec couleur violette comme dans le popup
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'],
                                 fontSize=25.2, textColor=colors.HexColor('#9c27b0'),
                                 spaceAfter=25, alignment=TA_LEFT, fontName='Helvetica-Bold')
    # Labels
    label_style = ParagraphStyle('LabelStyle', parent=styles['Normal'],
                                 fontSize=14, fontName='Helvetica-Bold',
                                 textColor=colors.black, spaceAfter=8, leading=14)
    # Small
    small_style = ParagraphStyle('SmallStyle', parent=styles['Normal'],
                                fontSize=12.6, fontName='Helvetica',
                                textColor=colors.HexColor('#666'), spaceAfter=15, leading=12.6)
    # Description/Input
    description_style = ParagraphStyle('DescriptionStyle', parent=styles['Normal'],
                                     fontSize=14, fontName='Helvetica',
                                     textColor=colors.black, spaceAfter=15, leading=14)
    
    story = []
    # Le Suffixe n'est pas affiché pour les réparations (uniquement pour les demandes d'intervention)
    story.append(Paragraph("🔧 Fiche de Réparation", title_style))
    story.append(Spacer(1, 0.8*cm))
    
    # Machine Concernée
    story.append(Paragraph("Machine Concernée *", label_style))
    machine_text = reparation.get('postes_reel', '') or ''
    machine_table = Table([[Paragraph(machine_text, description_style)]], colWidths=[16*cm], rowHeights=[0.8*cm])
    machine_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f0f0f0')),
        ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#ddd')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 14),
    ]))
    story.append(machine_table)
    story.append(Paragraph("Machine sur laquelle la réparation sera effectuée", small_style))
    
    # Intervenant
    story.append(Paragraph("Intervenant *", label_style))
    intervenant_text = reparation.get('intervenant', '') or ''
    if reparation.get('mat_inter'):
        intervenant_text += f" (Matricule: {reparation.get('mat_inter')})"
    inter_table = Table([[Paragraph(intervenant_text, description_style)]], colWidths=[16*cm], rowHeights=[0.8*cm])
    inter_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f0f0f0')),
        ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#ddd')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 14),
    ]))
    story.append(inter_table)
    
    # Dates côte à côte
    story.append(Spacer(1, 0.3*cm))
    dates_row = [
        [Paragraph("Date/Heure Début *", label_style), Paragraph("Date/Heure Fin", label_style)]
    ]
    dates_header = Table(dates_row, colWidths=[8*cm, 8*cm])
    dates_header.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(dates_header)
    
    dates_values = [
        [Paragraph(dte_deb_display, description_style), Paragraph(dte_fin_display, description_style)]
    ]
    dates_table = Table(dates_values, colWidths=[8*cm, 8*cm], rowHeights=[0.8*cm])
    dates_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f0f0f0')),
        ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#ddd')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 14),
    ]))
    story.append(dates_table)
    
    # Temps réel
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph("Temps Réel", label_style))
    tps_reel_text = reparation.get('tps_reel', '') or '-'
    tps_table = Table([[Paragraph(tps_reel_text, description_style)]], colWidths=[16*cm], rowHeights=[0.8*cm])
    tps_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f0f0f0')),
        ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#ddd')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 14),
    ]))
    story.append(tps_table)
    
    # Nature de la réparation
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph("Nature *", label_style))
    
    # Checkbox pour la nature (violette comme dans le popup)
    cross_char = '✖️'
    nat_mec_checked = nat_display == 'Mécanique'
    nat_elec_checked = nat_display == 'Électrique'
    
    checkbox_mec = Paragraph(f'<font color="#9c27b0" size="18"><b>{cross_char}</b></font>', ParagraphStyle('CrossStyle', parent=styles['Normal'], alignment=TA_CENTER, fontSize=18, textColor=colors.HexColor('#9c27b0'))) if nat_mec_checked else Paragraph('', styles['Normal'])
    checkbox_mec_table = Table([[checkbox_mec]], colWidths=[0.8*cm], rowHeights=[0.8*cm])
    checkbox_mec_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.white),
        ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#9c27b0') if nat_mec_checked else colors.HexColor('#ddd')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ]))
    
    checkbox_elec = Paragraph(f'<font color="#9c27b0" size="18"><b>{cross_char}</b></font>', ParagraphStyle('CrossStyle', parent=styles['Normal'], alignment=TA_CENTER, fontSize=18, textColor=colors.HexColor('#9c27b0'))) if nat_elec_checked else Paragraph('', styles['Normal'])
    checkbox_elec_table = Table([[checkbox_elec]], colWidths=[0.8*cm], rowHeights=[0.8*cm])
    checkbox_elec_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.white),
        ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#9c27b0') if nat_elec_checked else colors.HexColor('#ddd')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ]))
    
    nat_table = Table([
        [checkbox_mec_table, Paragraph("Mécanique", description_style), Spacer(1, 0.5*cm), checkbox_elec_table, Paragraph("Électrique", description_style)]
    ], colWidths=[0.8*cm, 3*cm, 1*cm, 0.8*cm, 3*cm])
    nat_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (1, 0), (1, 0), 'LEFT'),
        ('ALIGN', (4, 0), (4, 0), 'LEFT'),
    ]))
    story.append(nat_table)
    story.append(Paragraph("Type de réparation effectuée", small_style))
    
    # Articles / Pièces Détachées
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph("🔩 Articles / Pièces Détachées", label_style))
    
    articles = reparation.get('articles', [])
    if articles and len(articles) > 0:
        # En-tête du tableau
        articles_data = [['N°', 'Désignation', 'Quantité']]
        for idx, art in enumerate(articles, 1):
            articles_data.append([
                str(idx),
                art.get('designation', '') or '',
                str(art.get('quantite', 0))
            ])
        
        articles_table = Table(articles_data, colWidths=[1.5*cm, 12*cm, 2.5*cm])
        articles_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2196F3')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#ddd')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ]))
        story.append(articles_table)
    else:
        no_articles = Table([['Aucun article ajouté']], colWidths=[16*cm])
        no_articles.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#999')),
            ('FONTSTYLE', (0, 0), (-1, -1), 'ITALIC'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 20),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 20),
        ]))
        story.append(no_articles)
    
    try:
        doc.build(story)
        buffer.seek(0)
        pdf_data = buffer.getvalue()
        buffer.close()
        
        reparation_id = reparation.get('id', 'unknown')
        response = Response(pdf_data, mimetype='application/pdf')
        response.headers['Content-Disposition'] = f'inline; filename="fiche_reparation_{reparation_id}.pdf"'
        return response
    except Exception as e:
        buffer.close()
        print(f"[ERREUR] Erreur lors de la génération du PDF de réparation: {e}")
        import traceback
        traceback.print_exc()
        raise

@projet16_bp.route('/api/machines')
def api_machines():
    """API pour récupérer toutes les machines"""
    try:
        machines = get_machines()
        return jsonify(machines)
    except Exception as e:
        print(f"[ERREUR API] Erreur dans api_machines: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# ========== ROUTES API POUR LES ARTICLES ==========

@projet16_bp.route('/api/articles/<int:id_web_gmao>')
def api_get_articles(id_web_gmao):
    """API pour récupérer les articles d'une fiche (détecte automatiquement si c'est une demande ou une réparation directe)"""
    try:
        from db import get_db_cursor
        
        # Détecter si c'est une demande dans WEB_GMAO ou une réparation directe dans WEB_GMAO_REPARATION
        with get_db_cursor() as cursor:
            cursor.execute("SELECT ID FROM WEB_GMAO WHERE ID = ?", (id_web_gmao,))
            demande_exists = cursor.fetchone()
            
            if demande_exists:
                # C'est une réparation liée à une demande
                articles = get_articles_by_fiche(id_web_gmao=id_web_gmao)
            else:
                # Vérifier si c'est une réparation directe
                cursor.execute("SELECT ID FROM WEB_GMAO_REPARATION WHERE ID = ?", (id_web_gmao,))
                reparation_directe = cursor.fetchone()
                
                if reparation_directe:
                    # C'est une réparation directe
                    articles = get_articles_by_fiche(id_web_gmao_reparation=id_web_gmao)
                else:
                    return jsonify({"error": f"L'ID {id_web_gmao} n'existe ni dans WEB_GMAO ni dans WEB_GMAO_REPARATION"}), 404
        
        return jsonify(articles)
    except Exception as e:
        print(f"[ERREUR API] Erreur dans api_get_articles: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@projet16_bp.route('/api/save_articles/<int:id_web_gmao>', methods=['POST'])
def api_save_articles(id_web_gmao):
    """API pour sauvegarder tous les articles d'une fiche (détecte automatiquement si c'est une demande ou une réparation directe)"""
    try:
        from db import get_db_cursor
        
        # Détecter si c'est une demande dans WEB_GMAO ou une réparation directe dans WEB_GMAO_REPARATION
        with get_db_cursor() as cursor:
            cursor.execute("SELECT ID FROM WEB_GMAO WHERE ID = ?", (id_web_gmao,))
            demande_exists = cursor.fetchone()
            
            if demande_exists:
                # C'est une réparation liée à une demande
                data = request.get_json()
                articles = data.get('articles', [])
                saved_articles = save_articles_for_fiche(id_web_gmao=id_web_gmao, articles_data=articles)
            else:
                # Vérifier si c'est une réparation directe
                cursor.execute("SELECT ID FROM WEB_GMAO_REPARATION WHERE ID = ?", (id_web_gmao,))
                reparation_directe = cursor.fetchone()
                
                if reparation_directe:
                    # C'est une réparation directe
                    data = request.get_json()
                    articles = data.get('articles', [])
                    saved_articles = save_articles_for_fiche(id_web_gmao_reparation=id_web_gmao, articles_data=articles)
                else:
                    return jsonify({"error": f"L'ID {id_web_gmao} n'existe ni dans WEB_GMAO ni dans WEB_GMAO_REPARATION"}), 404
        
        if saved_articles is not None:
            return jsonify({
                "success": True,
                "message": "Articles sauvegardés avec succès",
                "articles": saved_articles
            })
        else:
            return jsonify({"error": "Erreur lors de la sauvegarde des articles"}), 500
            
    except Exception as e:
        print(f"[ERREUR API] Erreur dans api_save_articles: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@projet16_bp.route('/api/save_articles_reparation/<int:id_web_gmao_reparation>', methods=['POST'])
def api_save_articles_reparation(id_web_gmao_reparation):
    """API pour sauvegarder tous les articles d'une fiche de réparation directe"""
    try:
        data = request.get_json()
        articles = data.get('articles', [])
        
        saved_articles = save_articles_for_fiche(id_web_gmao_reparation=id_web_gmao_reparation, articles_data=articles)
        
        if saved_articles is not None:
            return jsonify({
                "success": True,
                "message": "Articles sauvegardés avec succès",
                "articles": saved_articles
            })
        else:
            return jsonify({"error": "Erreur lors de la sauvegarde des articles"}), 500
            
    except Exception as e:
        print(f"[ERREUR API] Erreur dans api_save_articles_reparation: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@projet16_bp.route('/api/add_article', methods=['POST'])
def api_add_article():
    """API pour ajouter un article à une fiche"""
    try:
        data = request.get_json()
        
        # Soit id_web_gmao (réparation liée à une demande) soit id_web_gmao_reparation (réparation directe)
        if 'id_gs_articles' not in data or 'quantite' not in data:
            return jsonify({"error": "Les champs id_gs_articles et quantite sont obligatoires"}), 400
        
        if 'id_web_gmao' not in data and 'id_web_gmao_reparation' not in data:
            return jsonify({"error": "Soit id_web_gmao soit id_web_gmao_reparation doit être fourni"}), 400
        
        new_id = add_article_to_reparation(
            id_web_gmao=data.get('id_web_gmao'),
            id_web_gmao_reparation=data.get('id_web_gmao_reparation'),
            id_gs_articles=data['id_gs_articles'],
            quantite=data['quantite']
        )
        
        return jsonify({
            "success": True,
            "id": new_id,
            "message": "Article ajouté avec succès"
        })
            
    except Exception as e:
        print(f"[ERREUR API] Erreur dans api_add_article: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@projet16_bp.route('/api/delete_article/<int:article_id>', methods=['DELETE'])
def api_delete_article(article_id):
    """API pour supprimer un article"""
    try:
        success = delete_article_from_reparation(article_id)
        
        if success:
            return jsonify({
                "success": True,
                "message": "Article supprimé avec succès"
            })
        else:
            return jsonify({"error": "Erreur lors de la suppression de l'article"}), 500
            
    except Exception as e:
        print(f"[ERREUR API] Erreur dans api_delete_article: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
