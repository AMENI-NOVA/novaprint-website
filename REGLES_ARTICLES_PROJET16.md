# 📋 Règles de Gestion des Articles - Projet 16

## 🎯 Principe Fondamental

Les tables sources (`GS_ARTICLES`, `GS_FAMILLES`, `GS_TYPES_ARTICLE`) sont en **LECTURE SEULE** depuis la page web.

Toutes les opérations d'enregistrement d'articles utilisés se font **UNIQUEMENT dans `WEB_GMAO_ARTICLES`**.

---

## ✅ Tables en LECTURE SEULE (Consultation uniquement)

Ces tables ne doivent **JAMAIS** être modifiées depuis la page web :

| Table | Utilisation |
|-------|-------------|
| `GS_ARTICLES` | Source pour la recherche d'articles (Select2) |
| `GS_FAMILLES` | Source pour afficher la famille d'un article |
| `GS_TYPES_ARTICLE` | Source pour filtrer les types 2 et 8 |

### Utilisation côté web :
```sql
-- ✅ AUTORISÉ : SELECT pour affichage
SELECT a.ID, a.Designation, f.Designation as Famille
FROM GS_ARTICLES a
INNER JOIN GS_FAMILLES f ON a.ID_FAMILLE = f.ID
WHERE ...

-- ❌ INTERDIT : INSERT, UPDATE, DELETE
-- Ces opérations ne doivent JAMAIS être exécutées depuis le projet 16
```

---

## 📝 Table d'ÉCRITURE (Enregistrement des utilisations)

### `WEB_GMAO_ARTICLES` : Table de travail du projet 16

Toutes les opérations se font dans cette table :

#### ✅ Ajout d'articles utilisés

```sql
INSERT INTO WEB_GMAO_ARTICLES (
    ID_WEB_GMAO,      -- ID de la fiche de réparation
    ID_GS_ARTICLES,   -- Référence à l'article source
    Quantite          -- Quantité utilisée
) VALUES (100, 456, 2.5);

-- Les désignations sont remplies AUTOMATIQUEMENT par le trigger
```

#### ✅ Modification de quantité

```sql
UPDATE WEB_GMAO_ARTICLES
SET Quantite = 5.0
WHERE ID = 123;
```

#### ✅ Suppression d'un article d'une fiche

```sql
DELETE FROM WEB_GMAO_ARTICLES
WHERE ID = 123;
```

---

## 🔄 Synchronisation Automatique

### Principe : Les triggers maintiennent la cohérence

**Scénario 1 : Insertion d'un article dans une fiche**
```sql
-- L'utilisateur insère uniquement l'ID de l'article
INSERT INTO WEB_GMAO_ARTICLES (ID_WEB_GMAO, ID_GS_ARTICLES, Quantite)
VALUES (100, 456, 2.5);

-- Le trigger TR_WEB_GMAO_ARTICLES_SYNC_INSERT remplit automatiquement :
-- - Designation_GS_ARTICLES
-- - Designation_GS_FAMILLES
-- - Designation_GS_TYPES_ARTICLE
```

**Scénario 2 : Mise à jour dans GS_ARTICLES**
```sql
-- Un administrateur modifie la désignation dans GS_ARTICLES
UPDATE GS_ARTICLES SET Designation = 'NOUVEAU NOM' WHERE ID = 456;

-- Le trigger TR_GS_ARTICLES_UPDATE_WEB_GMAO_ARTICLES met à jour automatiquement :
UPDATE WEB_GMAO_ARTICLES
SET Designation_GS_ARTICLES = 'NOUVEAU NOM'
WHERE ID_GS_ARTICLES = 456;

-- La page web affichera automatiquement le nouveau nom au prochain chargement
```

**Scénario 3 : Suppression dans GS_ARTICLES**
```sql
-- Un article est supprimé de GS_ARTICLES
DELETE FROM GS_ARTICLES WHERE ID = 456;

-- Grâce à ON DELETE SET NULL :
-- - ID_GS_ARTICLES devient NULL
-- - Les désignations copiées restent intactes (historique préservé)
```

---

## 🎨 Implémentation dans la page web

