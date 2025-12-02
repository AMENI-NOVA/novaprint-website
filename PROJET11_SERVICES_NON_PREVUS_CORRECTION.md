# Projet 11 - Correction : Enregistrement des Services Non Prévus

## 📅 Date de correction
20 octobre 2025

## 🔍 Problème Identifié

### Symptômes
Lorsqu'un utilisateur sélectionnait un **service non prévu** (via l'option "🔧 Autre service (non prévu)") :
1. ✅ La sélection du service fonctionnait
2. ✅ La sélection de la machine fonctionnait
3. ✅ Un message d'information s'affichait correctement
4. ❌ **MAIS** aucun champ de saisie n'apparaissait après le message
5. ❌ Impossible d'enregistrer les données du traitement

### Message affiché
```
⚠️ Service Non Prévu - Saisie Manuelle
Service : FACONNAGE
Machine : Déchiqutage
⚠️ Important : Comme ce service n'était pas prévu, veuillez saisir manuellement 
la quantité produite et les autres informations.
```

### Cause Racine
**Problème 1 : Champs opérateurs non générés**
- Les champs de saisie (opérateur, quantité, etc.) ne s'affichaient pas
- La fonction `genererChampsOperateurs()` n'était pas appelée pour les services non prévus

**Problème 2 : Backend ne gérait pas les services sans fiche**
- Le backend exigeait une `id_fiche_travail` valide
- Pour les services non prévus, il n'existe pas de fiche dans `GP_FICHES_TRAVAIL`
- Le système retournait une erreur car la fiche n'était pas trouvée

**Problème 3 : Données manquantes**
- Le formulaire JavaScript n'envoyait pas `numero_commande` et `nom_service`
- Ces informations sont nécessaires pour enregistrer un service non prévu

## ✅ Solution Implémentée

### Principe
Les **services non prévus** sont maintenant traités de la même manière que les services prévus :
- Même formulaire de saisie
- Même table de destination (`WEB_TRAITEMENTS`)
- Mêmes champs à renseigner (opérateur, quantité, machine, etc.)

**Différence** : Au lieu de récupérer les informations depuis `GP_FICHES_TRAVAIL`, le système récupère directement les informations de la commande et utilise les données saisies manuellement.

## 🔧 Modifications Apportées

### 1. Frontend (`templates/projet11_nouveau.html`)

#### ✅ Correction 1 : Génération des champs opérateurs
**Ligne 551-598** : Ajout de l'appel à `genererChampsOperateurs(1)`

```javascript
// Gérer la sélection du poste manuel
$(document).on('change', '#poste_manuel', function() {
    // ... code existant ...
    
    // CORRECTION: Générer les champs opérateurs pour les services non prévus
    genererChampsOperateurs(1);
    
    // Afficher la section de saisie
    $('#separator').show();
    $('#sectionSaisie').show();
    
    // Mettre le focus sur le premier champ de saisie
    setTimeout(function() {
        $('#nb_pers').focus().select();
    }, 300);
});
```

**Résultat** : Les champs de saisie (opérateur, quantité, etc.) s'affichent maintenant correctement.

#### ✅ Correction 2 : Envoi des données supplémentaires
**Ligne 962-973** : Ajout de `numero_commande` et `nom_service`

```javascript
const data = {
    id_fiche_travail: parseInt($('#id_fiche_travail').val()) || 0,
    dte_deb: $('#dte_deb').val(),
    dte_fin: $('#dte_fin').val(),
    nb_op: parseInt($('#nb_op').val()) || 0,
    nb_pers: parseInt($('#nb_pers').val()) || 1,
    matricule_personel: parseInt(operateurPrincipal),
    postes_reel: $('#machine_reelle').val() || null,
    // Pour les services non prévus
    numero_commande: currentNumeroCommande || null,
    nom_service: currentService || null
};
```

#### ✅ Correction 3 : Validation adaptée
**Ligne 975-988** : Validation pour accepter `id_fiche_travail = 0`

```javascript
// Validation
// Pour les services non prévus, id_fiche_travail peut être 0
if (data.id_fiche_travail === null || data.id_fiche_travail === undefined) {
    alert('Erreur: Fiche de travail non sélectionnée');
    return;
}

// Pour les services non prévus (id_fiche_travail = 0), vérifier les infos supplémentaires
if (data.id_fiche_travail === 0) {
    if (!data.numero_commande || !data.nom_service) {
        alert('Erreur: Informations de commande et service requises pour un service non prévu');
        return;
    }
}
```

### 2. Backend (`logic/projet11.py`)

#### ✅ Correction 4 : Gestion des services non prévus
**Ligne 673-788** : Nouvelle logique pour gérer `id_fiche_travail = 0`

