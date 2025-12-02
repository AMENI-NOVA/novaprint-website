# Projet 11 - Sélection par Numéro de Commande

## ✅ Modification Implémentée

Le formulaire de création de traitement a été modifié pour permettre une **sélection en cascade** basée sur le **numéro de commande** (dossier).

---

## 🎯 Nouveau Flux de Sélection

### Avant
1. ❌ Sélectionner directement une fiche de travail (difficile à trouver)
2. Remplir les informations

### Maintenant
1. ✅ **ÉTAPE 1**: Sélectionner le numéro de commande (dossier)
2. ✅ **ÉTAPE 2**: Sélectionner la fiche de travail pour cette commande
3. ✅ **ÉTAPE 3**: Remplir les informations du traitement

---

## 📋 Fonctionnement Détaillé

### ÉTAPE 1️⃣ : Sélection du Numéro de Commande

L'utilisateur voit une liste déroulante avec:
```
2025100018 - MPP HOUSE - Étiquettes 100x50
2025100017 - CLIENT ABC - Brochures A4
2025100016 - AUTRE CLIENT - Cartes de visite
...
```

**Avantages**:
- ✓ Liste claire et lisible
- ✓ Numéro de commande visible en premier
- ✓ Client et référence affichés
- ✓ Facile de trouver le dossier souhaité

### ÉTAPE 2️⃣ : Sélection de la Fiche de Travail

Une fois la commande sélectionnée, le système charge **automatiquement** les fiches de travail associées:

```
Fiche #432530 - SOUS-TRAITANCE - LIVRAISON
Fiche #432531 - IMPRESSION - OFFSET
Fiche #432532 - FAÇONNAGE - DÉCOUPE
...
```

**Avantages**:
- ✓ Uniquement les fiches de cette commande
- ✓ Liste filtrée et pertinente
- ✓ Service et poste visibles
- ✓ Choix simplifié

### ÉTAPE 3️⃣ : Informations du Traitement

Ensuite, l'utilisateur remplit:
- Date de début
- Date de fin
- Nombre d'opérations
- Nombre de personnes
- Opérateur

---

## 🔧 Modifications Techniques

### 1. Module Python (`logic/projet11.py`)

**Nouvelles fonctions ajoutées**:

```python
def get_numeros_commandes_disponibles():
    """Récupère les numéros de commandes disponibles"""
    # Retourne: liste des commandes avec fiches disponibles
```

```python
def get_fiches_by_numero_commande(numero_commande):
    """Récupère les fiches pour une commande spécifique"""
    # Retourne: fiches de travail de cette commande uniquement
```

### 2. Routes Flask (`routes/projet11_routes.py`)

**Nouveaux endpoints API**:

```python
@projet11_bp.route('/projet11/api/numeros-commandes')
def api_numeros_commandes():
    # GET: Liste des numéros de commandes disponibles
```

```python
@projet11_bp.route('/projet11/api/fiches-by-commande/<numero>')
def api_fiches_by_commande(numero):
    # GET: Fiches de travail pour une commande spécifique
```

**Route modifiée**:

```python
@projet11_bp.route('/projet11/nouveau')
def nouveau_traitement():
    # Passe maintenant "commandes" au lieu de "fiches"
```

### 3. Template HTML (`templates/projet11_nouveau.html`)

**Structure modifiée**:

```html
<!-- ÉTAPE 1 -->
<select id="numero_commande">
    <!-- Liste des commandes -->
</select>

<!-- Info commande sélectionnée -->
<div id="infoCommandeSelectionnee">
    <!-- Numéro, client, référence -->
</div>

<!-- ÉTAPE 2 -->
<select id="id_fiche_travail">
    <!-- Chargé dynamiquement via AJAX -->
</select>

<!-- ÉTAPE 3 -->
<!-- Dates, nombres, opérateur -->
```

**JavaScript ajouté**:

```javascript
// Écoute changement de commande
numero_commande.addEventListener('change', function() {
    // Charger les fiches via AJAX
    fetch(`/projet11/api/fiches-by-commande/${numero}`)
        .then(response => response.json())
        .then(fiches => {
            // Remplir le select des fiches
        });
});
```

---

## 🎨 Interface Utilisateur

### Écran de Sélection

