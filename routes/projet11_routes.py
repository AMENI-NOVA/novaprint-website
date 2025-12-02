#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Routes Flask pour le Projet 11 - Gestion des traitements (WEB_TRAITEMENTS)
"""

from flask import Blueprint, render_template, request, jsonify
from logic import projet11
from datetime import datetime

# Créer le blueprint
projet11_bp = Blueprint('projet11', __name__)


@projet11_bp.route('/projet11')
def index():
    """Page principale du projet 11"""
    return render_template('projet11.html')


@projet11_bp.route('/projet11/traitements')
def liste_traitements():
    """Page de liste des traitements"""
    traitements = projet11.get_all_traitements()
    return render_template('projet11_liste.html', traitements=traitements)


@projet11_bp.route('/projet11/nouveau')
def nouveau_traitement():
    """Page de création d'un nouveau traitement"""
    commandes = projet11.get_numeros_commandes_disponibles()
    operateurs = projet11.get_operateurs_disponibles()
    postes = projet11.get_postes_disponibles()
    return render_template('projet11_nouveau.html', commandes=commandes, operateurs=operateurs, postes=postes)


@projet11_bp.route('/projet11/fiche/<int:id_fiche>')
def details_fiche():
    """Récupère les détails d'une fiche de travail (AJAX)"""
    id_fiche = request.args.get('id_fiche', type=int)
    
    if not id_fiche:
        return jsonify({"error": "ID de fiche requis"}), 400
    
    operations = projet11.get_operations_by_fiche(id_fiche)
    traitement = projet11.get_traitement_by_fiche(id_fiche)
    
    return jsonify({
        "operations": operations,
        "traitement": traitement
    })


@projet11_bp.route('/projet11/api/traitements', methods=['GET'])
def api_get_traitements():
    """API pour récupérer tous les traitements"""
    traitements = projet11.get_all_traitements()
    return jsonify(traitements)


@projet11_bp.route('/projet11/api/traitements/<int:traitement_id>', methods=['GET'])
def api_get_traitement(traitement_id):
    """API pour récupérer un traitement spécifique"""
    traitement = projet11.get_traitement_by_id(traitement_id)
    
    if not traitement:
        return jsonify({"error": "Traitement non trouvé"}), 404
    
    return jsonify(traitement)


