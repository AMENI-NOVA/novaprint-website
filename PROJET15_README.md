# 📊 Projet 15 : Analyse de la Corrélation Déchets / Chiffre d'Affaires

## Vue d'ensemble

Le Projet 15 permet d'analyser la corrélation entre la quantité de déchets solides produits et le chiffre d'affaires mensuel de l'entreprise.

---

## 🎯 Objectifs

1. **Agréger les données mensuelles** de déchets et de chiffre d'affaires
2. **Visualiser la corrélation** entre les deux indicateurs
3. **Permettre l'édition** des données agrégées sans affecter les tables sources
4. **Identifier les tendances** et relations entre production de déchets et activité commerciale

---

## 🗄️ Structure de la Base de Données

### Table : `WEB_Coor_CH_dech`

| Champ | Type | Description |
|-------|------|-------------|
| `ID` | INT (PK) | Identifiant unique auto-incrémenté |
| `Annee` | INT | Année |
| `Mois` | INT | Mois (1-12) |
| `Date_WEB_Suivi_Dechets` | DATE | Date de référence (1er du mois) |
| `Quantite_WEB_Suivi_Dechets` | DECIMAL(18,2) | Total des déchets solides (kg) pour le mois |
| `Unite_WEB_Suivi_Dechets` | NVARCHAR(20) | Unité (toujours 'kg') |
| `DteFact_FACTURES` | DATE | Date de référence factures (1er du mois) |
| `TotalHTPce_FACTURES` | DECIMAL(18,2) | Total CA HT pour le mois |
| `Date_Creation` | DATETIME | Date de création de l'enregistrement |
| `Date_Modification` | DATETIME | Date de dernière modification |

**Contrainte unique** : `(Annee, Mois)` pour éviter les doublons

---

## 📁 Fichiers du Projet

### Backend

- **`logic/projet15.py`** : Logique métier
  - `get_all_correlations(annee)` : Récupère toutes les données
  - `get_correlation_by_id(id)` : Récupère une ligne spécifique
  - `update_correlation(id, data)` : Met à jour une ligne
  - `get_statistiques_correlation(annee)` : Calcule les statistiques
  - `get_annees_disponibles()` : Liste des années

- **`routes/projet15_routes.py`** : Routes Flask
  - `/projet15/` : Page principale
  - `/projet15/tableau` : Section tableau de données
  - `/projet15/graphique` : Section graphique comparatif
  - `/projet15/api/correlations` : API pour récupérer les données
  - `/projet15/api/correlation/<id>/update` : API pour mettre à jour
  - `/projet15/api/statistiques` : API pour les statistiques
  - `/projet15/api/annees` : API pour les années disponibles

### Frontend

- **`templates/projet15.html`** : Template principal
  - Section tableau de données éditable
  - Section graphique comparatif (Chart.js)
  - Filtre par année
  - Cartes statistiques

### Scripts utilitaires

- **`populate_table_projet15_auto.py`** : Population automatique des données
  - Agrège les données de `WEB_Suivi_Dechets` et `FACTURES`
  - Ne prend que les déchets solides (kg)
  - Crée une ligne par mois avec les totaux agrégés

---

## 🚀 Fonctionnalités

### 1. Tableau de Données

- ✅ Affichage mensuel des données agrégées
- ✅ Filtre par année
- ✅ **Édition en ligne** des valeurs
  - Quantité de déchets (kg)
  - Chiffre d'affaires HT (€)
- ✅ Modifications sauvegardées **uniquement dans `WEB_Coor_CH_dech`**
- ✅ Aucun impact sur les tables sources (`WEB_Suivi_Dechets`, `FACTURES`)

### 2. Graphique Comparatif

- 📈 **Graphique double axe** (Chart.js)
  - Axe gauche (vert) : Déchets solides (kg)
  - Axe droit (bleu) : Chiffre d'affaires HT (€)
- 📊 **Cartes statistiques**
  - Nombre de mois analysés
  - Total déchets solides
  - Total CA HT
  - Moyenne déchets/mois
- 🔍 Filtre par année
- 💡 Visualisation claire de la corrélation

---

## 💾 Population des Données

### Première population

```bash
python populate_table_projet15_auto.py
```

Ce script :
1. Vérifie l'existence de la table
2. Vide la table si elle contient des données
3. Agrège les données mensuelles :
   - **Déchets** : Somme des quantités en kg par mois depuis `WEB_Suivi_Dechets`
   - **CA** : Somme des `TotalHTPce` par mois depuis `FACTURES`
4. Insère les données agrégées
5. Affiche les statistiques globales

### Résultat de la population initiale

