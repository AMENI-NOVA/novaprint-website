from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from db import get_db_cursor, get_contact_principal, creer_prospect, ajouter_contact

bp = Blueprint("projet4", __name__, url_prefix="/projet4")

@bp.route("/api/societes", methods=["GET"])
def get_societes():
    query = request.args.get("query", "").strip().lower()

    with get_db_cursor() as cursor:
        cursor.execute("""
            SELECT A.ID_SOCIETE AS ID,
                   A.Nom AS NomClient,
                   A.Ville,
                   P.Nom AS NomPays,
                   A.Telephone,
                   A.Fax,
                   A.Mail
            FROM [SOCIETES_ADRESSES] A
            LEFT JOIN PAYS P ON P.ID = A.ID_PAYS
        """)
        rows = cursor.fetchall()

    societes = []
    for row in rows:
        nom = row.NomClient or ""
        if not query or query in nom.lower():
            societes.append({
                "id": row.ID,
                "raison_sociale": row.NomClient,
                "ville": row.Ville,
                "pays": row.NomPays,
                "telephone": row.Telephone,
                "fax": row.Fax,
                "email": row.Mail
            })

    return jsonify(societes)

@bp.route("/api/contact", methods=["GET"])
def get_contact():
    id_societe = request.args.get("id_societe")
    if not id_societe:
        return jsonify({"error": "ID société manquant"}), 400

    contact = get_contact_principal(id_societe)
    if contact:
        return jsonify(contact)
    return jsonify({"error": "Aucun contact trouvé"}), 404

@bp.route("/api/contacts", methods=["GET"])
def get_contacts():
    id_societe = request.args.get("id_societe")
    if not id_societe:
        return jsonify({"error": "ID société manquant"}), 400

    with get_db_cursor() as cursor:
        cursor.execute("""
            SELECT 
                P.ID AS ID_PERSONNE,
                P.Nom,
                P.Prenom,
                P.Telephone,
                P.Mobile,
                M.Mail,
                FCT.Fonction
            FROM SOCIETES_PERSONNES SP
            INNER JOIN PERSONNES P ON P.ID = SP.ID_PERSONNE
            LEFT JOIN (
                SELECT ID_PERSONNE, Mail
                FROM PERSONNES_MAIL
                WHERE ParDefaut = 1
            ) M ON M.ID_PERSONNE = P.ID
            LEFT JOIN (
                SELECT PF.ID_PERSONNE, FO.Nom AS Fonction, 
                       ROW_NUMBER() OVER (PARTITION BY PF.ID_PERSONNE ORDER BY PF.Ordre ASC) AS rn
                FROM PERSONNES_FONCTIONS PF
                INNER JOIN FONCTIONS FO ON FO.ID = PF.ID_FONCTION
            ) FCT ON FCT.ID_PERSONNE = P.ID AND FCT.rn = 1
            WHERE SP.ID_SOCIETE = ?
        """, id_societe)

        rows = cursor.fetchall()
        contacts = []
        for row in rows:
            contacts.append({
                "id": row.ID_PERSONNE,
                "nom": row.Nom,
                "prenom": row.Prenom,
                "telephone": row.Telephone or row.Mobile,
                "email": row.Mail,
                "fonction": row.Fonction
            })

    return jsonify(contacts)

@bp.route("/api/fonctions", methods=["GET"])
def get_fonctions():
    with get_db_cursor() as cursor:
        cursor.execute("SELECT ID, Nom FROM FONCTIONS WHERE Archive = 0 ORDER BY Nom")
        rows = cursor.fetchall()
        fonctions = [{"id": row.ID, "nom": row.Nom} for row in rows]
    return jsonify(fonctions)

@bp.route("/", methods=["GET", "POST"])
def rapport_visite():
    if request.method == "POST":
        data = request.form

        objet_str = ""
        origine_str = ""
        is_new = data.get("is_new_prospect") == "true"

        if is_new:
            id_societe = creer_prospect(
                raison_sociale=data.get("raison_sociale"),
                ville=data.get("ville"),
                pays=data.get("pays"),
                telephone=data.get("telephone"),
                email=data.get("email")
            )

            id_personne = ajouter_contact(
                id_societe=id_societe,
                nom=data.get("contact_nom"),
                prenom="",
                telephone=data.get("contact_telephone"),
                email=data.get("contact_email"),
                id_fonction=data.get("id_fonction")
            )
        else:
            id_societe = data.get("id_societe")
            id_personne = data.get("id_personne")
            id_fonction = data.get("id_fonction")

            if id_fonction:
                with get_db_cursor() as cursor:
                    cursor.execute("""
                        DELETE FROM PERSONNES_FONCTIONS WHERE ID_PERSONNE = ?
                    """, id_personne)
                    cursor.execute("""
                        INSERT INTO PERSONNES_FONCTIONS (ID_PERSONNE, ID_FONCTION, Ordre)
                        VALUES (?, ?, 1)
                    """, id_personne, id_fonction)
                    cursor.connection.commit()

        with get_db_cursor() as cursor:
            cursor.execute("""
                INSERT INTO VISITES_CLIENTS
                (ID_SOCIETE, RaisonSociale, DateVisite, NatureVisite, Objet, Origine, Sujets, Bilan, Visiteur, CreePar, CreeLe)
                VALUES (?, ?, GETDATE(), ?, ?, ?, ?, ?, ?, ?, GETDATE())
            """, (
                id_societe,
                data.get("raison_sociale"),
                data.get("nature_visite"),
                objet_str,
                origine_str,
                data.get("resume_visite"),
                data.get("bilan"),
                data.get("nom_visiteur"),
                "user"  # À adapter si auth
            ))
            cursor.connection.commit()

        flash("Rapport enregistré avec succès.")
        return redirect(url_for("projet4.rapport_visite"))

    return render_template("projet4.html")