@projet11_bp.route('/projet11/api/traitements', methods=['POST'])
def api_create_traitement():
    """API pour créer un nouveau traitement"""
    try:
        data = request.get_json()
        print(f"[DEBUG API] Données reçues: {data}")

        def _safe_int(value):
            try:
                return int(value)
            except (TypeError, ValueError):
                return 0

        data['pdt_c'] = _safe_int(data.get('pdt_c'))
        data['pdt_nnc'] = _safe_int(data.get('pdt_nnc'))
        data['pdt_anc'] = _safe_int(data.get('pdt_anc'))
        data['nb_op'] = data['pdt_c'] + data['pdt_nnc'] + data['pdt_anc']

        if data['nb_op'] <= 0:
            return jsonify({"error": "Veuillez saisir au moins une quantité produite"}), 400
        data['nb_op'] = data['pdt_c'] + data['pdt_nnc'] + data['pdt_anc']
        
        # Valider les données requises
        # CORRECTION: Accepter id_fiche_travail = 0 pour les services non prévus
        if data.get('id_fiche_travail') is None:
            print("[ERREUR API] ID de fiche de travail manquant")
            return jsonify({"error": "ID de fiche de travail requis"}), 400
        
        # Pour les services non prévus (id_fiche_travail = 0), vérifier les données supplémentaires
        if data.get('id_fiche_travail') == 0:
            print("[INFO API] Service non prévu détecté")
            if not data.get('numero_commande') or not data.get('nom_service'):
                print(f"[ERREUR API] Données manquantes - numero_commande: {data.get('numero_commande')}, nom_service: {data.get('nom_service')}")
                return jsonify({"error": "Pour un service non prévu, le numéro de commande et le nom du service sont requis"}), 400
        
        if data['nb_op'] <= 0:
            print("[ERREUR API] Aucune quantité produite fournie")
            return jsonify({"error": "Veuillez saisir au moins une quantité produite"}), 400

        # Convertir les dates si nécessaire
        # CORRECTION: Gérer l'heure locale du navigateur (sans conversion UTC)
        if data.get('dte_deb'):
            try:
                # Format local: 2025-10-20T14:30:00 (sans Z, donc heure locale)
                if 'T' in data['dte_deb']:
                    # Enlever le Z s'il existe (ancien format)
                    date_str = data['dte_deb'].replace('Z', '')
                    # Parser le format ISO local
                    if '.' in date_str:
                        # Avec millisecondes: 2025-10-20T14:30:00.123
                        data['dte_deb'] = datetime.strptime(date_str.split('.')[0], '%Y-%m-%dT%H:%M:%S')
                    else:
                        # Sans millisecondes: 2025-10-20T14:30:00
                        data['dte_deb'] = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S')
                else:
                    data['dte_deb'] = datetime.strptime(data['dte_deb'], '%Y-%m-%d %H:%M:%S')
            except (ValueError, AttributeError) as e:
                print(f"Erreur parsing dte_deb: {e}")
        
        if data.get('dte_fin'):
            try:
                # Format local: 2025-10-20T14:30:00 (sans Z, donc heure locale)
                if 'T' in data['dte_fin']:
                    # Enlever le Z s'il existe (ancien format)
                    date_str = data['dte_fin'].replace('Z', '')
                    # Parser le format ISO local
                    if '.' in date_str:
                        # Avec millisecondes: 2025-10-20T14:30:00.123
                        data['dte_fin'] = datetime.strptime(date_str.split('.')[0], '%Y-%m-%dT%H:%M:%S')
                    else:
                        # Sans millisecondes: 2025-10-20T14:30:00
                        data['dte_fin'] = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S')
                else:
                    data['dte_fin'] = datetime.strptime(data['dte_fin'], '%Y-%m-%d %H:%M:%S')
            except (ValueError, AttributeError) as e:
                print(f"Erreur parsing dte_fin: {e}")
        
        # Créer le traitement
        print("[INFO API] Appel à create_traitement()")
        traitement_id = projet11.create_traitement(data)
        
        if traitement_id:
            print(f"[SUCCESS API] Traitement créé avec ID: {traitement_id}")
            return jsonify({
                "success": True,
                "id": traitement_id,
                "message": "Traitement créé avec succès"
            }), 201
        else:
            print("[ERREUR API] create_traitement() a retourné None")
            return jsonify({"error": "Erreur lors de la création du traitement - Vérifiez les logs serveur"}), 500
            
    except Exception as e:
        print(f"[EXCEPTION API] {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Erreur serveur: {str(e)}"}), 500


