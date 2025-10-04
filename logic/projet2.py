from flask import Blueprint, render_template
from db import get_commandes_en_cours

# ✅ Déclaration du blueprint
bp = Blueprint("projet2", __name__, url_prefix="/projet2")

@bp.route("/")
def commandes():
    rows = get_commandes_en_cours()
    return render_template("projet2.html", rows=rows)