```python
# SERVICE NON PRÉVU: Si id_fiche_travail est 0 ou NULL, c'est un service non prévu
if not id_fiche_travail or id_fiche_travail == 0:
    print("[INFO] Service non prévu détecté - Traitement sans fiche de travail")
    
    # Récupérer les infos depuis le formulaire
    numero_commande = data.get('numero_commande')
    nom_service = data.get('nom_service')
    nom_poste_reel = data.get('postes_reel')
    
    # Récupérer les infos de la commande directement
    cursor.execute("""
        SELECT 
            C.ID, C.Numero, C.Reference, C.QteComm, C.ID_SOCIETE, S.RaiSocTri
        FROM COMMANDES C
        LEFT JOIN SOCIETES S ON S.ID = C.ID_SOCIETE
        WHERE LTRIM(RTRIM(C.Numero)) = ?
    """, (numero_commande.strip(),))
    
    commande_data = cursor.fetchone()
    
    # Construire un objet fiche_data virtuel
    fiche_data = type('obj', (object,), {
        0: None,  # FT.ID (NULL pour service non prévu)
        1: commande_data[0],  # ID_COMMANDE
        5: commande_data[1],  # Numero_COMMANDES
        6: commande_data[2],  # Reference_COMMANDES
        7: commande_data[3],  # QteComm_COMMANDES
        9: commande_data[5],  # RaiSocTri_SOCIETES
        11: nom_poste_reel or '',  # Nom machine réelle
        14: nom_service or ''  # Nom service
    })()
    
    operation_data = None  # Pas d'opérations prévues
    traitement_data = None  # Pas de traitement prévu
```

#### ✅ Correction 5 : Récupération de l'ID créé
**Ligne 880-901** : Logique adaptée pour retrouver l'enregistrement

```python
# Récupérer l'ID inséré
if id_fiche_travail and id_fiche_travail != 0:
    # Service prévu : recherche par id_fiche_travail
    cursor.execute("""
        SELECT TOP 1 ID 
        FROM WEB_TRAITEMENTS 
        WHERE ID_FICHE_TRAVAIL = ? 
        AND Matricule_personel = ?
        AND DteDeb = ?
        ORDER BY DateCreation DESC
    """, (id_fiche_travail, matricule, data.get('dte_deb')))
else:
    # Service non prévu : recherche par commande, service et date
    cursor.execute("""
        SELECT TOP 1 ID 
        FROM WEB_TRAITEMENTS 
        WHERE (ID_FICHE_TRAVAIL IS NULL OR ID_FICHE_TRAVAIL = 0)
        AND Matricule_personel = ?
        AND DteDeb = ?
        AND Numero_COMMANDES = ?
        AND Nom_GP_SERVICES = ?
        ORDER BY DateCreation DESC
    """, (matricule, data.get('dte_deb'), data.get('numero_commande'), data.get('nom_service')))
```

## 📊 Flux de Traitement

### Service PRÉVU (avec fiche de travail)
```
1. Utilisateur sélectionne une commande
2. Utilisateur sélectionne un service prévu
3. Système charge les infos de GP_FICHES_TRAVAIL
   ├─ Quantité prévue (OpPrevDev)
   ├─ Temps prévu (TpsPrevDev)
   ├─ Machine prévue
   └─ ID_FICHE_TRAVAIL (valide)
4. Utilisateur saisit les données réelles
5. Enregistrement dans WEB_TRAITEMENTS avec ID_FICHE_TRAVAIL
```

### Service NON PRÉVU (sans fiche de travail)
```
1. Utilisateur sélectionne une commande
2. Utilisateur sélectionne "🔧 Autre service (non prévu)"
3. Utilisateur choisit le service manuellement
4. Utilisateur choisit la machine manuellement
5. Système charge UNIQUEMENT les infos de COMMANDES
   ├─ Numéro commande
   ├─ Client
   ├─ Référence
   └─ Quantité commande
6. ID_FICHE_TRAVAIL = 0 (service non prévu)
7. Utilisateur saisit les données réelles
8. Enregistrement dans WEB_TRAITEMENTS avec ID_FICHE_TRAVAIL = 0
```

## 📋 Champs Enregistrés

### Services Prévus vs Non Prévus

| Champ WEB_TRAITEMENTS | Service PRÉVU | Service NON PRÉVU |
|----------------------|---------------|-------------------|
| `ID_FICHE_TRAVAIL` | ID valide | 0 ou NULL |
| `ID_GP_TRAITEMENTS` | ID valide ou NULL | NULL |
| `DteDeb` | ✅ Capturé | ✅ Capturé |
| `DteFin` | ✅ Capturé | ✅ Capturé |
| `NbOp` | ✅ Saisi | ✅ Saisi |
| `NbPers` | ✅ Saisi | ✅ Saisi |
| `Numero_COMMANDES` | ✅ Depuis fiche | ✅ Depuis commande |
| `Reference_COMMANDES` | ✅ Depuis fiche | ✅ Depuis commande |
| `QteComm_COMMANDES` | ✅ Depuis fiche | ✅ Depuis commande |
| `RaiSocTri_SOCIETES` | ✅ Depuis fiche | ✅ Depuis commande |
| `Matricule_personel` | ✅ Saisi | ✅ Saisi |
| `Nom_personel` | ✅ Depuis personel | ✅ Depuis personel |
| `Prenom_personel` | ✅ Depuis personel | ✅ Depuis personel |
| `Nom_GP_SERVICES` | ✅ Depuis fiche | ✅ Saisi manuellement |
| `Nom_GP_POSTES` | ✅ Depuis fiche | ✅ Machine prévue ou vide |
| `OpPrevDev_GP_FICHES_OPERATIONS` | ✅ Depuis opérations | NULL |
| `TpsPrevDev_GP_FICHES_OPERATIONS` | ✅ Depuis opérations | NULL |
| `PostesReel` | ✅ Saisi | ✅ Saisi |
| `TpsReel` | ✅ Calculé | ✅ Calculé |

