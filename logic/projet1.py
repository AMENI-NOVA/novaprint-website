from flask import Blueprint, jsonify, render_template, request
from db import (
    get_commandes, update_commande, get_historique_commande
)

# ✅ Déclaration du blueprint
bp = Blueprint("projet1", __name__, url_prefix="/projet1")

@bp.route("/")
def index():
    return render_template("projet1.html")

@bp.route("/api/commandes")
def api_commandes():
    return jsonify(get_commandes())

@bp.route("/update_commande", methods=["POST"])
def api_update_commande():
    data = request.get_json()
    numero = data.get("id")
    new_date = data.get("start")

    if numero and new_date:
        success = update_commande(numero, new_date)
        if success:
            return jsonify({"status": "success"}), 200
        else:
            return jsonify({"status": "error", "message": "Échec de la mise à jour"}), 500
    return jsonify({"status": "error", "message": "Données invalides"}), 400


@bp.route("/api/historique/<numero>")
def historique_commande(numero):
    data = get_historique_commande(numero)
    return jsonify(data)

