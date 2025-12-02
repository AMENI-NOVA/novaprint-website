# 📋 Projet 16 - GMAO (Gestion de la Maintenance Assistée par Ordinateur)

## 🎯 Objectif

Créer un système de gestion de la maintenance assistée par ordinateur permettant de suivre les interventions préventives et correctives avec synchronisation automatique des données depuis les tables sources.

## 🗄️ Structure de la Base de Données

### Table : `WEB_GMAO`

#### Colonnes Natives

| Colonne | Type | Description | Contraintes |
|---------|------|-------------|-------------|
| `ID` | INT IDENTITY | Identifiant unique | PRIMARY KEY, AUTO_INCREMENT |
| `Code` | CHAR(1) | Type d'intervention | NOT NULL, CHECK IN ('P', 'C') |
| `DteDeb` | DATETIME | Date de début | NULL |
| `DteFin` | DATETIME | Date de fin | NULL |
| `TpsReel` | COMPUTED | Temps réel calculé | DATEDIFF(MINUTE, DteDeb, DteFin) |
| `PostesReel` | VARCHAR(50) | Nom du poste (lecture seule) | NULL |
| `OperRec` | NVARCHAR(101) | Nom + Prénom opérateur réclamant | NULL |
| `MatrOpRec` | INT | Matricule opérateur réclamant | FK vers personel.Matricule |
| `DteRec` | DATETIME | Date de réclamation | NULL |
| `Reclamation` | NTEXT | Texte de la réclamation | NULL |
| `Internvenant` | NVARCHAR(101) | Nom + Prénom intervenant | NULL |
| `MatInter` | INT | Matricule intervenant | FK vers personel.Matricule |
| `Nat` | VARCHAR(4) | Nature intervention | CHECK IN ('Mec', 'Elec') |

#### Blocs d'Articles (3 blocs identiques)

| Colonne | Type | Description | Contraintes |
|---------|------|-------------|-------------|
| `DesignArtX` | VARCHAR(200) | Désignation article (lecture seule) | NULL |
| `DesignArtX_FK` | INT | FK vers GS_ARTICLES.ID | FK, familles 2 et 8 uniquement |
| `QuantiteArtX` | DECIMAL(10,3) | Quantité utilisée | NULL |

*Où X = 1, 2, 3*

#### Métadonnées

| Colonne | Type | Description | Contraintes |
|---------|------|-------------|-------------|
| `DateCreation` | DATETIME | Date de création | DEFAULT GETDATE() |
| `DateModification` | DATETIME | Date de modification | DEFAULT GETDATE() |

## 🔗 Relations et Clés Étrangères

### Clés Étrangères Principales
- `PostesReel_FK` → `GP_POSTES.ID`
- `MatrOpRec` → `personel.Matricule`
- `MatInter` → `personel.Matricule`
- `DesignArt1_FK` → `GS_ARTICLES.ID`
- `DesignArt2_FK` → `GS_ARTICLES.ID`
- `DesignArt3_FK` → `GS_ARTICLES.ID`

### Contraintes de Validation
- **Code** : Doit être 'P' (Préventif) ou 'C' (Correctif)
- **Nat** : Doit être 'Mec' (Mécanique) ou 'Elec' (Électrique)
- **Dates** : DteFin >= DteDeb si les deux sont renseignées
- **Articles** : Doivent appartenir aux familles dont `GS_TYPES_ARTICLE.ID ∈ (2, 8)`

## 🔄 Synchronisation Automatique

### Approche Choisie : **TRIGGERS**

Les triggers ont été choisis pour leur capacité à maintenir la cohérence en temps réel et leur simplicité d'implémentation.

#### Triggers de Synchronisation (INSERT/UPDATE)
1. **TR_WEB_GMAO_SYNC_POSTES** : Synchronise les noms de postes
2. **TR_WEB_GMAO_SYNC_OPREC** : Synchronise les noms des opérateurs réclamants
3. **TR_WEB_GMAO_SYNC_EXEC** : Synchronise les noms des exécuteurs
4. **TR_WEB_GMAO_SYNC_ARTICLES** : Synchronise les désignations d'articles