```
[SUCCESS] 114 enregistrement(s) insere(s) !

[STATS] Statistiques globales :
   Periode : 2011 - 2025
   Nombre de mois : 114
   Total dechets : 304470.00 kg
   Total CA HT : 67389352.17 euros
```

---

## 🔒 Principe d'Isolation des Données

### ⚠️ IMPORTANT : Protection des tables sources

Toutes les **modifications effectuées via l'interface web** du Projet 15 sont enregistrées **UNIQUEMENT** dans la table `WEB_Coor_CH_dech`.

**Aucune modification ne peut affecter** :
- ❌ La table `WEB_Suivi_Dechets` (source des déchets)
- ❌ La table `FACTURES` (source du CA)

### Traçabilité

Chaque champ de `WEB_Coor_CH_dech` est nommé avec le suffixe de sa table source :
- `Quantite_WEB_Suivi_Dechets` → Provient de `WEB_Suivi_Dechets`
- `TotalHTPce_FACTURES` → Provient de `FACTURES`

Cette nomenclature permet de toujours identifier l'origine des données.

---

## 🌐 Accès à l'Interface Web

### Pages principales

- **Page d'accueil** : http://localhost:5000/projet15/graphique
- **Tableau de données** : http://localhost:5000/projet15/tableau
- **Graphique comparatif** : http://localhost:5000/projet15/graphique

### Navigation

Le Projet 15 est accessible depuis :
- 🏠 Page d'accueil : "📊 Projet 15 – Corrélation Déchets/CA"
- 📋 Navbar : "📊 Corrélation"

---

## 📈 Interprétation des Résultats

### Corrélation positive

Si les deux courbes évoluent dans le même sens :
- ↗️ Augmentation des déchets + Augmentation du CA
- 💡 **Interprétation** : Plus l'activité est forte, plus la production de déchets augmente

### Corrélation négative

Si les courbes évoluent en sens inverse :
- ↗️ Augmentation des déchets + Diminution du CA
- 💡 **Interprétation** : Possibles inefficacités de production

### Pas de corrélation

Si les courbes sont indépendantes :
- 💡 **Interprétation** : Les déchets ne sont pas directement liés au volume d'activité

---

## 🔄 Mise à Jour des Données

### Régénérer l'agrégation

Pour mettre à jour les données agrégées avec les dernières valeurs des tables sources :

```bash
python populate_table_projet15_auto.py
```

**⚠️ Attention** : Cette opération :
- Vide la table `WEB_Coor_CH_dech`
- **Supprime toutes les modifications manuelles**
- Réimporte les données fraîches depuis les sources

### Fréquence recommandée

- 📅 **Mensuelle** : Pour avoir les données du mois écoulé
- 📊 **Trimestrielle** : Pour les analyses de tendances

---

## 🛠️ Maintenance

### Contrôle qualité des données

Le script vérifie automatiquement :
- ✅ Existence de la table
- ✅ Cohérence des dates
- ✅ Conversion correcte des unités (kg uniquement)

### Logs et erreurs

Les erreurs sont affichées avec le préfixe `[ERREUR]` et incluent :
- Le message d'erreur
- Le stack trace complet

---

## 📊 Statistiques Disponibles

### Par mois

- Quantité de déchets solides (kg)
- Chiffre d'affaires HT (€)

### Globales (par période)

- Nombre total de mois
- Total des déchets solides
- Total du CA HT
- Moyenne des déchets par mois
- Moyenne du CA par mois
- Période couverte (année min - année max)

---

## 🎨 Design et UX

- **Couleurs** : Bleu pour le CA, Vert pour les déchets
- **Graphique responsive** : S'adapte à la taille de l'écran
- **Édition intuitive** : Clic sur une cellule pour éditer
- **Feedback immédiat** : Alertes de succès/erreur
- **Navigation fluide** : Boutons de section clairs

---

## 📝 Notes Techniques

### Agrégation SQL

L'agrégation utilise un `FULL OUTER JOIN` pour garantir :
- Tous les mois avec des déchets sont inclus
- Tous les mois avec du CA sont inclus
- Les mois sans déchets ou sans CA affichent 0

### Performance

- Requêtes optimisées avec `GROUP BY` et agrégations
- Index sur `(Annee, Mois)` pour des recherches rapides
- Pagination potentielle pour de grandes périodes

---

## 🔐 Sécurité

- ✅ Validation des données côté serveur
- ✅ Transactions SQL pour l'intégrité des données
- ✅ Gestion des erreurs avec rollback automatique
- ✅ Aucune injection SQL (paramètres bindés)

---

## ✅ Projet Terminé !

Le Projet 15 est maintenant **opérationnel** et prêt à être utilisé pour analyser la corrélation entre les déchets et le chiffre d'affaires ! 🎉

**Bon analyse ! 📊📈**













