# Projet 11 - Logique Quantité Prévue

## ✅ RÈGLE IMPLÉMENTÉE

La **quantité prévue affichée** pour un poste suit maintenant cette logique:

```
SI OpPrevDev_GP_FICHES_OPERATIONS existe ET > 0
    ALORS Quantité Prévue = OpPrevDev_GP_FICHES_OPERATIONS
SINON
    Quantité Prévue = QteComm_COMMANDES
```

---

## 🎯 CONTEXTE

### Deux Sources de Quantité

**1. Quantité Commande** (`QteComm_COMMANDES`):
- Source: Table `COMMANDES`
- Représente: **Quantité totale commandée par le client**
- Exemple: 15,000 pièces

**2. Quantité Prévue par Poste** (`OpPrevDev_GP_FICHES_OPERATIONS`):
- Source: Table `GP_FICHES_OPERATIONS`
- Représente: **Quantité prévue pour ce poste spécifique**
- Exemple: 15,000 pièces (ou différent si production partielle)

---

## 📊 CAS D'USAGE

### Cas 1: OpPrevDev Renseigné

**Données**:
```
QteComm_COMMANDES = 15,000
OpPrevDev_GP_FICHES_OPERATIONS = 12,000
```

**Logique appliquée**:
```
OpPrevDev existe (12,000) ET > 0 → ✅
→ Quantité Prévue = 12,000
```

**Affichage**:
```
Quantité Prévue (Poste): 12,000 pièces
```

**Raison**: Production partielle sur ce poste (peut-être 3,000 sur un autre poste)

---

### Cas 2: OpPrevDev NULL ou 0

**Données**:
```
QteComm_COMMANDES = 15,000
OpPrevDev_GP_FICHES_OPERATIONS = NULL (ou 0)
```

**Logique appliquée**:
```
OpPrevDev est NULL (ou 0) → ❌
→ Quantité Prévue = QteComm_COMMANDES
→ Quantité Prévue = 15,000
```

**Affichage**:
```
Quantité Prévue (Poste): 15,000 pièces
```

**Raison**: Pas de quantité spécifique prévue pour ce poste, donc on prend la quantité totale de la commande.

---

### Cas 3: Production Complète

**Données**:
```
QteComm_COMMANDES = 10,000
OpPrevDev_GP_FICHES_OPERATIONS = 10,000
```

**Logique appliquée**:
```
OpPrevDev existe (10,000) ET > 0 → ✅
→ Quantité Prévue = 10,000
```

**Affichage**:
```
Quantité Prévue (Poste): 10,000 pièces
```

**Raison**: Production complète prévue sur ce poste.

---

## 🔧 IMPLÉMENTATION

### Fonction Backend Modifiée

**Fichier**: `logic/projet11.py`  
**Fonction**: `get_postes_prevus_by_commande_service()`  
**Ligne**: 313-316

```python
for row in cursor.fetchall():
    # Logique quantité prévue:
    # Si OpPrevDev existe et > 0, l'utiliser
    # Sinon, utiliser QteComm_COMMANDES (quantité commande)
    qte_prevue = row.OpPrevDev if (row.OpPrevDev and row.OpPrevDev > 0) else row.QteComm_COMMANDES
    
    postes.append({
        # ...
        "qte_prevue": qte_prevue,  # ← Quantité calculée
        "op_prev_dev": row.OpPrevDev or 0.000,  # ← Valeur brute stockée
        # ...
    })
```

**Distinction importante**:
- `qte_prevue`: Quantité **affichée** (avec logique de fallback)
- `op_prev_dev`: Valeur **brute** de OpPrevDev (pour référence)

---

### Requête SQL

**Jointure avec GP_FICHES_OPERATIONS**:

```sql
LEFT JOIN (
    SELECT 
        ID_FICHE_TRAVAIL,
        SUM(OpPrevDev) as OpPrevDev,
        SUM(TpsPrevDev) as TpsPrevDev
    FROM GP_FICHES_OPERATIONS
    GROUP BY ID_FICHE_TRAVAIL
) FOP ON FOP.ID_FICHE_TRAVAIL = FT.ID
```

**Type de jointure**: `LEFT JOIN` → Permet de récupérer les fiches même si aucune opération n'existe.

**Résultat**: `OpPrevDev` peut être `NULL` si aucune opération n'est trouvée.

---

## 📈 EXEMPLE COMPLET

### Commande: 2025050026 - 15,000 badges

#### Service: OFFSET FEUILLES

**Données en base**:
```
Table: COMMANDES
  QteComm = 15,000

Table: GP_FICHES_OPERATIONS
  ID_FICHE_TRAVAIL = 409438
  OpPrevDev = NULL  ← Pas renseigné
```

