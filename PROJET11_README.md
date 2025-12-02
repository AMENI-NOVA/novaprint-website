# Projet 11 – Gestion des Traitements (WEB_TRAITEMENTS)

## Vue d'ensemble

Le Projet 11 est un système de gestion des traitements de production qui consolide automatiquement les données provenant de plusieurs tables sources et permet l'ajout de données spécifiques via une interface web.

## Objectifs

1. **Centralisation des données** : Regrouper les informations de plusieurs tables sources en une seule table `WEB_TRAITEMENTS`
2. **Saisie web** : Permettre l'ajout de données spécifiques (dates, nombre d'opérations, personnel)
3. **Intégrité référentielle** : Maintenir les liens avec les tables sources via des clés étrangères
4. **Mise à jour automatique** : Les modifications dans les tables sources sont reflétées automatiquement
5. **Analyse et statistiques** : Fournir des statistiques sur les traitements par service et opérateur

## Structure de la Base de Données

### Table WEB_TRAITEMENTS

#### Champs Principaux

- **ID** (INT, IDENTITY, PRIMARY KEY) : Identifiant unique du traitement
- **DteDeb** (DATETIME) : Date de début du traitement
- **DteFin** (DATETIME) : Date de fin du traitement (NULL si en cours)
- **NbOp** (INT) : Nombre d'opérations réalisées
- **NbPers** (INT) : Nombre de personnes affectées
- **ID_FICHE_TRAVAIL** (INT, NOT NULL) : Clé de liaison principale

#### Champs Importés avec Suffixes

Les champs importés conservent leur nom d'origine avec le suffixe de la table source :

**De COMMANDES :**
- ID_COMMANDES
- ID_SOCIETE_COMMANDES
- Numero_COMMANDES
- Reference_COMMANDES
- QteComm_COMMANDES

**De SOCIETES :**
- ID_SOCIETES
- RaiSocTri_SOCIETES

**De personel :**
- Matricule_personel
- Nom_personel
- Prenom_personel

**De GP_SERVICES :**
- ID_GP_SERVICES
- Nom_GP_SERVICES

**De GP_POSTES :**
- ID_GP_POSTES
- Nom_GP_POSTES
- ID_SERVICE_GP_POSTES

**De GP_FICHES_TRAVAIL :**
- ID_GP_FICHES_TRAVAIL
- ID_COMMANDE_GP_FICHES_TRAVAIL
- ID_POSTE_GP_FICHES_TRAVAIL

**De GP_FICHES_OPERATIONS :**
- ID_OPERATION_GP_FICHES_OPERATIONS
- OpPrevDev_GP_FICHES_OPERATIONS
- TpsPrevDev_GP_FICHES_OPERATIONS

**De GP_TRAITEMENTS :**
- ID_GP_TRAITEMENTS

#### Métadonnées

- **DateCreation** (DATETIME, DEFAULT GETDATE())
- **DateModification** (DATETIME, DEFAULT GETDATE())

### Clés Étrangères

La table maintient l'intégrité référentielle avec les tables sources :

- `FK_WEB_TRAITEMENTS_GP_FICHES_TRAVAIL` → GP_FICHES_TRAVAIL(ID)
- `FK_WEB_TRAITEMENTS_COMMANDES` → COMMANDES(ID)
- `FK_WEB_TRAITEMENTS_SOCIETES` → SOCIETES(ID)
- `FK_WEB_TRAITEMENTS_personel` → personel(Matricule)
- `FK_WEB_TRAITEMENTS_GP_SERVICES` → GP_SERVICES(ID)
- `FK_WEB_TRAITEMENTS_GP_POSTES` → GP_POSTES(ID)
- `FK_WEB_TRAITEMENTS_GP_TRAITEMENTS` → GP_TRAITEMENTS(ID)

### Index

Plusieurs index optimisent les performances :

- `IDX_WEB_TRAITEMENTS_ID_FICHE_TRAVAIL` : Sur ID_FICHE_TRAVAIL
- `IDX_WEB_TRAITEMENTS_NUMERO_COMMANDES` : Sur Numero_COMMANDES
- `IDX_WEB_TRAITEMENTS_DATES` : Sur (DteDeb, DteFin)

