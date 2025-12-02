# Projet 15 - Analyse de la Corrélation Déchets/CA

## 📌 Structure

### Routes disponibles

#### 1. Page d'accueil
- **URL** : `/projet15/`
- **Affichage** : 
  - En-tête du projet
  - 2 boutons de sélection de section
  - Aucune donnée affichée

#### 2. Tableau de données
- **URL** : `/projet15/tableau`
- **Affichage** :
  - Barre de navigation entre sections (avec section active)
  - Filtre par année
  - Tableau mensuel avec données de déchets et CA
  - Actions : Modifier en ligne

#### 3. Graphique comparatif
- **URL** : `/projet15/graphique`
- **Affichage** :
  - Barre de navigation entre sections (avec section active)
  - Filtre par année
  - Cartes statistiques (Nombre de mois, Total déchets, Moyenne déchets, Total CA, Moyenne CA)
  - **Graphique global** : Évolution Mensuelle - Total Déchets vs Chiffre d'Affaires
  - **3 graphiques séparés par type** :
    - 📄 Papier Offset vs CA (couleur : 🟠 Orange)
    - 📦 Carton blanc gris vs CA (couleur : 🔴 Rouge)
    - 🌳 Carton blanc bois vs CA (couleur : 🟡 Jaune)

## 🎨 Couleurs des graphiques

| Type de déchet | Couleur | Code RGBA |
|----------------|---------|-----------|
| Papier Offset | 🟠 Orange vif | rgba(255, 152, 0, 1) |
| Carton blanc gris | 🔴 Rouge | rgba(244, 67, 54, 1) |
| Carton blanc bois | 🟡 Jaune | rgba(255, 235, 59, 1) |
| Chiffre d'Affaires | 🔵 Bleu | rgba(33, 150, 243, 1) |

## 📊 Données affichées

### Filtrage
- **Période** : Uniquement données de 2025 et après (les données de 2023-2024 sont des tests et ne sont pas affichées)
- **Déchets** : Uniquement déchets solides mesurés en kg (les déchets liquides en m³ sont exclus)

### Agrégation
- Les données sont agrégées **par mois**
- Chaque ligne représente :
  - **Déchets** : Total mensuel en kg (somme de tous les types solides)
  - **CA** : Total mensuel du chiffre d'affaires HT

### Source des données
- **Table principale** : `WEB_Coor_CH_dech` (table de corrélation, ne modifie pas les sources)
- **Sources d'origine** :
  - `WEB_Suivi_Dechets` (Date, Type, Quantite, Unite)
  - `FACTURES` (DteFact, TotalHTPce)

## 🔧 Fonctionnalités

### Tableau
- ✅ Affichage mensuel des données agrégées
- ✅ Filtre par année
- ✅ Édition en ligne (modifie uniquement `WEB_Coor_CH_dech`)

### Graphiques
- ✅ Filtre par année (appliqué à tous les graphiques)
- ✅ Graphique global (tous les déchets solides)
- ✅ 3 graphiques séparés par type de déchet
- ✅ Axe dual (déchets à gauche, CA à droite)
- ✅ Couleurs distinctes pour chaque type
- ✅ Tooltips avec valeurs formatées

## 📝 Notes techniques

### Backend (logic/projet15.py)
- Toutes les fonctions filtrent automatiquement `WHERE Annee >= 2025`
- Les fonctions `get_correlation_par_type()` et `get_types_dechets_disponibles()` filtrent également par unité (kg uniquement)

### Frontend (templates/projet15.html)
- Les 3 graphiques par type sont créés simultanément dans `afficherGraphiqueTousTypes()`
- Chaque graphique utilise un canvas distinct :
  - `chart-papier-offset`
  - `chart-carton-gris`
  - `chart-carton-bois`

### API
- `/api/correlations` - Liste des corrélations (avec filtre année optionnel)
- `/api/statistiques` - Statistiques globales (avec filtre année optionnel)
- `/api/correlation_par_type` - Données par type de déchet (avec filtre année optionnel)
- `/api/types_dechets` - Liste des types disponibles
- `/api/annees` - Liste des années disponibles

## 🚀 Utilisation

1. Accédez à `/projet15/` pour voir la page d'accueil
2. Sélectionnez une section :
   - **Tableau de données** : Pour voir et modifier les données mensuelles
   - **Graphique comparatif** : Pour visualiser les corrélations

3. Utilisez les filtres par année pour affiner votre analyse

## ⚠️ Important

- Les modifications dans l'interface web **n'affectent que** la table `WEB_Coor_CH_dech`
- Les tables sources (`WEB_Suivi_Dechets` et `FACTURES`) **ne sont jamais modifiées**
- Pour recalculer les données de corrélation, exécutez `populate_table_projet15_auto.py`