**Calcul**:
```python
OpPrevDev = NULL
→ Condition: NULL and NULL > 0 → False
→ qte_prevue = QteComm_COMMANDES
→ qte_prevue = 15,000
```

**Affichage Frontend**:
```
┌────────────────────────────────────────┐
│ Machine Prévue: XL75                   │
│ Quantité Prévue: 15,000 pièces        │ ← QteComm_COMMANDES
│ Temps Prévu: 2.500 h                  │
└────────────────────────────────────────┘
```

---

#### Service: MASSICOTAGE (Production Partielle)

**Données en base**:
```
Table: COMMANDES
  QteComm = 15,000

Table: GP_FICHES_OPERATIONS
  ID_FICHE_TRAVAIL = 409439
  OpPrevDev = 10,000  ← Renseigné (partiel)
```

**Calcul**:
```python
OpPrevDev = 10,000
→ Condition: 10,000 and 10,000 > 0 → True
→ qte_prevue = OpPrevDev
→ qte_prevue = 10,000
```

**Affichage Frontend**:
```
┌────────────────────────────────────────┐
│ Machine Prévue: MASSICOT POLAIRE 137   │
│ Quantité Prévue: 10,000 pièces        │ ← OpPrevDev
│ Temps Prévu: 1.500 h                  │
└────────────────────────────────────────┘
```

**Note**: Les 5,000 pièces restantes sont peut-être prévues sur un autre massicot.

---

## 🎨 IMPACT SUR L'INTERFACE

### Frontend JavaScript

**Fichier**: `templates/projet11_nouveau.html`

**Affichage de la quantité**:

```javascript
// La quantité prévue vient du backend avec la logique déjà appliquée
$('#qte_prevue').text(poste.qte_prevue.toLocaleString('fr-FR'));
```

**Pas de logique supplémentaire** nécessaire côté frontend, car le backend envoie déjà la bonne valeur!

---

### Suggestion de Quantité

**Calcul du reste à produire**:

```javascript
const qtePrevue = poste.qte_prevue;  // Déjà calculée par le backend
const totalProduit = /* somme des traitements existants */;
const reste = qtePrevue - totalProduit;

// Suggérer le reste
$('#nb_op').val(reste);
```

**La suggestion utilise automatiquement** la quantité prévue correcte (avec fallback)!

---

## 🔍 VÉRIFICATION

### Dans SQL Server

**Requête pour voir les deux valeurs**:

```sql
SELECT 
    C.Numero,
    C.QteComm as Qte_Commande,
    FOP.OpPrevDev as Qte_Poste,
    CASE 
        WHEN FOP.OpPrevDev IS NOT NULL AND FOP.OpPrevDev > 0 
        THEN FOP.OpPrevDev
        ELSE C.QteComm
    END as Qte_Prevue_Finale,
    SRV.Nom as Service,
    P.Nom as Poste
FROM GP_FICHES_TRAVAIL FT
INNER JOIN COMMANDES C ON C.ID = FT.ID_COMMANDE
INNER JOIN GP_POSTES P ON P.ID = FT.ID_POSTE
INNER JOIN GP_SERVICES SRV ON SRV.ID = P.ID_SERVICE
LEFT JOIN (
    SELECT ID_FICHE_TRAVAIL, SUM(OpPrevDev) as OpPrevDev
    FROM GP_FICHES_OPERATIONS
    GROUP BY ID_FICHE_TRAVAIL
) FOP ON FOP.ID_FICHE_TRAVAIL = FT.ID
WHERE C.Numero = '2025050026'
```

**Résultat exemple**:
```
Numero       Qte_Commande  Qte_Poste  Qte_Prevue_Finale  Service          Poste
-----------  ------------  ---------  -----------------  ---------------  ----------------
2025050026   15000         NULL       15000             OFFSET FEUILLES  XL75
2025050026   15000         12000      12000             MASSICOTAGE      POLAIRE 137
2025050026   15000         3000       3000              MASSICOTAGE      POLAIRE 92
```

**Interprétation**:
- OFFSET: Pas de quantité spécifique → Utilise 15,000 (quantité commande)
- MASSICOT 137: 12,000 prévu
- MASSICOT 92: 3,000 prévu
- Total MASSICOTAGE: 12,000 + 3,000 = 15,000 ✓

---

## 💡 AVANTAGES DE CETTE LOGIQUE

### 1. Flexibilité ✅

**Avec OpPrevDev**:
- Permet la **répartition** sur plusieurs postes
- Quantités spécifiques par machine
- Production optimisée

**Sans OpPrevDev**:
- **Fallback automatique** sur la quantité commande
- Pas besoin de saisir OpPrevDev pour chaque poste
- Fonctionne même si GP_FICHES_OPERATIONS est vide