## 🧪 Scénario de Test

### Test : Ajouter un service non prévu "FACONNAGE"

1. **Sélectionner une commande**
   - Choisir une commande existante (ex: "25-1234")
   
2. **Sélectionner "Autre service (non prévu)"**
   - Dans le champ Service, saisir : `__AUTRE__`
   - Ou sélectionner "🔧 Autre service (non prévu)"

3. **Choisir le service**
   - Un select apparaît avec TOUS les services
   - Sélectionner : `FACONNAGE`

4. **Choisir la machine**
   - Un select apparaît avec les machines du service FACONNAGE
   - Sélectionner : `Déchiqutage`

5. **Vérifier l'affichage**
   - ✅ Message d'information affiché
   - ✅ Section de saisie visible
   - ✅ Champs opérateur, quantité, nb personnes, machine visibles

6. **Remplir les données**
   - Nombre de personnes : `1`
   - Machine réelle : `Déchiqutage` (pré-sélectionné)
   - Opérateur : Sélectionner un opérateur
   - Quantité produite : `1000`

7. **Enregistrer**
   - Cliquer sur "Arrêter et Enregistrer"
   - ✅ Message de confirmation
   - ✅ Redirection vers la liste

8. **Vérifier dans la base**
   ```sql
   SELECT * FROM WEB_TRAITEMENTS 
   WHERE Nom_GP_SERVICES = 'FACONNAGE' 
   AND (ID_FICHE_TRAVAIL IS NULL OR ID_FICHE_TRAVAIL = 0)
   ORDER BY DateCreation DESC
   ```

### Résultats Attendus

```
ID: 12345
ID_FICHE_TRAVAIL: 0
Numero_COMMANDES: 25-1234
Nom_GP_SERVICES: FACONNAGE
Nom_GP_POSTES: NULL ou vide
PostesReel: Déchiqutage
NbOp: 1000
NbPers: 1
TpsReel: (calculé selon durée)
OpPrevDev_GP_FICHES_OPERATIONS: NULL
TpsPrevDev_GP_FICHES_OPERATIONS: NULL
```

## ✅ Résultat Final

**AVANT** :
- Service non prévu → Champs cachés ❌
- Impossible d'enregistrer ❌

**APRÈS** :
- Service non prévu → Champs affichés ✅
- Enregistrement dans WEB_TRAITEMENTS ✅
- Même flux que service prévu ✅
- Distinction via `ID_FICHE_TRAVAIL = 0` ✅

## 📝 Notes Importantes

### Identification des Services Non Prévus
Pour identifier un service non prévu dans la table `WEB_TRAITEMENTS` :
```sql
SELECT * FROM WEB_TRAITEMENTS 
WHERE ID_FICHE_TRAVAIL IS NULL OR ID_FICHE_TRAVAIL = 0
```

### Rapports et Statistiques
Les requêtes de statistiques doivent maintenant tenir compte des services non prévus :
```sql
-- Tous les traitements (prévus et non prévus)
SELECT COUNT(*) FROM WEB_TRAITEMENTS

-- Services prévus uniquement
SELECT COUNT(*) FROM WEB_TRAITEMENTS 
WHERE ID_FICHE_TRAVAIL IS NOT NULL AND ID_FICHE_TRAVAIL > 0

-- Services non prévus uniquement
SELECT COUNT(*) FROM WEB_TRAITEMENTS 
WHERE ID_FICHE_TRAVAIL IS NULL OR ID_FICHE_TRAVAIL = 0
```

## 📂 Fichiers Modifiés

| Fichier | Lignes | Description |
|---------|--------|-------------|
| `templates/projet11_nouveau.html` | 551-598 | Génération champs opérateurs |
| `templates/projet11_nouveau.html` | 962-988 | Envoi données + validation |
| `logic/projet11.py` | 673-788 | Gestion services non prévus (backend) |
| `logic/projet11.py` | 880-901 | Récupération ID traitement créé |

---

✅ **Les services non prévus peuvent maintenant être enregistrés dans WEB_TRAITEMENTS !** 🎉





