#### Triggers de Mise à Jour Inverse
5. **TR_GP_POSTES_UPDATE_WEB_GMAO** : Mise à jour depuis GP_POSTES
6. **TR_PERSONEL_UPDATE_WEB_GMAO** : Mise à jour depuis personel
7. **TR_GS_ARTICLES_UPDATE_WEB_GMAO** : Mise à jour depuis GS_ARTICLES

#### Triggers de Gestion des Suppressions
8. **TR_GP_POSTES_DELETE_WEB_GMAO** : Gestion des suppressions de postes
9. **TR_PERSONEL_DELETE_WEB_GMAO** : Gestion des suppressions de personnel
10. **TR_GS_ARTICLES_DELETE_WEB_GMAO** : Gestion des suppressions d'articles

## 📊 Vues Utilitaires

### `VW_WEB_GMAO_ARTICLES_AUTORISES`
Liste tous les articles autorisés (familles de type 2 et 8) avec leurs informations complètes.

### `VW_WEB_GMAO_COMPLET`
Vue complète des données GMAO avec libellés explicites et calculs automatiques.

## 🛠️ Procédures Stockées

### `SP_WEB_GMAO_INSERT`
Procédure pour insérer une nouvelle intervention GMAO avec tous les paramètres nécessaires.

## 🎨 Fonctionnalités Avancées

### 1. Colonne Calculée
- **TpsReel** : Calcul automatique du temps réel en minutes (DteFin - DteDeb)
- Conversion en heures disponible dans la vue `VW_WEB_GMAO_COMPLET`

### 2. Validation des Articles
- Vérification automatique que les articles sélectionnés appartiennent aux bonnes familles
- Erreur explicite si un article non autorisé est sélectionné

### 3. Gestion des Données Orphelines
- Mise à NULL automatique des références lors de suppressions dans les tables sources
- Préservation de l'intégrité des données

### 4. Optimisation des Performances
- Index sur les dates pour les recherches temporelles
- Index sur les codes et nature pour les filtres
- Index sur les matricules pour les recherches par personnel
- Index sur les FK des articles pour les jointures

## 📈 Avantages de Cette Architecture

### 1. **Cohérence des Données**
- ✅ Synchronisation automatique en temps réel
- ✅ Pas de données obsolètes
- ✅ Intégrité référentielle maintenue

### 2. **Performance**
- ✅ Index optimisés pour les requêtes fréquentes
- ✅ Colonnes calculées pour éviter les calculs répétitifs
- ✅ Vues pré-construites pour l'affichage

### 3. **Sécurité**
- ✅ Colonnes synchronisées en lecture seule
- ✅ Validation stricte des contraintes
- ✅ Gestion des erreurs explicites

### 4. **Maintenabilité**
- ✅ Structure claire et documentée
- ✅ Triggers bien organisés
- ✅ Procédures stockées réutilisables

## 🚀 Utilisation

### Insertion d'une Intervention
```sql
EXEC SP_WEB_GMAO_INSERT 
    @Code = 'P',
    @DteDeb = '2024-01-15 08:00:00',
    @DteFin = '2024-01-15 10:30:00',
    @PostesReel_FK = 1,
    @MatrOpRec = 123,
    @DteRec = '2024-01-15 07:45:00',
    @Reclamation = 'Maintenance préventive mensuelle',
    @MatInter = 456,
    @Nat = 'Mec',
    @DesignArt1_FK = 789,
    @QuantiteArt1 = 2.5
```

### Consultation des Données
```sql
-- Vue complète avec libellés
SELECT * FROM VW_WEB_GMAO_COMPLET
WHERE Code = 'P' AND Nat = 'Mec'

-- Articles autorisés
SELECT * FROM VW_WEB_GMAO_ARTICLES_AUTORISES
ORDER BY Designation
```

## 📋 Codes de Référence

### Codes d'Intervention
- **P** : Préventif
- **C** : Correctif

### Nature d'Intervention
- **Mec** : Mécanique
- **Elec** : Électrique

### Familles d'Articles Autorisées
- **Type 2** : [Description selon GS_TYPES_ARTICLE]
- **Type 8** : [Description selon GS_TYPES_ARTICLE]