### Backend (Python)

```python
# ✅ LECTURE depuis tables sources
def search_articles(query=""):
    """Recherche dans GS_ARTICLES (lecture seule)"""
    cursor.execute("""
        SELECT a.ID, a.Designation
        FROM GS_ARTICLES a
        INNER JOIN GS_FAMILLES f ON a.ID_FAMILLE = f.ID
        INNER JOIN GS_TYPES_ARTICLE t ON f.ID_TYPE_ARTICLE = t.ID
        WHERE t.ID IN (2, 8)  -- Filtre sur types autorisés
        AND a.Designation LIKE ?
    """, (f'%{query}%',))

# ✅ ÉCRITURE dans WEB_GMAO_ARTICLES
def add_article_to_reparation(id_web_gmao, id_article, quantite):
    """Enregistre un article utilisé"""
    cursor.execute("""
        INSERT INTO WEB_GMAO_ARTICLES (
            ID_WEB_GMAO, ID_GS_ARTICLES, Quantite
        ) VALUES (?, ?, ?)
    """, (id_web_gmao, id_article, quantite))
    # Les désignations sont remplies automatiquement par le trigger
```

### Frontend (JavaScript)

```javascript
// ✅ Affichage avec Select2 depuis tables sources
$('#article_select').select2({
    ajax: {
        url: '/projet16/api/search_articles',  // Lit depuis GS_ARTICLES
        // ...
    }
});

// ✅ Enregistrement dans WEB_GMAO_ARTICLES
$.ajax({
    url: '/projet16/api/add_article',
    method: 'POST',
    data: {
        id_web_gmao: 100,
        id_article: 456,
        quantite: 2.5
    }
});
```

---

## 📊 Flux de données

```
┌─────────────────────────────────────────────────────────┐
│         TABLES SOURCES (Lecture seule)                  │
├─────────────────────────────────────────────────────────┤
│  GS_ARTICLES  →  GS_FAMILLES  →  GS_TYPES_ARTICLE      │
│  (Designation)   (Designation)    (Designation)         │
│                                                          │
│  Modifiées par: Administrateur système UNIQUEMENT       │
│  Consultées par: Projet 16 (SELECT uniquement)          │
└──────────────────┬──────────────────────────────────────┘
                   │
                   │ Synchronisation automatique (Triggers)
                   ↓
┌─────────────────────────────────────────────────────────┐
│      WEB_GMAO_ARTICLES (Lecture + Écriture)            │
├─────────────────────────────────────────────────────────┤
│  ID, ID_WEB_GMAO, ID_GS_ARTICLES, Quantite             │
│  + Désignations copiées (synchronisées)                 │
│                                                          │
│  Modifiée par: Page web Projet 16                       │
│  Opérations: INSERT, UPDATE, DELETE                     │
└─────────────────────────────────────────────────────────┘
```

---

## ✅ Garanties du système

| Garantie | Description |
|----------|-------------|
| **Protection des sources** | GS_ARTICLES, GS_FAMILLES, GS_TYPES_ARTICLE ne sont jamais modifiées |
| **Synchronisation** | Mises à jour automatiques via triggers |
| **Historique** | Désignations copiées préservées même si source supprimée |
| **Flexibilité** | Nombre illimité d'articles par fiche |
| **Intégrité** | Contraintes FK et cascade de suppression |
| **Performance** | Index sur colonnes clés |

---

## 🔧 Tests réalisés

✅ Création de la table  
✅ Insertion d'articles avec auto-remplissage des désignations  
✅ Vérification des liaisons entre tables  
✅ Test de la suppression en cascade  
✅ Validation des contraintes de clés étrangères  

---

## 📌 Prochaines étapes

La table est créée et fonctionnelle. Il reste à :

1. ⏳ Adapter l'interface web pour utiliser `WEB_GMAO_ARTICLES`
2. ⏳ Créer les fonctions Python d'insertion/modification/suppression
3. ⏳ Ajouter les routes API Flask
4. ⏳ Modifier le popup de réparation pour gérer plusieurs articles

La structure est prête et respecte toutes vos règles ! 🎉