@projet11_bp.route('/projet11/api/traitements/start', methods=['POST'])
def api_start_traitement():
    """API pour démarrer un traitement (chronomètre)"""
    try:
        data = request.get_json() or {}

        def _safe_int(value, default=0):
            try:
                return int(value)
            except (TypeError, ValueError):
                return default

        # Normaliser les champs numériques
        data['pdt_c'] = _safe_int(data.get('pdt_c'))
        data['pdt_nnc'] = _safe_int(data.get('pdt_nnc'))
        data['pdt_anc'] = _safe_int(data.get('pdt_anc'))
        data['nb_pers'] = max(1, _safe_int(data.get('nb_pers'), 1))

        # Matricule opérateur (peut être None si non fourni)
        matricule = data.get('matricule_personel')
        try:
            data['matricule_personel'] = int(matricule) if matricule is not None else None
        except (TypeError, ValueError):
            data['matricule_personel'] = None

        # ID fiche travail (0 pour service non prévu)
        id_fiche_raw = data.get('id_fiche_travail')
        try:
            data['id_fiche_travail'] = int(id_fiche_raw) if id_fiche_raw is not None else None
        except (TypeError, ValueError):
            data['id_fiche_travail'] = None

        if data.get('id_fiche_travail') is None:
            return jsonify({"error": "ID de fiche de travail requis"}), 400

        # Services non prévus : s'assurer d'avoir les informations minimales
        if data['id_fiche_travail'] == 0:
            if not data.get('numero_commande') or not data.get('nom_service'):
                return jsonify({"error": "Pour un service non prévu, le numéro de commande et le nom du service sont requis"}), 400

        # Conversion de la date de début (locale)
        if data.get('dte_deb'):
            try:
                date_str = data['dte_deb'].replace('Z', '')
                if 'T' in date_str:
                    if '.' in date_str:
                        data['dte_deb'] = datetime.strptime(date_str.split('.')[0], '%Y-%m-%dT%H:%M:%S')
                    else:
                        data['dte_deb'] = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S')
                else:
                    data['dte_deb'] = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
            except (ValueError, AttributeError) as e:
                print(f"[ERREUR API START] Parse dte_deb: {e}")
                data['dte_deb'] = datetime.now()
        else:
            data['dte_deb'] = datetime.now()

        data['dte_fin'] = None  # Chronomètre en cours

        traitement_id = projet11.create_traitement(data)
        if traitement_id:
            return jsonify({
                "success": True,
                "id": traitement_id,
                "message": "Traitement démarré"
            }), 201

        return jsonify({"error": "Impossible de démarrer le traitement"}), 500

    except Exception as e:
        print(f"[EXCEPTION API START] {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Erreur serveur: {str(e)}"}), 500


