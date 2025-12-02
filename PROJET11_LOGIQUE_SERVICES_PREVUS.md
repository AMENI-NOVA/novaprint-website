# Projet 11 - Logique des Services Prévus et Chronomètre

## 🎯 Nouvelle Logique Implémentée

Le système fonctionne maintenant en se basant sur les **services et postes PRÉVUS** dans GP_FICHES_TRAVAIL.

---

## 📋 Nouveau Flux de Travail

### ÉTAPE 1️⃣: Sélectionner le Numéro de Commande
```
Exemple: 2025050026 - CCIS - badges MEDIBAT 2025
```

### ÉTAPE 2️⃣: Sélectionner le SERVICE Prévu
```
Services disponibles (basés sur GP_FICHES_TRAVAIL):
- OFFSET FEUILLES (1 poste prévu)
- PRE-PRESS (2 postes prévus)
- Massicotage (1 poste prévu)
- CONDITIONNEMENT (1 poste prévu)
- SOUS-TRAITANCE (1 poste prévu)
```

### ÉTAPE 3️⃣: Machine et Quantité S'affichent Automatiquement
```
Service sélectionné: OFFSET FEUILLES

📋 Informations Prévues (Automatiques):
  Machine prévue: XL75
  Quantité prévue: 15,000
  Temps prévu: 2.5 heures
```

### ÉTAPE 4️⃣: Traitements Existants du Service
```
⚠️ Productions déjà enregistrées pour OFFSET FEUILLES:

• Session 1: 15/10 08:00 → 12:00 ✅ Terminé
             5,000 opérations - XL75 - ABBES - 4h00

• Session 2: 15/10 14:00 → En cours ⏳
             3,000 opérations - XL75 - BACCOUCHE - 2h15

Total produit dans ce service: 8,000 / 15,000
Reste à produire: 7,000
```

### ÉTAPE 5️⃣: Sélectionner Opérateur + Machine Réelle
```
Opérateur: [ABBES MARIEM]
Machine réelle: [XL75] (ou CD102 si changement)
```

### ÉTAPE 6️⃣: Chronomètre Démarre Automatiquement ⏱️
```
⏱️ CHRONOMÈTRE EN COURS

Démarré à: 15/10/2025 08:30:15
Temps écoulé: 00:15:32

[ARRÊTER ET ENREGISTRER]
```

### ÉTAPE 7️⃣: Enregistrement Automatique
```
Quand on clique sur "Enregistrer":
  ✅ Temps début: 15/10/2025 08:30:15 (auto)
  ✅ Temps fin: 15/10/2025 11:45:47 (auto)
  ✅ Durée: 3h15min32s (calculée)
  ✅ Quantité produite: [saisie utilisateur]
```

---

## 🔧 Fonctions Backend Créées

### 1. get_services_prevus_by_commande(numero_commande)

**Objectif**: Récupérer les services qui ont des postes prévus pour cette commande

**Retour**:
```python
[
    {
        "id_service": 6,
        "nom_service": "OFFSET FEUILLES",
        "nb_fiches": 1  # Nombre de postes prévus dans ce service
    },
    {
        "id_service": 3,
        "nom_service": "PRE-PRESS",
        "nb_fiches": 2
    }
]
```

---

### 2. get_postes_prevus_by_commande_service(numero_commande, nom_service)

**Objectif**: Récupérer les postes/machines PRÉVUS pour un service spécifique

**Retour**:
```python
[
    {
        "id_fiche_travail": 409718,
        "id_poste": 45,
        "nom_poste": "XL75",
        "nom_service": "OFFSET FEUILLES",
        "qte_prevue": 15000,
        "op_prev_dev": 15000.000,
        "tps_prev_dev": 2.500  # Heures prévues
    }
]
```

---

### 3. get_traitements_existants_service(numero_commande, nom_service)

**Objectif**: Récupérer les traitements déjà enregistrés pour ce service

