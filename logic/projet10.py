from flask import Blueprint, jsonify, render_template, request
from db import (
    get_controles_qualite, 
    get_controle_qualite_by_id,
    create_controle_qualite,
    update_controle_qualite,
    get_statistiques_controle_qualite,
    get_numeros_commandes_disponibles
)

# Déclaration du blueprint
bp = Blueprint("projet10", __name__, url_prefix="/projet10")

@bp.route("/")
def index():
    """Page principale du contrôle qualité"""
    return render_template("projet10.html")

# ---------------------------
# API CONTRÔLE QUALITÉ
# ---------------------------
@bp.route("/api/controles")
def api_controles():
    """API pour récupérer tous les contrôles qualité"""
    return jsonify(get_controles_qualite())

@bp.route("/api/controle/<int:controle_id>")
def api_controle(controle_id):
    """API pour récupérer un contrôle qualité par ID"""
    controle = get_controle_qualite_by_id(controle_id)
    if controle:
        return jsonify(controle)
    return jsonify({"error": "Contrôle non trouvé"}), 404

@bp.route("/api/numeros-commandes")
def api_numeros_commandes():
    """API pour récupérer les numéros de commandes disponibles"""
    return jsonify(get_numeros_commandes_disponibles())

@bp.route("/api/statistiques")
def api_statistiques():
    """API pour récupérer les statistiques de contrôle qualité"""
    return jsonify(get_statistiques_controle_qualite())

@bp.route("/api/controle", methods=["POST"])
def api_create_controle():
    """API pour créer un nouveau contrôle qualité"""
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "Données manquantes"}), 400
    
    # Validation des champs obligatoires
    required_fields = ['date_controle', 'numero_dossier', 'operateur']
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({"error": f"Champ obligatoire manquant: {field}"}), 400
    
    controle_id = create_controle_qualite(data)
    
    if controle_id:
        return jsonify({"status": "success", "id": controle_id}), 201
    else:
        return jsonify({"error": "Erreur lors de la création"}), 500

@bp.route("/api/controle/<int:controle_id>", methods=["PUT"])
def api_update_controle(controle_id):
    """API pour mettre à jour un contrôle qualité"""
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "Données manquantes"}), 400
    
    success = update_controle_qualite(controle_id, data)
    
    if success:
        return jsonify({"status": "success"}), 200
    else:
        return jsonify({"error": "Erreur lors de la mise à jour"}), 500

@bp.route("/api/controle/<int:controle_id>", methods=["DELETE"])
def api_delete_controle(controle_id):
    """API pour supprimer un contrôle qualité"""
    # Note: Vous pouvez ajouter une fonction de suppression dans db.py si nécessaire
    return jsonify({"error": "Suppression non implémentée"}), 501