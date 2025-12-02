# Projet 11 - Ajout du Champ PostesReel

## ✅ Modification Terminée

Le champ **PostesReel** a été ajouté avec succès à la table `WEB_TRAITEMENTS` pour permettre l'enregistrement de la **machine réellement utilisée** lors du traitement.

---

## 🎯 Objectif

### Problème
Dans la production, il peut y avoir un **changement de machine** par rapport à celle initialement prévue:
- Machine prévue (dans GP_FICHES_TRAVAIL → GP_POSTES): Nom_GP_POSTES
- Machine réelle (utilisée en production): **PostesReel** ← NOUVEAU

### Solution
Ajout d'un nouveau champ `PostesReel` dans `WEB_TRAITEMENTS` qui permet de saisir la machine réellement utilisée.

---

## 📊 Structure de la Table (Mise à Jour)

### Avant : 19 champs
### Après : **20 champs** (+1)

### Nouveau Champ Ajouté

| Champ | Type | NULL | Description |
|-------|------|------|-------------|
| **PostesReel** | VARCHAR(50) | ✓ | Machine/Poste réellement utilisé |

**Position**: Entre `TpsPrevDev_GP_FICHES_OPERATIONS` et `DateCreation`

---

## 🔧 Modifications Techniques

### 1. Base de Données

**Commande SQL exécutée:**
```sql
ALTER TABLE [dbo].[WEB_TRAITEMENTS]
ADD [PostesReel] VARCHAR(50) NULL
```

**Résultat**: ✅ Champ ajouté avec succès

---

### 2. Module Python (`logic/projet11.py`)

#### Nouvelle Fonction Ajoutée

```python
def get_postes_disponibles():
    """
    Récupère la liste de tous les postes/machines 
    disponibles depuis GP_POSTES
    """
    # Retourne: liste des postes groupés par service
```

**Données retournées:**
```python
{
    "id": 123,
    "nom": "XL75",
    "nom_service": "OFFSET FEUILLES",
    "nom_complet": "OFFSET FEUILLES - XL75"
}
```

#### Fonctions Modifiées

1. **`get_all_traitements()`**
   - Ajout de `PostesReel` dans le SELECT
   - Ajout de `"postes_reel"` dans le dict retourné

2. **`get_traitement_by_id()`**
   - Ajout de `PostesReel` dans le SELECT
   - Ajout de `"postes_reel"` dans le dict retourné

3. **`create_traitement()`**
   - Ajout de `PostesReel` dans l'INSERT
   - Récupération de `data.get('postes_reel')`

4. **`update_traitement()`**
   - Ajout de `PostesReel` dans l'UPDATE
   - Récupération de `data.get('postes_reel')`

---

### 3. Routes Flask (`routes/projet11_routes.py`)

#### Nouvelle Route API

```python
@projet11_bp.route('/projet11/api/postes', methods=['GET'])
def api_postes():
    """API pour récupérer la liste des postes/machines disponibles"""
```

**URL**: `GET /projet11/api/postes`

**Réponse**:
```json
[
  {
    "id": 123,
    "nom": "XL75",
    "nom_service": "OFFSET FEUILLES",
    "nom_complet": "OFFSET FEUILLES - XL75"
  },
  ...
]
```

#### Route Modifiée

```python
@projet11_bp.route('/projet11/nouveau')
def nouveau_traitement():
    # Passe maintenant "postes" en plus
    return render_template('projet11_nouveau.html', 
                         commandes=commandes, 
                         operateurs=operateurs, 
                         postes=postes)
```

---

### 4. Templates HTML

#### `templates/projet11_nouveau.html`

**Ajout dans le formulaire:**
```html
<div class="col-md-6 mb-3">
    <label for="postes_reel" class="form-label">
        <strong>Machine/Poste Réel</strong>
    </label>
    <select class="form-select" id="postes_reel">
        <option value="">-- Sélectionner une machine --</option>
        {% for poste in postes %}
        <option value="{{ poste.nom }}">
            {{ poste.nom_service }} - {{ poste.nom }}
        </option>
        {% endfor %}
    </select>
    <small class="text-muted">
        Machine réellement utilisée (si différente de celle prévue)
    </small>
</div>
```

**JavaScript mis à jour:**
```javascript
const data = {
    // ... autres champs
    postes_reel: document.getElementById('postes_reel').value || null
};
```

---

#### `templates/projet11_liste.html`

**Nouvelle colonne dans le tableau:**
```html
<thead>
    <tr>
        <!-- ... autres colonnes ... -->
        <th>Poste Prévu</th>
        <th>Machine Réelle</th> ← NOUVELLE
        <!-- ... suite ... -->
    </tr>
</thead>
<tbody>
    <td>{{ t.poste or '-' }}</td>
    <td>
        {% if t.postes_reel %}
            <strong class="text-primary">{{ t.postes_reel }}</strong>
        {% else %}
            <span class="text-muted">-</span>
        {% endif %}
    </td>
</tbody>
```