**Retour**:
```python
[
    {
        "id": 1,
        "dte_deb": "2025-10-15 08:00",
        "dte_fin": "2025-10-15 12:00",
        "nb_op": 5000,
        "nb_pers": 2,
        "postes_reel": "XL75",
        "operateur": "ABBES MARIEM",
        "duree_minutes": 240,
        "duree_heures": 4.000,
        "en_cours": False
    }
]
```

---

## 🌐 Routes API Créées

### 1. GET /projet11/api/services-prevus/{numero_commande}

**Exemple**: `/projet11/api/services-prevus/2025050026`

**Retour**: Liste des services prévus pour cette commande

---

### 2. GET /projet11/api/postes-prevus/{numero_commande}/{service}

**Exemple**: `/projet11/api/postes-prevus/2025050026/OFFSET%20FEUILLES`

**Retour**: Postes prévus pour ce service dans cette commande

---

### 3. GET /projet11/api/traitements-service/{numero_commande}/{service}

**Exemple**: `/projet11/api/traitements-service/2025050026/OFFSET%20FEUILLES`

**Retour**: Traitements déjà enregistrés pour ce service

---

## ⏱️ Logique du Chronomètre

### Démarrage Automatique

**Condition**: Dès que l'utilisateur a sélectionné:
1. ✅ Numéro de commande
2. ✅ Service
3. ✅ Machine/Poste
4. ✅ Opérateur

**Action**: Le chronomètre démarre automatiquement en JavaScript

**Code**:
```javascript
let chronoStart = null;
let chronoInterval = null;

function demarrerChrono() {
    chronoStart = new Date();
    
    chronoInterval = setInterval(() => {
        const now = new Date();
        const diff = now - chronoStart;
        const heures = Math.floor(diff / 3600000);
        const minutes = Math.floor((diff % 3600000) / 60000);
        const secondes = Math.floor((diff % 60000) / 1000);
        
        document.getElementById('chrono').textContent = 
            `${heures.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secondes.toString().padStart(2, '0')}`;
    }, 1000);
}
```

---

### Enregistrement

**Quand on clique sur "Enregistrer"**:

```javascript
function enregistrer() {
    const now = new Date();
    
    const data = {
        dte_deb: chronoStart.toISOString(),     // Début chrono
        dte_fin: now.toISOString(),              // Maintenant
        duree_minutes: Math.floor((now - chronoStart) / 60000),
        // ... autres champs
    };
    
    // Arrêter le chrono
    clearInterval(chronoInterval);
    
    // Envoyer à l'API
    fetch('/projet11/api/traitements', {
        method: 'POST',
        body: JSON.stringify(data)
    });
}
```

---

## 🎨 Nouvelle Interface

### Formulaire Complet

```
┌────────────────────────────────────────────────┐
│ 1️⃣ Numéro de Commande *                        │
│ [2025050026 - CCIS - badges MEDIBAT 2025]     │
└────────────────────────────────────────────────┘

┌────────────────────────────────────────────────┐
│ 2️⃣ Service à Traiter *                         │
│ [OFFSET FEUILLES] (1 poste prévu)              │
└────────────────────────────────────────────────┘

┌────────────────────────────────────────────────┐
│ 📋 Informations Prévues (Automatiques)         │
│ Machine prévue: XL75                            │
│ Quantité prévue: 15,000                        │
│ Temps prévu: 2.5 heures                        │
└────────────────────────────────────────────────┘

┌────────────────────────────────────────────────┐
│ ⚠️ Productions Déjà Enregistrées (OFFSET)      │
│                                                 │
│ • Session 1: 15/10 08:00→12:00 ✅              │
│   5,000 op - XL75 - ABBES - 4h00               │
│                                                 │
│ • Session 2: 15/10 14:00→En cours ⏳           │
│   3,000 op - XL75 - BACCOUCHE - 2h15           │
│                                                 │
│ Total produit: 8,000 / 15,000                  │
│ Reste: 7,000                                    │
└────────────────────────────────────────────────┘

┌────────────────────────────────────────────────┐
│ 3️⃣ Traitement Actuel                           │
│                                                 │
│ Opérateur: [ABBES MARIEM]                      │
│ Machine réelle: [XL75]                         │
│ Quantité produite: [7000]                      │
│                                                 │
│ ⏱️ CHRONOMÈTRE: 00:15:32                       │
│ Démarré à: 15/10/2025 16:30:15                │
│                                                 │
│ [🛑 ARRÊTER ET ENREGISTRER]                    │
└────────────────────────────────────────────────┘
```