---

### 2. Cohérence ✅

**Toujours une quantité**:
- Jamais de quantité à 0 ou NULL affichée
- Si pas de détail par poste → Quantité commande
- Garantit une suggestion de quantité valide

---

### 3. Simplicité ✅

**Pas de saisie manuelle**:
- Quantité calculée automatiquement
- Logique transparente pour l'utilisateur
- Moins d'erreurs

---

## 🚀 POUR TESTER

**Serveur Flask**: Déjà redémarré automatiquement ✓

**Actualisez votre navigateur**:
```
http://localhost:5000/projet11/nouveau
```

### Test Cas 1: Avec OpPrevDev

```
1. Trouver une commande avec OpPrevDev renseigné
2. Sélectionner cette commande
3. Sélectionner un service
4. Vérifier "Quantité Prévue" affichée
   → Doit correspondre à OpPrevDev ✓
```

---

### Test Cas 2: Sans OpPrevDev

```
1. Trouver une commande sans OpPrevDev (NULL)
2. Sélectionner cette commande
3. Sélectionner un service
4. Vérifier "Quantité Prévue" affichée
   → Doit correspondre à QteComm_COMMANDES ✓
```

---

### Requête SQL pour Trouver des Exemples

**Avec OpPrevDev**:
```sql
SELECT TOP 3 C.Numero, FOP.OpPrevDev, C.QteComm
FROM GP_FICHES_TRAVAIL FT
INNER JOIN COMMANDES C ON C.ID = FT.ID_COMMANDE
LEFT JOIN (
    SELECT ID_FICHE_TRAVAIL, SUM(OpPrevDev) as OpPrevDev
    FROM GP_FICHES_OPERATIONS
    GROUP BY ID_FICHE_TRAVAIL
) FOP ON FOP.ID_FICHE_TRAVAIL = FT.ID
WHERE FOP.OpPrevDev IS NOT NULL AND FOP.OpPrevDev > 0
```

**Sans OpPrevDev**:
```sql
SELECT TOP 3 C.Numero, FOP.OpPrevDev, C.QteComm
FROM GP_FICHES_TRAVAIL FT
INNER JOIN COMMANDES C ON C.ID = FT.ID_COMMANDE
LEFT JOIN (
    SELECT ID_FICHE_TRAVAIL, SUM(OpPrevDev) as OpPrevDev
    FROM GP_FICHES_OPERATIONS
    GROUP BY ID_FICHE_TRAVAIL
) FOP ON FOP.ID_FICHE_TRAVAIL = FT.ID
WHERE FOP.OpPrevDev IS NULL OR FOP.OpPrevDev = 0
```

---

## 📋 EXEMPLE DÉTAILLÉ

### Commande: 2025050026 - 15,000 badges

#### Service: OFFSET FEUILLES

**Tables**:
```
COMMANDES:
  Numero = 2025050026
  QteComm = 15,000  ← Quantité totale

GP_FICHES_OPERATIONS:
  ID_FICHE_TRAVAIL = 409438
  OpPrevDev = NULL  ← Pas de quantité spécifique
```

**Calcul**:
```python
row.OpPrevDev = NULL
→ Condition: NULL and NULL > 0 → False
→ qte_prevue = row.QteComm_COMMANDES
→ qte_prevue = 15,000
```

**Interface Web**:
```
┌─────────────────────────────────────────────┐
│ 📋 Informations Prévues                     │
├─────────────────────────────────────────────┤
│ Machine Prévue: XL75                        │
│ Quantité Prévue: 15,000 pièces             │ ← QteComm
│ Temps Prévu: 2.500 h                       │
│ Fiche de Travail: #409438                  │
└─────────────────────────────────────────────┘
```

---

#### Service: MASSICOTAGE (Répartition)

**Tables**:
```
COMMANDES:
  Numero = 2025050026
  QteComm = 15,000  ← Quantité totale

GP_FICHES_OPERATIONS (Poste 1):
  ID_FICHE_TRAVAIL = 409439
  OpPrevDev = 10,000  ← Massicot 1

GP_FICHES_OPERATIONS (Poste 2):
  ID_FICHE_TRAVAIL = 409440
  OpPrevDev = 5,000  ← Massicot 2
```

**Calcul Poste 1**:
```python
row.OpPrevDev = 10,000
→ Condition: 10,000 and 10,000 > 0 → True
→ qte_prevue = row.OpPrevDev
→ qte_prevue = 10,000
```

