"""
Routes pour le Projet 14 - Registre de suivi des déchets
"""
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from logic.projet14 import (
    get_all_dechets,
    get_dechet_by_id,
    create_dechet,
    update_dechet,
    delete_dechet,
    get_types_predefined,
    get_statistiques_dechets,
    get_dechets_par_mois
)
from datetime import datetime

projet14_bp = Blueprint('projet14', __name__, url_prefix='/projet14')

@projet14_bp.route('/')
def index():
    """Page principale du registre de suivi des déchets"""
    types_predefined = get_types_predefined()
    return render_template('projet14.html', 
                         types_predefined=types_predefined,
                         date_du_jour=datetime.now().strftime('%Y-%m-%d'),
                         section=None)

@projet14_bp.route('/registre')
def registre():
    """Section Registre"""
    types_predefined = get_types_predefined()
    return render_template('projet14.html', 
                         types_predefined=types_predefined,
                         date_du_jour=datetime.now().strftime('%Y-%m-%d'),
                         section='registre')

@projet14_bp.route('/saisie')
def saisie():
    """Section Saisie d'un nouveau fichier (ouvre la popup)"""
    types_predefined = get_types_predefined()
    return render_template('projet14.html', 
                         types_predefined=types_predefined,
                         date_du_jour=datetime.now().strftime('%Y-%m-%d'),
                         section='saisie')

@projet14_bp.route('/statistiques')
def statistiques_view():
    """Section Statistiques"""
    types_predefined = get_types_predefined()
    return render_template('projet14.html', 
                         types_predefined=types_predefined,
                         date_du_jour=datetime.now().strftime('%Y-%m-%d'),
                         section='stats')

@projet14_bp.route('/liste')
def liste():
    """Retourne la liste des déchets en JSON"""
    dechets = get_all_dechets()
    return jsonify(dechets)

@projet14_bp.route('/get_types')
def get_types():
    """Retourne les types de déchets prédéfinis"""
    return jsonify(get_types_predefined())

@projet14_bp.route('/ajouter', methods=['POST'])
def ajouter():
    """Ajoute un nouvel enregistrement de déchet"""
    try:
        data = request.get_json() if request.is_json else request.form.to_dict()
        
        # Validation
        if not data.get('type'):
            return jsonify({"success": False, "message": "Le type de déchet est requis"}), 400
        
        if not data.get('quantite'):
            return jsonify({"success": False, "message": "La quantité est requise"}), 400
        
        # Valeurs par défaut
        if not data.get('date'):
            data['date'] = datetime.now().strftime('%Y-%m-%d')
        
        if not data.get('unite'):
            data['unite'] = 'kg'
        
        dechet_id = create_dechet(data)
        
        if dechet_id:
            return jsonify({
                "success": True, 
                "message": "Déchet enregistré avec succès",
                "id": dechet_id
            })
        else:
            return jsonify({"success": False, "message": "Erreur lors de l'enregistrement"}), 500
            
    except Exception as e:
        print(f"Erreur dans /ajouter: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "message": str(e)}), 500

@projet14_bp.route('/modifier/<int:dechet_id>', methods=['GET', 'POST'])
def modifier(dechet_id):
    """Modifie un enregistrement de déchet"""
    if request.method == 'GET':
        dechet = get_dechet_by_id(dechet_id)
        if dechet:
            return jsonify(dechet)
        else:
            return jsonify({"success": False, "message": "Déchet introuvable"}), 404
    
    elif request.method == 'POST':
        try:
            data = request.get_json() if request.is_json else request.form.to_dict()
            
            # Validation
            if not data.get('type'):
                return jsonify({"success": False, "message": "Le type de déchet est requis"}), 400
            
            if not data.get('quantite'):
                return jsonify({"success": False, "message": "La quantité est requise"}), 400
            
            if update_dechet(dechet_id, data):
                return jsonify({"success": True, "message": "Déchet modifié avec succès"})
            else:
                return jsonify({"success": False, "message": "Erreur lors de la modification"}), 500
                
        except Exception as e:
            print(f"Erreur dans /modifier: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({"success": False, "message": str(e)}), 500

@projet14_bp.route('/supprimer/<int:dechet_id>', methods=['POST', 'DELETE'])
def supprimer(dechet_id):
    """Supprime un enregistrement de déchet"""
    try:
        if delete_dechet(dechet_id):
            return jsonify({"success": True, "message": "Déchet supprimé avec succès"})
        else:
            return jsonify({"success": False, "message": "Erreur lors de la suppression"}), 500
    except Exception as e:
        print(f"Erreur dans /supprimer: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


@projet14_bp.route('/api/statistiques')
def api_statistiques():
    """Retourne les statistiques en JSON"""
    annee = request.args.get('annee', None)
    stats = get_statistiques_dechets(annee)
    return jsonify(stats)

@projet14_bp.route('/mois/<int:annee>/<int:mois>')
def par_mois(annee, mois):
    """Retourne les déchets pour un mois donné"""
    dechets = get_dechets_par_mois(annee, mois)
    return jsonify(dechets)

