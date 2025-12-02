"""
Routes pour le Projet 12 - Registre de suivi des Produits Non Conformes et des Réclamations Clients
"""
from flask import Blueprint, render_template, request, jsonify, make_response
from logic.projet12 import (
    get_liste_references,
    get_liste_clients,
    get_liste_numeros,
    get_info_commande,
    ajouter_enregistrement,
    get_liste_enregistrements,
    supprimer_enregistrement,
    modifier_enregistrement,
    get_enregistrement_par_id,
    generer_pdf_fiche,
    # Statistiques
    get_statistiques_kpi,
    get_evolution_temporelle,
    get_top_clients,
    get_analyse_causes,
    get_comparaison_periodes
)
from db import get_controle_qualite_by_numero

projet12_bp = Blueprint('projet12', __name__)

@projet12_bp.route('/projet12')
@projet12_bp.route('/projet12/ListeDesFichiers')
@projet12_bp.route('/projet12/SaisieNouveauFichier')
@projet12_bp.route('/projet12/Statistiques')
def projet12():
    """
    Page principale du Projet 12
    Gère les sections avec URLs dynamiques et le modal de saisie
    """
    return render_template('projet12.html')

@projet12_bp.route('/projet12/get_references', methods=['GET'])
def get_references():
    """
    API pour récupérer la liste des références
    """
    try:
        references = get_liste_references()
        return jsonify({'success': True, 'data': references})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@projet12_bp.route('/projet12/get_clients', methods=['GET'])
def get_clients():
    """
    API pour récupérer la liste des clients
    """
    try:
        clients = get_liste_clients()
        return jsonify({'success': True, 'data': clients})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@projet12_bp.route('/projet12/get_numeros', methods=['GET'])
def get_numeros():
    """
    API pour récupérer la liste des numéros de commandes
    """
    try:
        numeros = get_liste_numeros()
        return jsonify({'success': True, 'data': numeros})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@projet12_bp.route('/projet12/get_info_commande/<numero>', methods=['GET'])
