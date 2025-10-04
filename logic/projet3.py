from flask import Blueprint, render_template, jsonify, request
from db import (
    get_commandes_bat,
    update_date_bat,
    update_reception_elem,
    envoyer_bat
)

bp = Blueprint("projet3", __name__, url_prefix="/projet3")

# Page HTML principale
@bp.route("/")
def page_projet3():
    return render_template("projet3.html")

# API pour retourner les données du suivi BAT
@bp.route("/api/commandes")
def api_commandes_bat():
    rows = get_commandes_bat()
    data = [
        {
            "ID": row["ID"],
            "Numero": row["Numero"],
            "RaisonSociale": row["RaisonSociale"],
            "DteBat": row["DteBat"].strftime('%Y-%m-%d') if row["DteBat"] else "",
            "DteReceptElem": row["DteReceptElem"].strftime('%Y-%m-%d') if row["DteReceptElem"] else "",
            "EtatPrepress": row["EtatPrepress"],
            "PourcentageReceptElem": row["PourcentageReceptElem"],
            "EtatLiv": row["EtatLiv"]
        } for row in rows
    ]
    return jsonify({"data": data})

# API pour mettre à jour la date BAT
@bp.route("/api/commandes/<int:id_commande>", methods=["PUT"])
def maj_bat(id_commande):
    data = request.get_json()
    success = update_date_bat(id_commande, data.get("DteBat"))
    return jsonify({"success": success})

# API pour confirmer réception des éléments
@bp.route("/api/commandes/<int:id_commande>/reception", methods=["PUT"])
def maj_reception(id_commande):
    return jsonify({"success": update_reception_elem(id_commande)})

# API pour valider envoi BAT
@bp.route("/api/commandes/<int:id_commande>/envoi", methods=["PUT"])
def maj_envoi_bat(id_commande):
    return jsonify({"success": envoyer_bat(id_commande)})