**Interface Web (Poste 1)**:
```
┌─────────────────────────────────────────────┐
│ 📋 Informations Prévues                     │
├─────────────────────────────────────────────┤
│ Machine Prévue: MASSICOT POLAIRE 137        │
│ Quantité Prévue: 10,000 pièces             │ ← OpPrevDev
│ Temps Prévu: 1.500 h                       │
│ Fiche de Travail: #409439                  │
└─────────────────────────────────────────────┘
```

**Calcul Poste 2**:
```python
row.OpPrevDev = 5,000
→ Condition: 5,000 and 5,000 > 0 → True
→ qte_prevue = row.OpPrevDev
→ qte_prevue = 5,000
```

**Interface Web (Poste 2)**:
```
┌─────────────────────────────────────────────┐
│ 📋 Informations Prévues                     │
├─────────────────────────────────────────────┤
│ Machine Prévue: MASSICOT POLAIRE 92         │
│ Quantité Prévue: 5,000 pièces              │ ← OpPrevDev
│ Temps Prévu: 0.750 h                       │
│ Fiche de Travail: #409440                  │
└─────────────────────────────────────────────┘
```

**Vérification**: 10,000 + 5,000 = 15,000 ✓ (Total commande respecté)

---

## 🎯 CALCUL DU RESTE À PRODUIRE

### Logique

```javascript
const qtePrevue = poste.qte_prevue;  // Déjà calculée avec fallback
const totalProduit = /* somme des traitements existants */;
const reste = qtePrevue - totalProduit;

if (reste > 0) {
    $('#nb_op').val(reste);  // Suggérer le reste
}
```

**Avec le fallback**:
- Si OpPrevDev existe → Reste basé sur OpPrevDev
- Si OpPrevDev NULL → Reste basé sur QteComm

---

## 📊 TABLEAUX DE VÉRITÉ

### Condition de Sélection

| OpPrevDev | Condition | Résultat |
|-----------|-----------|----------|
| NULL | NULL and NULL > 0 | **False** → QteComm |
| 0 | 0 and 0 > 0 | **False** → QteComm |
| 100 | 100 and 100 > 0 | **True** → OpPrevDev (100) |
| 15000 | 15000 and 15000 > 0 | **True** → OpPrevDev (15000) |

---

### Exemples de Résultats

| QteComm | OpPrevDev | Quantité Affichée | Source |
|---------|-----------|-------------------|--------|
| 15000 | NULL | 15000 | QteComm (fallback) |
| 15000 | 0 | 15000 | QteComm (fallback) |
| 15000 | 12000 | 12000 | OpPrevDev |
| 15000 | 15000 | 15000 | OpPrevDev |
| 10000 | 5000 | 5000 | OpPrevDev |

---

## ✅ VALIDATION

### Test 1: Vérifier l'Affichage

**Dans l'interface web**:

1. Sélectionner une commande
2. Sélectionner un service
3. Observer la "Quantité Prévue" affichée

**Vérifier dans la base**:
```sql
SELECT 
    C.QteComm,
    FOP.OpPrevDev,
    CASE 
        WHEN FOP.OpPrevDev IS NOT NULL AND FOP.OpPrevDev > 0 
        THEN FOP.OpPrevDev 
        ELSE C.QteComm 
    END as Qte_Prevue_Calculee
FROM GP_FICHES_TRAVAIL FT
INNER JOIN COMMANDES C ON C.ID = FT.ID_COMMANDE
LEFT JOIN (
    SELECT ID_FICHE_TRAVAIL, SUM(OpPrevDev) as OpPrevDev
    FROM GP_FICHES_OPERATIONS
    GROUP BY ID_FICHE_TRAVAIL
) FOP ON FOP.ID_FICHE_TRAVAIL = FT.ID
WHERE C.Numero = '[votre commande]'
```

**La valeur affichée doit correspondre à `Qte_Prevue_Calculee`!**

---

## 🎊 RÉSUMÉ

### Règle Implémentée

✅ **Si OpPrevDev existe et > 0**: Utiliser OpPrevDev  
✅ **Si OpPrevDev NULL ou 0**: Utiliser QteComm_COMMANDES  

### Avantages

✅ **Flexibilité**: Gère les productions partielles  
✅ **Robustesse**: Fallback automatique  
✅ **Cohérence**: Toujours une quantité valide  
✅ **Simplicité**: Logique transparente pour l'utilisateur  

### Code Modifié

✅ **Backend**: `logic/projet11.py` - Fonction `get_postes_prevus_by_commande_service()`  
✅ **Logique**: 3 lignes de code pour gérer le fallback  
✅ **Frontend**: Aucune modification nécessaire (reçoit la bonne valeur)  

---

**Version**: 1.7.5  
**Statut**: ✅ **Production Ready**

---

*Logique quantité prévue avec fallback implémentée!* 🎯✨


























