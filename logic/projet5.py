from flask import Blueprint, render_template, request, jsonify
from db import get_db_cursor  # On garde uniquement get_db_cursor car query n'existe pas
from datetime import datetime

bp = Blueprint("projet5", __name__, url_prefix="/projet5")

@bp.route("/")
def index():
    return render_template("projet5.html")

@bp.route("/api/fiche_travail")
def fiche_travail():
    sql = """
        SELECT FT.ID AS id_fiche, FT.RefFiche AS ref_fiche,
               C.Numero AS commande, S.RaiSocTri AS client,
               P.ID AS id_poste, P.Nom AS poste, SR.Nom AS service,
               T.DteDeb AS dte_deb, T.HeurDeb AS heur_deb,
               T.DteFin AS dte_fin, T.HeurFin AS heur_fin,
               T.ID_PERSONNE AS id_personne,
               T.Remarques AS remarques
        FROM GP_FICHES_TRAVAIL FT
        JOIN COMMANDES C ON C.ID = FT.ID_COMMANDE
        JOIN SOCIETES S ON S.ID = C.ID_SOCIETE
        JOIN GP_POSTES P ON P.ID = FT.ID_POSTE
        JOIN GP_SERVICES SR ON SR.ID = P.ID_SERVICE
        LEFT JOIN GP_TRAITEMENTS T ON T.ID_FICHE_TRAVAIL = FT.ID
        WHERE C.Termine = 0
    """
    with get_db_cursor() as cursor:
        cursor.execute(sql)
        rows = cursor.fetchall()

    fiches = {}
    for row in rows:
        service = row.service or "Inconnu"

        # Récupérer les opérations disponibles pour ce poste
        with get_db_cursor() as c2:
            c2.execute("SELECT ID, Nom FROM GP_POSTES_OP WHERE ID_POSTE = ?", (row.id_poste,))
            operations = c2.fetchall()

        fiches.setdefault(service, []).append({
            "id_fiche": row.id_fiche,
            "ref_fiche": row.ref_fiche,
            "commande": row.commande,
            "client": row.client,
            "poste": row.poste,
            "id_poste": row.id_poste,
            "service": row.service,
            "dte_deb": row.dte_deb.isoformat() if row.dte_deb else None,
            "heur_deb": row.heur_deb,
            "dte_fin": row.dte_fin.isoformat() if row.dte_fin else None,
            "heur_fin": row.heur_fin,
            "id_personne": row.id_personne,
            "remarques": row.remarques,
            "operations": [{"id": op.ID, "nom": op.Nom} for op in operations]
        })
    return jsonify(fiches)

@bp.route("/api/personnes")
def personnes():
    sql = """
        SELECT P.ID, P.Nom, E.Code
        FROM PERSONNES P
        JOIN EMPLOYES E ON P.ID = E.ID_PERSONNE
        WHERE E.Atelier = 1
    """
    with get_db_cursor() as cursor:
        cursor.execute(sql)
        rows = cursor.fetchall()
    return jsonify([{"id": r.ID, "nom": r.Nom, "code": r.Code} for r in rows])

@bp.route("/api/operations/<int:id_poste>")
def operations_par_poste(id_poste):
    sql = """
        SELECT ID, Nom FROM GP_POSTES_OP WHERE ID_POSTE = ?
    """
    with get_db_cursor() as cursor:
        cursor.execute(sql, (id_poste,))
        rows = cursor.fetchall()
    return jsonify([{"id": r.ID, "nom": r.Nom} for r in rows])

@bp.route("/api/save_traitement", methods=["POST"])
def save_traitement():
    data = request.json

    try:
        print("📥 Données reçues :", data)

        id_fiche = int(data["id_fiche_travail"])
        id_personne = int(data["id_personne"])
        id_operation = int(data["id_operation"])
        dte_deb = data.get("dte_deb")
        dte_fin = data.get("dte_fin")
        heur_deb_str = data.get("heur_deb", "")
        heur_fin_str = data.get("heur_fin", "")
        nb_op = float(data.get("nb_op", 0))

        def parse_heure(h):
            h, m = map(int, h.split(":"))
            return h + m / 60

        heur_deb = parse_heure(heur_deb_str)
        heur_fin = parse_heure(heur_fin_str)
        tps_reel = round(heur_fin - heur_deb, 2) if heur_fin > heur_deb else 0

        with get_db_cursor() as cursor:
            # Insère traitement
            cursor.execute("""
                INSERT INTO GP_TRAITEMENTS
                (ID_FICHE_TRAVAIL, ID_PERSONNE, DteDeb, HeurDeb, DteFin, HeurFin, NbOp, NbPers, Origine, Remarques)
                VALUES (?, ?, ?, ?, ?, ?, ?, 1, 1, '')
            """, (id_fiche, id_personne, dte_deb, heur_deb, dte_fin, heur_fin, nb_op))

            # Vérifie existence dans GP_FICHES_OPERATIONS
            cursor.execute("""
                SELECT COUNT(*) FROM GP_FICHES_OPERATIONS
                WHERE ID_FICHE_TRAVAIL = ? AND ID_OPERATION = ?
            """, (id_fiche, id_operation))
            exists = cursor.fetchone()[0]

            if exists:
                cursor.execute("""
                    UPDATE GP_FICHES_OPERATIONS
                    SET OpReel = ?, TpsRelPass = ?
                    WHERE ID_FICHE_TRAVAIL = ? AND ID_OPERATION = ?
                """, (nb_op, tps_reel, id_fiche, id_operation))
            else:
                cursor.execute("""
                    INSERT INTO GP_FICHES_OPERATIONS (ID_FICHE_TRAVAIL, ID_OPERATION, OpReel, TpsRelPass)
                    VALUES (?, ?, ?, ?)
                """, (id_fiche, id_operation, nb_op, tps_reel))

            cursor.connection.commit()

        return jsonify({"success": True, "message": "✅ Traitement et opération enregistrés."})

    except Exception as e:
        print("❌ Erreur :", e)
        return jsonify({"success": False, "message": str(e)})

@bp.route("/api/change_poste", methods=["POST"])
def change_poste():
    data = request.json
    id_fiche = data.get("id_fiche_travail")
    nouveau_poste = data.get("nouveau_poste")

    try:
        with get_db_cursor() as cursor:
            cursor.execute("""
                UPDATE GP_FICHES_TRAVAIL
                SET ID_POSTE = (
                    SELECT ID FROM GP_POSTES WHERE Nom = ?
                )
                WHERE ID = ?
            """, (nouveau_poste, id_fiche))
        return jsonify({"success": True, "message": "Poste mis à jour"})
    except Exception as e:
        print(f"Erreur changement poste: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