@bp.route("/api/update_societe", methods=["POST"])
def update_societe():
    data = request.get_json()
    with get_db_cursor() as cursor:
        cursor.execute("""
            UPDATE SOCIETES_ADRESSES
            SET Ville = ?, Telephone = ?, Fax = ?, Mail = ?
            WHERE ID_SOCIETE = ?
        """, (
            data.get("ville"),
            data.get("telephone"),
            data.get("fax"),
            data.get("email"),
            data.get("id_societe")
        ))
        cursor.connection.commit()
    return jsonify({"success": True})

@bp.route("/api/update_contact", methods=["POST"])
def update_contact():
    data = request.get_json()
    with get_db_cursor() as cursor:
        cursor.execute("""
            UPDATE PERSONNES
            SET Telephone = ?, Mobile = ?
            WHERE ID = ?
        """, (
            data.get("telephone"),
            data.get("mobile"),
            data.get("id_personne")
        ))

        if data.get("email"):
            cursor.execute("""
                UPDATE PERSONNES_MAIL
                SET Mail = ?
                WHERE ID_PERSONNE = ? AND ParDefaut = 1
            """, (
                data.get("email"),
                data.get("id_personne")
            ))

        if data.get("id_fonction"):
            cursor.execute("DELETE FROM PERSONNES_FONCTIONS WHERE ID_PERSONNE = ?", data.get("id_personne"))
            cursor.execute("""
                INSERT INTO PERSONNES_FONCTIONS (ID_PERSONNE, ID_FONCTION, Ordre)
                VALUES (?, ?, 1)
            """, data.get("id_personne"), data.get("id_fonction"))

        cursor.connection.commit()
    return jsonify({"success": True})
@bp.route("/api/add_contact", methods=["POST"])
def add_contact():
    data = request.get_json()
    id_societe = data.get("id_societe")
    nom = data.get("nom")
    email = data.get("email")
    telephone = data.get("telephone")
    id_fonction = data.get("id_fonction")

    with get_db_cursor() as cursor:
        cursor.execute("""
            INSERT INTO PERSONNES (Nom, Telephone)
            OUTPUT INSERTED.ID
            VALUES (?, ?)
        """, nom, telephone)
        id_personne = cursor.fetchone()[0]

        cursor.execute("""
            INSERT INTO SOCIETES_PERSONNES (ID_SOCIETE, ID_PERSONNE)
            VALUES (?, ?)
        """, id_societe, id_personne)

        if email:
            cursor.execute("""
                INSERT INTO PERSONNES_MAIL (ID_PERSONNE, Mail, ParDefaut)
                VALUES (?, ?, 1)
            """, id_personne, email)

        if id_fonction:
            cursor.execute("""
                INSERT INTO PERSONNES_FONCTIONS (ID_PERSONNE, ID_FONCTION, Ordre)
                VALUES (?, ?, 1)
            """, id_personne, id_fonction)

        cursor.connection.commit()

    return jsonify({"success": True, "id_personne": id_personne})
@bp.route("/api/add_prospect", methods=["POST"])
def add_prospect():
    data = request.get_json()
    
    if not data.get("raison_sociale") or not data.get("pays"):
        return jsonify({"success": False, "error": "Champs requis manquants"}), 400

    try:
        id_societe = creer_prospect(
            raison_sociale=data.get("raison_sociale"),
            ville=data.get("ville"),
            pays=data.get("pays"),
            telephone=data.get("telephone"),
            email=data.get("email")
        )
        return jsonify({"success": True, "id_societe": id_societe})
    except Exception as e:
        print("🚨 ERREUR lors de add_prospect:", e)  # <--- AJOUT ICI
        return jsonify({"success": False, "error": str(e)}), 500
@bp.route("/api/pays", methods=["GET"])
def get_pays():
    with get_db_cursor() as cursor:
        cursor.execute("SELECT ID, Nom FROM PAYS ORDER BY Nom")
        return jsonify([{"id": row.ID, "nom": row.Nom} for row in cursor.fetchall()])
@bp.route("/api/categories", methods=["GET"])
def get_categories():
    with get_db_cursor() as cursor:
        cursor.execute("""
            SELECT ID, Nom FROM CATEGORIES_SOCIETES
            WHERE Archive = 0
            ORDER BY Nom
        """)
        rows = cursor.fetchall()
        categories = [{"id": row.ID, "nom": row.Nom} for row in rows]
    return jsonify(categories)