def get_info_commande_route(numero):
    """
    API pour récupérer les informations d'une commande (client et référence)
    """
    try:
        info = get_info_commande(numero)
        if info:
            return jsonify({'success': True, 'data': info})
        else:
            return jsonify({'success': False, 'error': 'Commande non trouvée'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@projet12_bp.route('/projet12/ajouter', methods=['POST'])
def ajouter():
    """
    API pour ajouter un nouvel enregistrement
    """
    try:
        data = request.get_json()
        
        success, message = ajouter_enregistrement(
            data.get('date'),
            data.get('type'),
            data.get('nc'),
            data.get('des_nc'),
            data.get('cause'),
            data.get('numero_commandes'),
            data.get('reference_commandes'),
            data.get('raisoctri_societes'),
            data.get('qte_comm_commandes'),
            data.get('qte_nc'),
            data.get('carac_nc')
        )
        
        if success:
            return jsonify({'success': True, 'message': message})
        else:
            return jsonify({'success': False, 'error': message}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@projet12_bp.route('/projet12/liste', methods=['GET'])
def liste():
    """
    API pour récupérer la liste des enregistrements
    """
    try:
        type_registre = request.args.get('type')
        enregistrements = get_liste_enregistrements(type_registre)
        return jsonify({'success': True, 'data': enregistrements})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@projet12_bp.route('/projet12/supprimer/<int:id>', methods=['DELETE'])
def supprimer(id):
    """
    API pour supprimer un enregistrement
    """
    try:
        success, message = supprimer_enregistrement(id)
        
        if success:
            return jsonify({'success': True, 'message': message})
        else:
            return jsonify({'success': False, 'error': message}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@projet12_bp.route('/projet12/modifier/<int:id>', methods=['PUT'])
def modifier(id):
    """
    API pour modifier un enregistrement
    """
    try:
        data = request.get_json()
        
        success, message = modifier_enregistrement(
            id,
            data.get('date'),
            data.get('type'),
            data.get('nc'),
            data.get('des_nc'),
            data.get('cause'),
            data.get('numero_commandes'),
            data.get('reference_commandes'),
            data.get('raisoctri_societes'),
            data.get('qte_comm_commandes'),
            data.get('qte_nc'),
            data.get('carac_nc')
        )
        
        if success:
            return jsonify({'success': True, 'message': message})
        else:
            return jsonify({'success': False, 'error': message}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@projet12_bp.route('/projet12/pdf/<int:id>', methods=['GET'])
def telecharger_pdf(id):
    """
    Génère et télécharge le PDF d'une fiche
    """
    try:
        pdf_content, filename = generer_pdf_fiche(id)
        
        if pdf_content:
            response = make_response(pdf_content)
            response.headers['Content-Type'] = 'application/pdf'
            response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
        else:
            return jsonify({'success': False, 'error': 'Enregistrement non trouvé'}), 404
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@projet12_bp.route('/projet12/controle_qualite/<numero>', methods=['GET'])
def get_controle_qualite_numero(numero):
    """
    Récupère le contrôle qualité du Projet 10 associé à un numéro de commande
    """
    try:
        controle = get_controle_qualite_by_numero(numero)
        
        if controle:
            # Formater la date pour l'affichage
            if controle.get('date_controle'):
                controle['date_controle'] = controle['date_controle'].strftime('%d/%m/%Y') if hasattr(controle['date_controle'], 'strftime') else str(controle['date_controle'])
            if controle.get('date_creation'):
                controle['date_creation'] = controle['date_creation'].strftime('%d/%m/%Y %H:%M') if hasattr(controle['date_creation'], 'strftime') else str(controle['date_creation'])
            
            return jsonify({'success': True, 'data': controle})
        else:
            return jsonify({'success': False, 'error': 'Aucun contrôle qualité trouvé pour ce numéro de dossier'}), 404
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================================================
# ROUTES API STATISTIQUES
# ============================================================================

@projet12_bp.route('/projet12/api/stats/kpi', methods=['GET'])
def api_stats_kpi():
    """
    API pour récupérer les indicateurs clés (KPI)
    """
    try:
        date_debut = request.args.get('date_debut')
        date_fin = request.args.get('date_fin')
        
        stats = get_statistiques_kpi(date_debut, date_fin)
        
        if stats:
            return jsonify({'success': True, 'data': stats})
        else:
            return jsonify({'success': False, 'error': 'Erreur lors de la récupération des KPI'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@projet12_bp.route('/projet12/api/stats/evolution', methods=['GET'])
def api_stats_evolution():
    """
    API pour récupérer l'évolution temporelle
    """
    try:
        nb_mois = int(request.args.get('nb_mois', 6))
        
        evolution = get_evolution_temporelle(nb_mois)
        return jsonify({'success': True, 'data': evolution})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@projet12_bp.route('/projet12/api/stats/top-clients', methods=['GET'])
def api_stats_top_clients():
    """
    API pour récupérer le top clients
    """
    try:
        limit = int(request.args.get('limit', 10))
        date_debut = request.args.get('date_debut')
        date_fin = request.args.get('date_fin')
        
        clients = get_top_clients(limit, date_debut, date_fin)
        return jsonify({'success': True, 'data': clients})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@projet12_bp.route('/projet12/api/stats/causes', methods=['GET'])
def api_stats_causes():
    """
    API pour récupérer l'analyse des causes
    """
    try:
        limit = int(request.args.get('limit', 10))
        date_debut = request.args.get('date_debut')
        date_fin = request.args.get('date_fin')
        
        causes = get_analyse_causes(limit, date_debut, date_fin)
        return jsonify({'success': True, 'data': causes})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@projet12_bp.route('/projet12/api/stats/comparaison', methods=['GET'])
def api_stats_comparaison():
    """
    API pour comparer deux périodes
    """
    try:
        date_debut_1 = request.args.get('date_debut_1')
        date_fin_1 = request.args.get('date_fin_1')
        date_debut_2 = request.args.get('date_debut_2')
        date_fin_2 = request.args.get('date_fin_2')
        
        if not all([date_debut_1, date_fin_1, date_debut_2, date_fin_2]):
            return jsonify({'success': False, 'error': 'Toutes les dates sont requises'}), 400
        
        comparaison = get_comparaison_periodes(date_debut_1, date_fin_1, date_debut_2, date_fin_2)
        
        if comparaison:
            return jsonify({'success': True, 'data': comparaison})
        else:
            return jsonify({'success': False, 'error': 'Erreur lors de la comparaison'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

