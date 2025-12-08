# 📦 Table WEB_GMAO_ARTICLES

## 🎯 Objectif

Table dédiée à l'enregistrement des articles utilisés dans les fiches de réparation du projet 16 (GMAO).

Remplace les anciennes colonnes `DesignArt1`, `DesignArt2`, `DesignArt3` de la table `WEB_GMAO` par une structure flexible permettant un nombre illimité d'articles par fiche.

---

## 📋 Structure de la table

| Colonne | Type | Description | Contraintes |
|---------|------|-------------|-------------|
| `ID` | INT IDENTITY | Identifiant unique de la ligne | PRIMARY KEY, AUTO_INCREMENT |
| `ID_WEB_GMAO` | INT | Référence à la fiche de réparation | NOT NULL, FK → WEB_GMAO.ID |
| `ID_GS_ARTICLES` | INT | Référence à l'article | NULL, FK → GS_ARTICLES.ID |
| `Designation_GS_ARTICLES` | VARCHAR(200) | Copie de la désignation de l'article | NULL, synchronisée automatiquement |
| `Designation_GS_FAMILLES` | VARCHAR(100) | Copie de la désignation de la famille | NULL, synchronisée automatiquement |
| `Designation_GS_TYPES_ARTICLE` | VARCHAR(100) | Copie de la désignation du type | NULL, synchronisée automatiquement |
| `Quantite` | DECIMAL(10,3) | Quantité utilisée | NULL |
| `DateCreation` | DATETIME | Date de création de la ligne | DEFAULT GETDATE() |
| `DateModification` | DATETIME | Date de dernière modification | DEFAULT GETDATE() |

---

## 🔗 Relations entre tables

### Relations principales

```
WEB_GMAO_ARTICLES.ID_WEB_GMAO → WEB_GMAO.ID (ON DELETE CASCADE)
WEB_GMAO_ARTICLES.ID_GS_ARTICLES → GS_ARTICLES.ID (ON DELETE SET NULL)
```

### Liaisons pour récupération des désignations

```
GS_ARTICLES.ID_FAMILLE → GS_FAMILLES.ID
GS_FAMILLES.ID_TYPE_ARTICLE → GS_TYPES_ARTICLE.ID
```

---

## 🔧 Fonctionnalités

### 1. **Multiple articles par fiche**

Une fiche de réparation (`ID_WEB_GMAO`) peut avoir plusieurs articles :

```sql
-- Exemple : Fiche ID 100 avec 3 articles
INSERT INTO WEB_GMAO_ARTICLES (ID_WEB_GMAO, ID_GS_ARTICLES, Quantite)
VALUES 
    (100, 456, 2.5),   -- Article 1
    (100, 789, 1.0),   -- Article 2
    (100, 123, 5.0);   -- Article 3
```

### 2. **Synchronisation automatique des désignations**

Les triggers maintiennent automatiquement les désignations à jour :

- **TR_WEB_GMAO_ARTICLES_SYNC_INSERT** : Synchronise lors de l'insertion
- **TR_WEB_GMAO_ARTICLES_SYNC_UPDATE** : Synchronise lors de la mise à jour
- **TR_GS_ARTICLES_UPDATE_WEB_GMAO_ARTICLES** : Met à jour depuis GS_ARTICLES

```sql
-- Insertion avec synchronisation automatique
INSERT INTO WEB_GMAO_ARTICLES (ID_WEB_GMAO, ID_GS_ARTICLES, Quantite)
VALUES (100, 456, 2.5);

-- Les désignations sont remplies automatiquement par le trigger
```

### 3. **Filtre sur les types d'articles**

Seuls les articles des types 2 et 8 sont autorisés :

```sql
-- Vue des articles autorisés
SELECT * FROM VW_WEB_GMAO_ARTICLES_AUTORISES;
```

### 4. **Suppression en cascade**

Si une fiche de réparation est supprimée, tous ses articles sont supprimés automatiquement :

```sql
DELETE FROM WEB_GMAO WHERE ID = 100;
-- Tous les articles liés dans WEB_GMAO_ARTICLES sont supprimés automatiquement
```

---

## 📊 Exemples d'utilisation

### Insérer des articles pour une fiche

```sql
-- Insérer 2 articles pour la fiche 100
INSERT INTO WEB_GMAO_ARTICLES (ID_WEB_GMAO, ID_GS_ARTICLES, Quantite)
VALUES 
    (100, 456, 2.5),  -- Article 456, quantité 2.5
    (100, 789, 1.0);  -- Article 789, quantité 1.0
```

### Récupérer les articles d'une fiche

```sql
SELECT 
    ID,
    Designation_GS_ARTICLES,
    Designation_GS_FAMILLES,
    Designation_GS_TYPES_ARTICLE,
    Quantite
FROM WEB_GMAO_ARTICLES
WHERE ID_WEB_GMAO = 100
ORDER BY ID;
```

### Récupérer une fiche complète avec ses articles

```sql
SELECT 
    g.ID as ID_Fiche,
    g.PostesReel,
    g.Internvenant,
    a.Designation_GS_ARTICLES,
    a.Quantite
FROM WEB_GMAO g
LEFT JOIN WEB_GMAO_ARTICLES a ON g.ID = a.ID_WEB_GMAO
WHERE g.ID = 100;
```

---

## ✅ Avantages de cette structure

| Avantage | Description |
|----------|-------------|
| **Flexibilité** | Nombre illimité d'articles par fiche (au lieu de 3) |
| **Normalisation** | Meilleure structure de base de données |
| **Historique** | Les désignations sont copiées (protection contre suppressions) |
| **Synchronisation** | Les désignations sont mises à jour automatiquement si modifiées |
| **Performance** | Index sur `ID_WEB_GMAO` et `ID_GS_ARTICLES` |
| **Intégrité** | Contraintes FK et suppression en cascade |

---

## 🔄 Migration depuis l'ancien système

Les anciennes colonnes `DesignArt1/2/3` et `QuantiteArt1/2/3` de `WEB_GMAO` peuvent être migrées vers `WEB_GMAO_ARTICLES` :

```sql
-- Migration des articles existants
INSERT INTO WEB_GMAO_ARTICLES (ID_WEB_GMAO, Designation_GS_ARTICLES, Quantite)
SELECT ID, DesignArt1, QuantiteArt1
FROM WEB_GMAO
WHERE DesignArt1 IS NOT NULL

UNION ALL

SELECT ID, DesignArt2, QuantiteArt2
FROM WEB_GMAO
WHERE DesignArt2 IS NOT NULL

UNION ALL

SELECT ID, DesignArt3, QuantiteArt3
FROM WEB_GMAO
WHERE DesignArt3 IS NOT NULL;
```

---

## 📌 Règles importantes

1. ✅ **Une fiche peut avoir plusieurs articles** (relation 1-N)
2. ✅ **Chaque ligne = 1 article** dans WEB_GMAO_ARTICLES
3. ✅ **Seuls les types 2 et 8** sont autorisés (filtrage côté application)
4. ✅ **Les désignations sont copiées** pour maintenir l'historique
5. ✅ **Synchronisation automatique** via triggers
6. ✅ **Suppression en cascade** si la fiche est supprimée

---

## ✅ Validation

La table a été testée et validée avec succès :
- ✅ Création de la table
- ✅ Insertion d'articles
- ✅ Synchronisation des désignations
- ✅ Suppression en cascade
- ✅ Contraintes de clés étrangères

La table est prête à être intégrée dans le projet 16 ! 🎉