@projet11_bp.route('/projet11/api/traitements/<int:traitement_id>', methods=['PUT'])
def api_update_traitement(traitement_id):
    """API pour mettre à jour un traitement"""
    try:
        data = request.get_json()

        def _safe_int(value):
            try:
                return int(value)
            except (TypeError, ValueError):
                return 0

        data['pdt_c'] = _safe_int(data.get('pdt_c'))
        data['pdt_nnc'] = _safe_int(data.get('pdt_nnc'))
        data['pdt_anc'] = _safe_int(data.get('pdt_anc'))
        
        # Convertir les dates si nécessaire
        # CORRECTION: Gérer l'heure locale du navigateur (sans conversion UTC)
        if data.get('dte_deb'):
            try:
                if 'T' in data['dte_deb']:
                    date_str = data['dte_deb'].replace('Z', '')
                    if '.' in date_str:
                        data['dte_deb'] = datetime.strptime(date_str.split('.')[0], '%Y-%m-%dT%H:%M:%S')
                    else:
                        data['dte_deb'] = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S')
                else:
                    data['dte_deb'] = datetime.strptime(data['dte_deb'], '%Y-%m-%d %H:%M:%S')
            except (ValueError, AttributeError) as e:
                print(f"Erreur parsing dte_deb: {e}")
        
        if data.get('dte_fin'):
            try:
                if 'T' in data['dte_fin']:
                    date_str = data['dte_fin'].replace('Z', '')
                    if '.' in date_str:
                        data['dte_fin'] = datetime.strptime(date_str.split('.')[0], '%Y-%m-%dT%H:%M:%S')
                    else:
                        data['dte_fin'] = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S')
                else:
                    data['dte_fin'] = datetime.strptime(data['dte_fin'], '%Y-%m-%d %H:%M:%S')
            except (ValueError, AttributeError) as e:
                print(f"Erreur parsing dte_fin: {e}")
        
        # Mettre à jour le traitement
        success = projet11.update_traitement(traitement_id, data)
        
        if success:
            return jsonify({
                "success": True,
                "message": "Traitement mis à jour avec succès"
            })
        else:
            return jsonify({"error": "Erreur lors de la mise à jour"}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@projet11_bp.route('/projet11/api/traitements/<int:traitement_id>', methods=['DELETE'])
def api_delete_traitement(traitement_id):
    """API pour supprimer un traitement"""
    try:
        success = projet11.delete_traitement(traitement_id)
        
        if success:
            return jsonify({
                "success": True,
                "message": "Traitement supprimé avec succès"
            })
        else:
            return jsonify({"error": "Erreur lors de la suppression"}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@projet11_bp.route('/projet11/statistiques')
def statistiques():
    """Page de statistiques des traitements"""
    stats = projet11.get_statistiques_traitements()
    stats_services = projet11.get_traitements_par_service()
    stats_operateurs = projet11.get_traitements_par_operateur()
    
    return render_template(
        'projet11_stats.html',
        stats=stats,
        stats_services=stats_services,
        stats_operateurs=stats_operateurs
    )


@projet11_bp.route('/projet11/api/statistiques', methods=['GET'])
def api_statistiques():
    """API pour récupérer les statistiques"""
    stats = projet11.get_statistiques_traitements()
    stats_services = projet11.get_traitements_par_service()
    stats_operateurs = projet11.get_traitements_par_operateur()
    
    return jsonify({
        "global": stats,
        "par_service": stats_services,
        "par_operateur": stats_operateurs
    })


@projet11_bp.route('/projet11/api/fiches-disponibles', methods=['GET'])
def api_fiches_disponibles():
    """API pour récupérer les fiches de travail disponibles"""
    fiches = projet11.get_fiches_travail_disponibles()
    return jsonify(fiches)


@projet11_bp.route('/projet11/api/operateurs', methods=['GET'])
def api_operateurs():
    """API pour récupérer la liste des opérateurs"""
    operateurs = projet11.get_operateurs_disponibles()
    return jsonify(operateurs)


@projet11_bp.route('/projet11/api/numeros-commandes', methods=['GET'])
def api_numeros_commandes():
    """API pour récupérer les numéros de commandes disponibles"""
    commandes = projet11.get_numeros_commandes_disponibles()
    return jsonify(commandes)


@projet11_bp.route('/projet11/api/fiches-by-commande/<numero_commande>', methods=['GET'])
def api_fiches_by_commande(numero_commande):
    """API pour récupérer les fiches de travail d'une commande spécifique"""
    fiches = projet11.get_fiches_by_numero_commande(numero_commande)
    return jsonify(fiches)


@projet11_bp.route('/projet11/api/postes', methods=['GET'])
def api_postes():
    """API pour récupérer la liste des postes/machines disponibles"""
    postes = projet11.get_postes_disponibles()
    return jsonify(postes)


@projet11_bp.route('/projet11/api/traitements-fiche/<int:id_fiche_travail>', methods=['GET'])
def api_traitements_fiche(id_fiche_travail):
    """API pour récupérer les traitements existants d'une fiche de travail"""
    traitements = projet11.get_traitements_existants_fiche(id_fiche_travail)
    return jsonify(traitements)


@projet11_bp.route('/projet11/api/services-prevus/<numero_commande>', methods=['GET'])
def api_services_prevus(numero_commande):
    """API pour récupérer les services prévus pour une commande"""
    services = projet11.get_services_prevus_by_commande(numero_commande)
    return jsonify(services)


@projet11_bp.route('/projet11/api/postes-prevus/<numero_commande>/<nom_service>', methods=['GET'])
def api_postes_prevus(numero_commande, nom_service):
    """API pour récupérer les postes prévus pour une commande et un service"""
    postes = projet11.get_postes_prevus_by_commande_service(numero_commande, nom_service)
    return jsonify(postes)


@projet11_bp.route('/projet11/api/traitements-service/<numero_commande>/<nom_service>', methods=['GET'])
def api_traitements_service(numero_commande, nom_service):
    """API pour récupérer les traitements existants pour une commande et un service"""
    traitements = projet11.get_traitements_existants_service(numero_commande, nom_service)
    return jsonify(traitements)


@projet11_bp.route('/projet11/api/services-tous', methods=['GET'])
def api_services_tous():
    """API pour récupérer TOUS les services disponibles depuis GP_SERVICES"""
    services = projet11.get_tous_services()
    return jsonify(services)


@projet11_bp.route('/projet11/api/postes-tous-service/<nom_service>', methods=['GET'])
def api_postes_tous_service(nom_service):
    """API pour récupérer TOUS les postes d'un service spécifique"""
    postes = projet11.get_postes_by_service(nom_service)
    return jsonify(postes)