---

## 📊 Exemple Complet

### Commande 2025050026 - CCIS - 15,000 badges

#### Services Prévus

| Service | Postes Prévus | Quantité |
|---------|---------------|----------|
| PRE-PRESS | LABO, Prosetter | 15,000 |
| OFFSET FEUILLES | XL75 | 15,000 |
| Massicotage | POLAR78 | 15,000 |
| CONDITIONNEMENT | CONDITIONNEMENT | 15,000 |
| SOUS-TRAITANCE | LIVRAISON | 15,000 |

#### Production dans OFFSET FEUILLES

**Poste prévu**: XL75  
**Quantité prévue**: 15,000  
**Temps prévu**: 2.5h  

**Sessions enregistrées**:

1. **Lundi 08:00**
   - Opérateur: ABBES
   - Machine: XL75
   - Début: 08:00:00
   - Fin: 12:00:00
   - Durée: 4h00 (240min)
   - Quantité: 5,000
   - Statut: ✅ Terminé

2. **Lundi 14:00**
   - Opérateur: BACCOUCHE
   - Machine: XL75
   - Début: 14:00:00
   - Fin: En cours...
   - Durée: 2h15 (135min)
   - Quantité: 3,000
   - Statut: ⏳ En cours

**Total produit**: 8,000  
**Reste**: 7,000  

**Nouvelle session** (à créer):
- Opérateur: [À sélectionner]
- Machine: XL75 (ou CD102 si changement)
- Chrono: Démarre dès la sélection
- Quantité: 7,000 (suggérée)

---

## 🔧 Implémentation Technique

### Étapes d'Implémentation

Cette fonctionnalité nécessite:

#### ✅ FAIT
1. Fonctions backend créées
2. Routes API créées
3. Support production par lots

#### 🔄 EN COURS
4. Template HTML avec sélection par service
5. JavaScript du chronomètre
6. Affichage des traitements existants du service
7. Calcul automatique du reste à produire

#### 📋 À FAIRE
8. Tests complets
9. Documentation utilisateur
10. Ajout d'un champ "DureeReelle" dans la table

---

## 🎯 Prochaine Étape

Voulez-vous que je créé maintenant:

### Option A: Template Complet avec Chronomètre
- Nouveau formulaire avec sélection par service
- Chronomètre automatique
- Affichage du reste à produire
- **Temps estimé**: Complexe, ~200 lignes de code

### Option B: Implémentation Progressive
- D'abord: Sélection par service (sans chrono)
- Ensuite: Affichage des prévisions
- Plus tard: Chronomètre
- **Avantage**: Tests progressifs

### Option C: Garder la Version Actuelle + Documentation
- Le système actuel fonctionne déjà bien
- Documentation de la logique souhaitée
- Implémentation ultérieure

---

## 📊 Résumé de ce qui est Prêt

### ✅ Backend Prêt
- `get_services_prevus_by_commande()`
- `get_postes_prevus_by_commande_service()`
- `get_traitements_existants_service()`

### ✅ API Prête
- `GET /projet11/api/services-prevus/<numero>`
- `GET /projet11/api/postes-prevus/<numero>/<service>`
- `GET /projet11/api/traitements-service/<numero>/<service>`

### 🔄 Frontend À Adapter
- Template HTML à refondre pour la nouvelle logique
- JavaScript du chronomètre à implémenter
- Affichage des totaux/restes

---

**Que souhaitez-vous que je fasse maintenant?**

Je recommande l'**Option B** (implémentation progressive) pour éviter de tout casser et tester au fur et à mesure.

Voulez-vous que je continue avec la refonte du template?

---

*Fonctions backend prêtes - En attente de directive pour le frontend*



