## Fonctionnalités

### 1. Créer un Nouveau Traitement

**URL** : `/projet11/nouveau`

**Processus** :
1. Sélectionner une fiche de travail disponible
2. Les informations de la commande s'affichent automatiquement
3. Saisir les données spécifiques :
   - Date de début (obligatoire)
   - Date de fin (optionnel)
   - Nombre d'opérations
   - Nombre de personnes
   - Opérateur (optionnel)
4. Enregistrer le traitement

**Données automatiques** :
- Toutes les informations des tables sources sont récupérées automatiquement
- Les champs sont remplis par jointure avec les tables d'origine

### 2. Liste des Traitements

**URL** : `/projet11/traitements`

**Fonctionnalités** :
- Affichage de tous les traitements avec pagination
- Filtrage et recherche (via DataTables)
- Actions : Voir détails, Modifier, Supprimer
- Indicateur de statut (En cours / Terminé)

### 3. Statistiques

**URL** : `/projet11/statistiques`

**Indicateurs disponibles** :
- Total des traitements
- Traitements terminés vs en cours
- Total et moyenne d'opérations
- Moyenne de personnes par traitement

**Analyses** :
- **Par Service** : Nombre de traitements, total et moyenne d'opérations
- **Par Opérateur** : Nombre de traitements et total d'opérations

**Visualisations** :
- Graphique circulaire : Répartition par service
- Graphique à barres : Top 10 des opérateurs

## API REST

### Endpoints

#### GET `/projet11/api/traitements`
Récupère la liste de tous les traitements

**Réponse** :
```json
[
  {
    "id": 1,
    "dte_deb": "2024-10-15 08:00:00",
    "dte_fin": "2024-10-15 17:00:00",
    "nb_op": 150,
    "nb_pers": 3,
    "numero_commande": "CMD001",
    "client": "Client ABC",
    ...
  }
]
```

#### GET `/projet11/api/traitements/{id}`
Récupère un traitement spécifique

#### POST `/projet11/api/traitements`
Crée un nouveau traitement

**Données requises** :
```json
{
  "id_fiche_travail": 123,
  "dte_deb": "2024-10-15T08:00",
  "dte_fin": "2024-10-15T17:00",
  "nb_op": 150,
  "nb_pers": 3,
  "matricule_personel": 456
}
```

#### PUT `/projet11/api/traitements/{id}`
Met à jour un traitement existant

**Champs modifiables** :
- dte_deb
- dte_fin
- nb_op
- nb_pers

#### DELETE `/projet11/api/traitements/{id}`
Supprime un traitement

#### GET `/projet11/api/fiches-disponibles`
Récupère les fiches de travail disponibles (non encore traitées)

#### GET `/projet11/api/operateurs`
Récupère la liste des opérateurs

#### GET `/projet11/api/statistiques`
Récupère toutes les statistiques

## Fichiers du Projet

### Scripts SQL

- **`create_web_traitements.sql`** : Script de création de la table avec toutes les clés étrangères et index

### Scripts Python

- **`create_table_projet11.py`** : Exécute le script SQL pour créer la table
- **`inspect_tables_projet11.py`** : Inspecte la structure des tables sources

### Modules Python

- **`logic/projet11.py`** : Logique métier et fonctions CRUD
- **`routes/projet11_routes.py`** : Routes Flask et API REST

### Templates HTML

- **`templates/projet11.html`** : Page d'accueil du projet
- **`templates/projet11_liste.html`** : Liste des traitements
- **`templates/projet11_nouveau.html`** : Formulaire de création
- **`templates/projet11_stats.html`** : Page de statistiques

## Installation et Configuration

### 1. Créer la table

```bash
python create_table_projet11.py
```

### 2. Vérifier la structure

Le script affichera :
- La structure complète de la table
- Les clés étrangères créées
- Les index

### 3. Lancer l'application

```bash
python app.py
```

### 4. Accéder au projet

Ouvrir un navigateur et aller à : `http://localhost:5000/projet11`