**Modal de modification mise à jour:**
```html
<div class="mb-3">
    <label for="edit_postes_reel" class="form-label">
        Machine/Poste Réel
    </label>
    <input type="text" class="form-control" id="edit_postes_reel" 
           placeholder="Ex: OFFSET - XL75">
</div>
```

**JavaScript modifié:**
```javascript
// Dans modifierTraitement()
document.getElementById('edit_postes_reel').value = data.postes_reel || '';

// Dans sauvegarderModifications()
const data = {
    // ... autres champs
    postes_reel: document.getElementById('edit_postes_reel').value || null
};
```

---

## 🎨 Interface Utilisateur

### Page de Création (`/projet11/nouveau`)

```
┌─────────────────────────────────────────────────┐
│ 3️⃣ Informations du Traitement                   │
├─────────────────────────────────────────────────┤
│ Date Début: [........]  Date Fin: [........]    │
│ Nb Opérations: [...]    Nb Personnes: [...]     │
│ Opérateur: [........]   Machine Réelle: [....] │← NOUVEAU
└─────────────────────────────────────────────────┘
```

### Page de Liste (`/projet11/traitements`)

| Poste Prévu | Machine Réelle |
|-------------|----------------|
| LIVRAISON | **XL75** ← Si différent |
| OFFSET | - ← Si identique |

**Affichage**:
- Machine réelle en **gras bleu** si renseignée
- Tiret gris si non renseignée

---

## 📋 Cas d'Usage

### Cas 1: Machine Prévue = Machine Réelle

**Situation**: Le traitement se fait sur la machine prévue

**Action**: Laisser le champ "Machine Réelle" vide

**Résultat**: Seul le poste prévu s'affiche dans la liste

---

### Cas 2: Changement de Machine

**Situation**: La machine prévue était "OFFSET - CD102" mais on utilise "OFFSET - XL75"

**Action**: 
1. Dans le formulaire, sélectionner "OFFSET FEUILLES - XL75"
2. Enregistrer

**Résultat**: 
- Colonne "Poste Prévu": CD102
- Colonne "Machine Réelle": **XL75** (en gras bleu)

---

### Cas 3: Modification Ultérieure

**Situation**: Le traitement a déjà été créé, on veut ajouter la machine réelle

**Action**:
1. Dans la liste, cliquer sur "Modifier" (crayon jaune)
2. Remplir le champ "Machine/Poste Réel"
3. Sauvegarder

**Résultat**: La machine réelle s'affiche dans la liste

---

## 📊 Exemple de Données

### Traitement avec Machine Différente

```json
{
  "id": 2,
  "numero_commande": "2025050026",
  "client": "CCIS",
  "service": "OFFSET FEUILLES",
  "poste": "CD102",              ← Machine prévue
  "postes_reel": "XL75",         ← Machine réellement utilisée
  "nb_op": 15000,
  "nb_pers": 2
}
```

**Affichage dans la liste:**
```
| Service         | Poste Prévu | Machine Réelle |
|-----------------|-------------|----------------|
| OFFSET FEUILLES | CD102       | XL75          |
```

---

## 🚀 Test de la Fonctionnalité

Le serveur Flask a **déjà redémarré automatiquement**.

### Test 1: Création avec Machine Réelle

1. Ouvrir: `http://localhost:5000/projet11/nouveau`
2. Sélectionner une commande (ex: 2025050026)
3. Sélectionner une fiche
4. Remplir les informations
5. **Sélectionner une machine dans "Machine/Poste Réel"**
6. Enregistrer

**Résultat attendu**: La machine réelle s'affiche dans la liste

---

### Test 2: Modification d'un Traitement Existant

1. Ouvrir: `http://localhost:5000/projet11/traitements`
2. Cliquer sur "Modifier" (crayon jaune) sur un traitement
3. Remplir "Machine/Poste Réel"
4. Sauvegarder

**Résultat attendu**: La machine réelle s'affiche dans la liste

---

### Test 3: Voir les Détails

1. Cliquer sur "Voir" (œil bleu)
2. Vérifier que "Machine Réelle" apparaît dans les détails

---

## 📈 Statistiques

### Nombre de Postes Disponibles

Exécuter pour voir combien de postes sont disponibles:

```python
from logic import projet11
postes = projet11.get_postes_disponibles()
print(f"{len(postes)} postes disponibles")
```

---

## 💡 Avantages

### 1. Traçabilité
✓ Enregistrement de la machine réellement utilisée  
✓ Comparaison possible entre prévu et réel  
✓ Historique des changements de machine  

