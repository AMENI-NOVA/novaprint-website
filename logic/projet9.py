from flask import Blueprint, jsonify, render_template, request
from db import (
    get_commandes_avec_suivi, get_statistiques_performance, 
    get_performance_par_client, get_alertes_retard, marquer_livraison_reelle
)

# ✅ Déclaration du blueprint pour le suivi de performance
bp = Blueprint("projet9", __name__, url_prefix="/projet9")

@bp.route("/")
def index():
    """Page principale du suivi de performance de livraison"""
    return render_template("projet9.html")

@bp.route("/vue-ensemble")
def vue_ensemble():
    """Page Vue d'ensemble du projet 9"""
    return render_template("projet9_vue_ensemble.html")

@bp.route("/commandes-detaillees")
def commandes_detaillees():
    """Page Commandes détaillées du projet 9"""
    return render_template("projet9_commandes_detaillees.html")

@bp.route("/performance-clients")
def performance_clients():
    """Page Performance clients du projet 9"""
    return render_template("projet9_performance_clients.html")

@bp.route("/analyses-avancees")
def analyses_avancees():
    """Page Analyses avancées du projet 9"""
    return render_template("projet9_analyses_avancees.html")

# ---------------------------
# ROUTES SUIVI DES DÉLAIS
# ---------------------------
@bp.route("/api/commandes-avec-suivi")
def api_commandes_avec_suivi():
    """API pour récupérer les commandes avec informations de suivi"""
    return jsonify(get_commandes_avec_suivi())

@bp.route("/api/statistiques-performance")
def api_statistiques_performance():
    """API pour récupérer les statistiques de performance"""
    return jsonify(get_statistiques_performance())

@bp.route("/api/performance-par-client")
def api_performance_par_client():
    """API pour récupérer la performance par client"""
    return jsonify(get_performance_par_client())

@bp.route("/api/alertes-retard")
def api_alertes_retard():
    """API pour récupérer les alertes de retard"""
    return jsonify(get_alertes_retard())

@bp.route("/api/marquer-livraison", methods=["POST"])
def api_marquer_livraison():
    """API pour marquer une commande comme livrée"""
    data = request.get_json()
    numero = data.get("numero")
    date_livraison = data.get("date_livraison")
    user = data.get("user", "Système")

    if numero and date_livraison:
        success = marquer_livraison_reelle(numero, date_livraison, user)
        if success:
            return jsonify({"status": "success", "message": "Livraison marquée avec succès"}), 200
        else:
            return jsonify({"status": "error", "message": "Échec du marquage de livraison"}), 500
    return jsonify({"status": "error", "message": "Données invalides"}), 400