## Principes de Conception

### 1. Pas de Duplication de Champs Identiques

Les champs qui existent dans plusieurs tables (comme `ID_FICHE_TRAVAIL`) ne sont **pas dupliqués**. Un seul champ `ID_FICHE_TRAVAIL` sert de clé de liaison principale.

### 2. Suffixes pour Éviter les Conflits

Tous les champs importés portent le suffixe de leur table source :
- Évite les conflits de noms
- Facilite l'identification de l'origine des données
- Améliore la lisibilité

**Exemple** :
- `Numero` de COMMANDES devient `Numero_COMMANDES`
- `Nom` de GP_SERVICES devient `Nom_GP_SERVICES`

### 3. Données en Lecture Seule

Les champs importés des tables sources sont remplis **automatiquement** lors de la création et ne peuvent pas être modifiés manuellement. Seuls les champs spécifiques au web (DteDeb, DteFin, NbOp, NbPers) peuvent être modifiés.

### 4. Mise à Jour Automatique

Grâce aux clés étrangères, si une donnée change dans une table source (par exemple, le nom d'un client dans SOCIETES), la modification est automatiquement reflétée dans WEB_TRAITEMENTS via les jointures SQL.

## Bonnes Pratiques

### Création d'un Traitement

1. **Vérifier la fiche** : S'assurer que la fiche de travail sélectionnée est correcte
2. **Date de début** : Toujours renseigner la date de début
3. **Date de fin** : Ne remplir que si le traitement est terminé
4. **Nombre d'opérations** : Utiliser trois chiffres après la virgule [[memory:4553069]]
5. **Opérateur** : Sélectionner l'opérateur principal

### Modification

- Seules les données web peuvent être modifiées (dates, nombres)
- Les données sources restent en lecture seule
- Utiliser la date de fin pour marquer un traitement comme terminé

### Suppression

- Vérifier qu'aucune autre opération ne dépend du traitement
- La suppression est définitive

## Statistiques et Analyses

### Indicateurs Clés

1. **Volume** : Nombre total de traitements
2. **Statut** : Répartition terminés / en cours
3. **Productivité** : Moyenne d'opérations par traitement
4. **Ressources** : Moyenne de personnes par traitement

### Analyses Disponibles

1. **Par Service** : Identification des services les plus actifs
2. **Par Opérateur** : Suivi de la charge de travail individuelle
3. **Évolution** : Tendances dans le temps (via dates de création)

## Maintenance

### Backup

Sauvegarder régulièrement la table WEB_TRAITEMENTS :

```sql
SELECT * INTO WEB_TRAITEMENTS_BACKUP FROM WEB_TRAITEMENTS
```

### Optimisation

Reconstruire les index périodiquement :

```sql
ALTER INDEX ALL ON WEB_TRAITEMENTS REBUILD
```

### Nettoyage

Archiver les traitements anciens si nécessaire :

```sql
-- Exemple : archiver les traitements de plus de 2 ans
SELECT * INTO WEB_TRAITEMENTS_ARCHIVE 
FROM WEB_TRAITEMENTS 
WHERE DateCreation < DATEADD(YEAR, -2, GETDATE())
```

## Dépannage

### Problème : Fiche de travail non disponible

**Cause** : La fiche a déjà un traitement enregistré

**Solution** : Vérifier dans la liste des traitements ou créer une nouvelle fiche

### Problème : Erreur de clé étrangère

**Cause** : Donnée référencée n'existe pas dans la table source

**Solution** : Vérifier l'intégrité des données sources

### Problème : Dates incorrectes

**Cause** : Format de date non compatible

**Solution** : Utiliser le format YYYY-MM-DD HH:MM

## Technologies Utilisées

- **Base de données** : SQL Server
- **Backend** : Python 3, Flask, pyodbc
- **Frontend** : HTML5, CSS3, JavaScript, Bootstrap 5
- **Visualisation** : Chart.js
- **Tableaux** : DataTables

## Auteur

Projet développé pour Novaprint

## Version

Version 1.0 - Octobre 2024