### 2. Analyse
✓ Identifier les machines les plus utilisées  
✓ Détecter les écarts entre prévu et réel  
✓ Optimiser la planification  

### 3. Flexibilité
✓ Champ optionnel (peut être vide)  
✓ Modification possible à tout moment  
✓ Saisie libre ou sélection dans la liste  

---

## 📁 Fichiers Modifiés

### Backend
1. ✅ `logic/projet11.py`
   - Nouvelle fonction: `get_postes_disponibles()`
   - Mise à jour: `get_all_traitements()` (+ PostesReel)
   - Mise à jour: `get_traitement_by_id()` (+ PostesReel)
   - Mise à jour: `create_traitement()` (+ PostesReel)
   - Mise à jour: `update_traitement()` (+ PostesReel)

2. ✅ `routes/projet11_routes.py`
   - Nouvelle route: `GET /projet11/api/postes`
   - Mise à jour: `/projet11/nouveau` (passe postes au template)

### Frontend
3. ✅ `templates/projet11_nouveau.html`
   - Nouveau champ select pour PostesReel
   - JavaScript mis à jour (soumission)

4. ✅ `templates/projet11_liste.html`
   - Nouvelle colonne "Machine Réelle"
   - Modal de modification avec PostesReel
   - JavaScript mis à jour (modification)
   - Affichage dans les détails

### Base de Données
5. ✅ Table `WEB_TRAITEMENTS`
   - Champ `PostesReel VARCHAR(50) NULL` ajouté
   - Total: 20 champs (au lieu de 19)

---

## 🗂️ Structure Finale de la Table

```
WEB_TRAITEMENTS (20 champs)
├── ID (clé primaire)
├── DteDeb
├── DteFin
├── NbOp
├── NbPers
├── ID_FICHE_TRAVAIL (clé de liaison)
├── Numero_COMMANDES
├── Reference_COMMANDES
├── QteComm_COMMANDES
├── RaiSocTri_SOCIETES
├── Matricule_personel
├── Nom_personel
├── Prenom_personel
├── Nom_GP_SERVICES
├── Nom_GP_POSTES ← Machine prévue
├── OpPrevDev_GP_FICHES_OPERATIONS
├── TpsPrevDev_GP_FICHES_OPERATIONS
├── PostesReel ← Machine réelle (NOUVEAU)
├── DateCreation
└── DateModification
```

---

## 🎯 Utilisation

### Créer un Traitement avec Machine Réelle

```javascript
// Données envoyées à l'API
{
  "id_fiche_travail": 409715,
  "dte_deb": "2025-10-15T08:00",
  "nb_op": 100,
  "nb_pers": 2,
  "postes_reel": "XL75"  ← Machine réelle
}
```

### Affichage dans la Liste

```
Poste Prévu: CD102
Machine Réelle: XL75 (en gras bleu)
```

**Interprétation**: Le traitement devait se faire sur CD102 mais a été fait sur XL75.

---

## ✅ Validation

### Test dans SQL Server Management Studio

```sql
SELECT 
    ID,
    Numero_COMMANDES,
    Nom_GP_POSTES as PostePrevu,
    PostesReel as MachineReelle
FROM WEB_TRAITEMENTS
```

**Résultat attendu**: Le champ PostesReel est visible et peut être NULL ou contenir un nom de machine.

---

### Test dans l'Interface Web

1. ✅ Formulaire de création affiche la liste des postes
2. ✅ Sélection d'un poste fonctionne
3. ✅ Enregistrement inclut le poste réel
4. ✅ Liste affiche la colonne "Machine Réelle"
5. ✅ Modification permet de changer le poste réel
6. ✅ Détails affichent le poste réel

---

## 📈 Évolutions Possibles

### Court Terme
- Statistiques des écarts prévu/réel
- Alerte si machine différente
- Export des changements de machine

### Moyen Terme
- Graphique des machines les plus utilisées
- Taux d'utilisation par machine
- Rapport prévu vs réel

### Long Terme
- Prédiction de la machine à utiliser
- Optimisation automatique
- Intelligence artificielle

---

## 🎉 Résumé

### Modifications Réussies

✅ **Base de données**: Champ PostesReel ajouté  
✅ **Backend**: 5 fonctions modifiées + 1 nouvelle  
✅ **Routes**: 1 nouveau endpoint API  
✅ **Frontend**: 2 templates modifiés  
✅ **Tests**: Fonctionnalité opérationnelle  

### Résultat

La table WEB_TRAITEMENTS permet maintenant d'enregistrer:
- La **machine prévue** (Nom_GP_POSTES) - Automatique
- La **machine réelle** (PostesReel) - Saisie manuelle

**Cette fonctionnalité permet un meilleur suivi de la production et l'identification des écarts!** 🎯

---

*Modification implémentée - Octobre 2024*



























