"""
Script pour intégrer les données NC de la pièce jointe
1. Supprime tous les enregistrements NC existants
2. Intègre les nouvelles données
"""
from db import get_db_connection
from datetime import datetime

# Données de la pièce jointe
donnees_nc = [
    {
        'date': '13/02/2025',
        'numero_dossier': '2025010094',
        'nc': 'COLLAGE',
        'description': 'presence de point de colle',
        'cause': 'réglage au niveau de la machine de pliage collage'
    },
    {
        'date': '13/02/2025',
        'numero_dossier': '2025010093',
        'nc': 'COLLAGE',
        'description': 'presence de point de colle',
        'cause': 'réglage au niveau de la machine de pliage collage'
    },
    {
        'date': '20/02/2025',
        'numero_dossier': '2025010151',
        'nc': 'IMPRESSION',
        'description': 'nuance couleur et tache',
        'cause': 'feuille de démarrage et tache blanchet'
    },
    {
        'date': '11/03/2025',
        'numero_dossier': '2025010064',
        'nc': 'IMPRESSION',
        'description': 'nuance couleur',
        'cause': 'feuille de démarrage'
    },
    {
        'date': '07/04/2025',
        'numero_dossier': '202503080',
        'nc': 'IMPRESSION',
        'description': 'nuance couleur',
        'cause': 'feuille de démarrage'
    },
    {
        'date': '23/04/2025',
        'numero_dossier': '2025040014',
        'nc': 'impression',
        'description': 'tache rouge au niveau de la pose n°4',
        'cause': 'feuille de démarrage'
    },
    {
        'date': '05/05/2025',
        'numero_dossier': '2025020142',
        'nc': 'découpe',
        'description': 'déchirure au niveau de la découpe( estampage sur la frappe)',
        'cause': 'surpression de l\'etape estampage'
    },
    {
        'date': '04/06/2025',
        'numero_dossier': '2025050035',
        'nc': 'IMPRESSION',
        'description': 'nuance couleur',
        'cause': 'panne machine KBA groupe bleu'
    },
    {
        'date': '11/08/2025',
        'numero_dossier': '2025070158',
        'nc': 'IMPRESSION',
        'description': 'tache blanche au niveau du fond noir',
        'cause': ''
    },
    {
        'date': '19/09/2025',
        'numero_dossier': '2025090045',
        'nc': 'pliage/collage',
        'description': 'point de colle',
        'cause': 'bavure de colle au niveau de la pate de collage due a un probleme de réglage en fin de tirage avec non respect de la frequence de controle predefinis'
    }
]

def get_info_commande(numero_dossier, cursor):
    """Récupère les informations de la commande"""
    try:
        numero_clean = numero_dossier.strip() if numero_dossier else ''
        
        query = """
        SELECT C.Reference, S.RaiSocTri, C.QteComm
        FROM COMMANDES C
        LEFT JOIN SOCIETES S ON C.ID_SOCIETE = S.ID
        WHERE LTRIM(RTRIM(C.Numero)) = ?
        """
        cursor.execute(query, (numero_clean,))
        row = cursor.fetchone()
        
        if row:
            return {
                'reference': row.Reference if row.Reference else '',
                'client': row.RaiSocTri if row.RaiSocTri else '',
                'qte_comm': row.QteComm if row.QteComm else 0
            }
        else:
            print(f"⚠️  Commande {numero_clean} non trouvée dans la base")
            return None
    except Exception as e:
        print(f"❌ Erreur lors de la récupération de la commande {numero_dossier}: {e}")
        return None

def supprimer_nc_existants():
    """Supprime tous les enregistrements NC existants"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Compter les enregistrements NC
        cursor.execute("SELECT COUNT(*) FROM WEB_PdtNC_RecClt WHERE TYPE = 'NC'")
        count = cursor.fetchone()[0]
        
        if count > 0:
            print(f"🗑️  Suppression de {count} enregistrements NC existants...")
            cursor.execute("DELETE FROM WEB_PdtNC_RecClt WHERE TYPE = 'NC'")
            conn.commit()
            print(f"✓ {count} enregistrements supprimés")
        else:
            print("ℹ  Aucun enregistrement NC à supprimer")
        
        return True
    except Exception as e:
        print(f"❌ Erreur lors de la suppression : {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

def integrer_donnees():
    """Intègre les données de la pièce jointe"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        print(f"\n📝 Intégration de {len(donnees_nc)} enregistrements NC...")
        
        compteur = 0
        for i, donnee in enumerate(donnees_nc, start=1):
            # Convertir la date
            date_obj = datetime.strptime(donnee['date'], '%d/%m/%Y')
            
            # Récupérer les infos de la commande
            info_commande = get_info_commande(donnee['numero_dossier'], cursor)
            
            if info_commande:
                client = info_commande['client']
                reference = info_commande['reference']
                qte_comm = info_commande['qte_comm']
            else:
                # Si la commande n'est pas trouvée, on laisse vide
                client = ''
                reference = ''
                qte_comm = None
            
            # Générer la référence fichier
            ref_fich = f"NCP {i:02d}"
            
            # Insérer l'enregistrement
            query = """
            INSERT INTO WEB_PdtNC_RecClt 
            (Date, TYPE, NC, DesNC, Cause, Numero_COMMANDES, Reference_COMMANDES, 
             RaiSocTri_SOCIETES, QteComm_COMMANDES, QteNC, CaracNC, RefFich)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            cursor.execute(query, (
                date_obj,
                'NC',
                donnee['nc'],
                donnee['description'],
                donnee['cause'] if donnee['cause'] else None,
                donnee['numero_dossier'],
                reference,
                client,
                qte_comm,
                None,  # QteNC vide
                None,  # CaracNC vide
                ref_fich
            ))
            
            compteur += 1
            print(f"  ✓ {ref_fich} - N° {donnee['numero_dossier']} - {donnee['nc']} - Client: {client or '(non trouvé)'}")
        
        conn.commit()
        print(f"\n✓ {compteur} enregistrements NC intégrés avec succès")
        
        return True
    except Exception as e:
        print(f"❌ Erreur lors de l'intégration : {e}")
        conn.rollback()
        import traceback
        traceback.print_exc()
        return False
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print("=" * 70)
    print("INTÉGRATION DES DONNÉES NC - PIÈCE JOINTE")
    print("=" * 70)
    
    # Étape 1: Supprimer les NC existants
    if supprimer_nc_existants():
        # Étape 2: Intégrer les nouvelles données
        if integrer_donnees():
            print("\n" + "=" * 70)
            print("✅ INTÉGRATION TERMINÉE AVEC SUCCÈS")
            print("=" * 70)
        else:
            print("\n❌ L'intégration a échoué")
    else:
        print("\n❌ La suppression a échoué, intégration annulée")


















