"""
Routes pour le Projet 15 - Analyse corrélation déchets/CA
"""
from flask import Blueprint, render_template, request, jsonify
from logic.projet15 import (
    get_all_correlations,
    get_correlation_by_id,
    update_correlation,
    get_statistiques_correlation,
    get_annees_disponibles,
    get_correlation_par_type,
    get_types_dechets_disponibles
)

projet15_bp = Blueprint('projet15', __name__, url_prefix='/projet15')

@projet15_bp.route('/')
def index():
    """Page principale du projet 15"""
    return render_template('projet15.html', section=None)

@projet15_bp.route('/tableau')
def tableau():
    """Section Tableau de données"""
    return render_template('projet15.html', section='tableau')

@projet15_bp.route('/graphique')
def graphique():
    """Section Graphique comparatif"""
    return render_template('projet15.html', section='graphique')

@projet15_bp.route('/api/correlations')
def api_correlations():
    """Retourne toutes les corrélations en JSON"""
    try:
        annee = request.args.get('annee', None)
        correlations = get_all_correlations(annee)
        return jsonify(correlations)
    except Exception as e:
        print(f"[ERREUR API] Erreur dans api_correlations: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@projet15_bp.route('/api/correlation/<int:corr_id>')
def api_correlation_detail(corr_id):
    """Retourne une corrélation par son ID"""
    correlation = get_correlation_by_id(corr_id)
    if correlation:
        return jsonify(correlation)
    else:
        return jsonify({"error": "Corrélation introuvable"}), 404

@projet15_bp.route('/api/correlation/<int:corr_id>/update', methods=['POST'])
def api_update_correlation(corr_id):
    """Met à jour une corrélation"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"success": False, "message": "Données manquantes"}), 400
        
        if update_correlation(corr_id, data):
            return jsonify({"success": True, "message": "Données mises à jour avec succès"})
        else:
            return jsonify({"success": False, "message": "Erreur lors de la mise à jour"}), 500
            
    except Exception as e:
        print(f"Erreur dans update_correlation: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

@projet15_bp.route('/api/statistiques')
def api_statistiques():
    """Retourne les statistiques de corrélation"""
    annee = request.args.get('annee', None)
    stats = get_statistiques_correlation(annee)
    return jsonify(stats)

@projet15_bp.route('/api/annees')
def api_annees():
    """Retourne la liste des années disponibles"""
    annees = get_annees_disponibles()
    return jsonify(annees)

@projet15_bp.route('/api/correlation_par_type')
def api_correlation_par_type():
    """Retourne les données de corrélation par type de déchet"""
    try:
        annee = request.args.get('annee', None)
        donnees = get_correlation_par_type(annee)
        return jsonify(donnees)
    except Exception as e:
        print(f"[ERREUR API] Erreur dans api_correlation_par_type: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@projet15_bp.route('/api/types_dechets')
def api_types_dechets():
    """Retourne la liste des types de déchets disponibles"""
    try:
        types = get_types_dechets_disponibles()
        return jsonify(types)
    except Exception as e:
        print(f"[ERREUR API] Erreur dans api_types_dechets: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