```
┌─────────────────────────────────────────────────┐
│ 1️⃣ Numéro de Commande (Dossier) *               │
│ ┌───────────────────────────────────────────┐   │
│ │ 2025100018 - MPP HOUSE                    │   │
│ └───────────────────────────────────────────┘   │
│ Choisissez d'abord le dossier...                │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│ 📋 Commande Sélectionnée                        │
│ N° Commande: 2025100018                         │
│ Client: MPP HOUSE                                │
│ Référence: Étiquettes 100x50                    │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│ 2️⃣ Fiche de Travail *                           │
│ ┌───────────────────────────────────────────┐   │
│ │ Fiche #432530 - SOUS-TRAITANCE - LIVRAISON│   │
│ └───────────────────────────────────────────┘   │
│ Sélectionnez la fiche de travail...             │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│ 3️⃣ Informations du Traitement                   │
│ Date Début: [......]  Date Fin: [......]        │
│ Nb Opérations: [...]  Nb Personnes: [...]       │
│ Opérateur: [...]                                 │
└─────────────────────────────────────────────────┘
```

---

## 🚀 Avantages de Cette Approche

### 1. Meilleure Expérience Utilisateur
- ✓ Flux logique et intuitif
- ✓ Sélection par étapes
- ✓ Recherche facilitée par numéro de commande
- ✓ Moins de confusion

### 2. Données Filtrées
- ✓ Uniquement les fiches pertinentes
- ✓ Pas de surcharge d'informations
- ✓ Choix plus rapide

### 3. Clarté Visuelle
- ✓ Numérotation des étapes (1️⃣ 2️⃣ 3️⃣)
- ✓ Affichage progressif
- ✓ Informations contextuelles

### 4. Performance
- ✓ Chargement dynamique (AJAX)
- ✓ Pas de surcharge au démarrage
- ✓ Données à la demande

---

## 📊 Exemple d'Utilisation

### Scénario: Créer un traitement pour la commande 2025100018

1. **Ouvrir la page**: `http://localhost:5000/projet11/nouveau`

2. **ÉTAPE 1**: Sélectionner dans la liste déroulante
   ```
   2025100018 - MPP HOUSE - Étiquettes 100x50
   ```
   → Un encadré bleu apparaît avec les infos de la commande

3. **ÉTAPE 2**: Le système charge automatiquement les fiches
   ```
   Fiche #432530 - SOUS-TRAITANCE - LIVRAISON
   Fiche #432531 - IMPRESSION - OFFSET
   ```
   → Sélectionner la fiche souhaitée

4. **ÉTAPE 3**: Remplir les informations
   ```
   Date début: 2025-10-15 08:00
   Opérations: 100
   Personnes: 2
   Opérateur: ABBES MARIEM
   ```

5. **Enregistrer** → Traitement créé! ✅

---

## 🔄 Flux de Données

```
User sélectionne commande "2025100018"
    ↓
JavaScript détecte le changement
    ↓
Appel AJAX: GET /projet11/api/fiches-by-commande/2025100018
    ↓
Python: get_fiches_by_numero_commande("2025100018")
    ↓
SQL: SELECT ... WHERE C.Numero = '2025100018'
    ↓
Retour JSON: [
    {id_fiche_travail: 432530, service: "SOUS-TRAITANCE", ...},
    {id_fiche_travail: 432531, service: "IMPRESSION", ...}
]
    ↓
JavaScript remplit le <select> des fiches
    ↓
User sélectionne une fiche
    ↓
Affichage des détails
    ↓
User remplit et enregistre
```

---

## 📁 Fichiers Modifiés

### Backend
- ✅ `logic/projet11.py` - 2 nouvelles fonctions
- ✅ `routes/projet11_routes.py` - 2 nouveaux endpoints API

### Frontend
- ✅ `templates/projet11_nouveau.html` - Structure et JavaScript

### Supprimés
- ❌ `check_web_traitements.py` - Fichier temporaire

---

## ✅ Tests

Pour tester la nouvelle sélection:

1. **Démarrer le serveur**:
   ```bash
   python app.py
   ```

2. **Ouvrir le navigateur**:
   ```
   http://localhost:5000/projet11/nouveau
   ```

3. **Vérifier**:
   - ✓ La liste des commandes s'affiche
   - ✓ Sélectionner une commande affiche ses infos
   - ✓ Les fiches se chargent automatiquement
   - ✓ Sélectionner une fiche affiche les détails
   - ✓ Le formulaire est complet et fonctionnel

---

## 🎯 Résultat

La sélection par **numéro de commande** rend le formulaire:

✅ Plus intuitif  
✅ Plus rapide  
✅ Plus clair  
✅ Mieux organisé  
✅ Plus professionnel  

**L'utilisateur trouve son dossier facilement et crée le traitement en 3 étapes simples!**

---

*Modification implémentée - Octobre 2024*


