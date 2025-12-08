# 📋 Table WEB_GMAO_REPARATION

## 🎯 Objectif

Créer une table dédiée aux informations de réparation, séparant les données de réparation des demandes d'intervention dans la table `WEB_GMAO`.

## 🗄️ Structure de la Table

| Colonne | Type | Description | Contraintes |
|---------|------|-------------|-------------|
| `ID` | INT IDENTITY | Identifiant unique | PRIMARY KEY, AUTO_INCREMENT |
| `DteDeb` | DATETIME | Date/heure de début de la réparation | NULL |
| `DteFin` | DATETIME | Date/heure de fin de la réparation | NULL |
| `TpsReel` | FLOAT (COMPUTED) | Temps réel calculé | Colonne calculée persistée : `(DteFin - DteDeb) / 60.0` |
| `Nat` | VARCHAR(4) | Nature de la réparation | NULL, CHECK IN ('Mec', 'Elec') |
| `ID_StatRep` | INT | Statut de la réparation | NULL, FK → WEB_GMAO_StatRep.ID |
| `MatInter` | INT | Matricule de l'intervenant | NULL, FK → personel.Matricule |
| `Intervenant` | NVARCHAR(101) | Nom et prénom de l'intervenant | NULL |
| `ID_WEB_GMAO_Dem_In` | INT | Lien vers la demande d'intervention | NULL, FK → WEB_GMAO.ID |
| `PostesReel` | VARCHAR(50) | Machine concernée | NULL |
| `DateCreation` | DATETIME | Date de création | DEFAULT GETDATE() |
| `DateModification` | DATETIME | Date de modification | DEFAULT GETDATE() |

## 🔗 Relations

- `ID_WEB_GMAO_Dem_In` → `WEB_GMAO.ID` (ON DELETE SET NULL)
- `ID_StatRep` → `WEB_GMAO_StatRep.ID`
- `MatInter` → `personel.Matricule`

## 📌 Règles Fonctionnelles

### 1. **PostesReel**
- Si `ID_WEB_GMAO_Dem_In` est renseigné : copier la valeur de `PostesReel` depuis `WEB_GMAO`
- Sinon : utiliser la valeur saisie dans la fiche de réparation

### 2. **Réparations liées à une demande**
- Lorsqu'une réparation est créée pour une demande d'intervention existante :
  - `ID_WEB_GMAO_Dem_In` = ID de la demande dans `WEB_GMAO`
  - `PostesReel` est copié depuis `WEB_GMAO.PostesReel`

### 3. **Réparations directes**
- Lorsqu'une réparation est créée sans demande d'intervention :
  - `ID_WEB_GMAO_Dem_In` = NULL
  - `PostesReel` = valeur saisie dans le formulaire
  - Un enregistrement minimal est créé dans `WEB_GMAO` avec `Code = 'R'` pour lier les articles

## 🚀 Installation

### Option 1 : Script SQL
```sql
-- Exécuter dans SQL Server Management Studio
-- Fichier: create_web_gmao_reparation.sql
```

### Option 2 : Script Python
```bash
python setup_web_gmao_reparation.py
```

## 🔄 Migration des Données

Les données existantes dans `WEB_GMAO` (colonnes `DteDeb`, `DteFin`, `TpsReel`, `Nat`, `ID_StatRep`, `MatInter`, `Intervenant`) sont automatiquement migrées vers `WEB_GMAO_REPARATION` lors de la création de la table.

## ⚠️ Important

Après la création de la table et la migration :
- Les nouvelles réparations sont créées dans `WEB_GMAO_REPARATION`
- Les colonnes de réparation dans `WEB_GMAO` deviennent obsolètes mais restent pour compatibilité
- Le code Python a été modifié pour utiliser `WEB_GMAO_REPARATION` en priorité

## 📝 Fonctions Python Modifiées

- ✅ `update_reparation()` - Utilise `WEB_GMAO_REPARATION`
- ✅ `create_reparation_direct()` - Crée dans `WEB_GMAO_REPARATION` avec `ID_WEB_GMAO_Dem_In = NULL`
- ✅ `update_reparation_status()` - Met à jour dans `WEB_GMAO_REPARATION`
- ✅ `get_demande_by_id()` - Joint avec `WEB_GMAO_REPARATION` pour récupérer les données
- ✅ `get_all_demandes()` - Joint avec `WEB_GMAO_REPARATION` pour afficher les réparations
- ✅ `delete_reparation()` - Supprime depuis `WEB_GMAO_REPARATION`

