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
        
        # Validation des champs obligatoires
        required_fields = ['dte_deb', 'mat_inter', 'postes_reel', 'nat']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({"error": f"Le champ {field} est obligatoire"}), 400
        
        # Mettre à jour la réparation
        success = update_reparation(demande_id, data)
        
        if success:
            return jsonify({
                "success": True,
                "message": "Réparation enregistrée avec succès"
            })
        else:
            return jsonify({"error": "Erreur lors de l'enregistrement de la réparation"}), 500
            
    except Exception as e:
        print(f"[ERREUR API] Erreur dans api_update_reparation: {e}")
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
        if demande.get('dte_dem_in'):
            try:
                date_obj = datetime.strptime(demande['dte_dem_in'], '%Y-%m-%dT%H:%M')
                date_display = date_obj.strftime('%d/%m/%Y %H:%M')
            except:
                try:
                    # Essayer un autre format si nécessaire
                    date_obj = datetime.strptime(demande['dte_dem_in'], '%Y-%m-%d %H:%M:%S')
                    date_display = date_obj.strftime('%d/%m/%Y %H:%M')
                except:
                    date_display = demande.get('dte_dem_in', '-')
        
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
        print(f"[ERREUR API] Erreur dans api_demande_pdf: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

def _generate_pdf_with_reportlab(demande, date_display, etat_avec_arret_checked, etat_sans_arret_checked):
    """Fallback: générer PDF avec reportlab si pdfkit n'est pas disponible"""
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    from io import BytesIO
    
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
    story.append(Paragraph("📝 Fiche de Demande d'Intervention", title_style))
    story.append(Spacer(1, 0.8*cm))
    
    # Date et Heure
    story.append(Paragraph("Date et Heure *", label_style))
    date_table = Table([[Paragraph(date_display, description_style)]], colWidths=[16*cm], rowHeights=[0.8*cm])
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
    op_table = Table([[Paragraph(demande.get('oper_dem', ''), description_style)]], colWidths=[16*cm], rowHeights=[0.8*cm])
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
    machine_table = Table([[Paragraph(demande.get('postes_reel', ''), description_style)]], colWidths=[16*cm], rowHeights=[0.8*cm])
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
    checkbox_content_avec = Paragraph(f'<font color="#e91e63" size="18"><b>{cross_char}</b></font>', ParagraphStyle('CrossStyle', parent=styles['Normal'], alignment=1, fontSize=18, textColor=colors.HexColor('#e91e63'))) if etat_avec_arret_checked else ''
    checkbox_avec_arret = Table([[checkbox_content_avec]], colWidths=[0.8*cm], rowHeights=[0.8*cm])
    checkbox_avec_arret.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.white),
        ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#e91e63') if etat_avec_arret_checked else colors.HexColor('#ddd')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ]))
    
    # Checkbox "Sans Arrêt"
    checkbox_content_sans = Paragraph(f'<font color="#e91e63" size="18"><b>{cross_char}</b></font>', ParagraphStyle('CrossStyle', parent=styles['Normal'], alignment=1, fontSize=18, textColor=colors.HexColor('#e91e63'))) if etat_sans_arret_checked else ''
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
    
    doc.build(story)
    buffer.seek(0)
    pdf_data = buffer.getvalue()
    buffer.close()
    
    demande_id = demande.get('id', 'unknown')
    response = Response(pdf_data, mimetype='application/pdf')
    response.headers['Content-Disposition'] = f'inline; filename="fiche_demande_{demande_id}.pdf"'
    return response

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
    """API pour récupérer les articles d'une fiche de réparation"""
    try:
        articles = get_articles_by_fiche(id_web_gmao)
        return jsonify(articles)
    except Exception as e:
        print(f"[ERREUR API] Erreur dans api_get_articles: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@projet16_bp.route('/api/save_articles/<int:id_web_gmao>', methods=['POST'])
def api_save_articles(id_web_gmao):
    """API pour sauvegarder tous les articles d'une fiche"""
    try:
        data = request.get_json()
        articles = data.get('articles', [])
        
        saved_articles = save_articles_for_fiche(id_web_gmao, articles)
        
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

@projet16_bp.route('/api/add_article', methods=['POST'])
def api_add_article():
    """API pour ajouter un article à une fiche"""
    try:
        data = request.get_json()
        
        required_fields = ['id_web_gmao', 'id_gs_articles', 'quantite']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Le champ {field} est obligatoire"}), 400
        
        new_id = add_article_to_reparation(
            data['id_web_gmao'],
            data['id_gs_articles'],
            data['quantite']
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
