# 📊 PROJET 12 - Statistiques Proposées

## 📌 Contexte

Le Projet 12 est un **Registre de suivi des Produits Non Conformes (NC) et des Réclamations Clients (REC)**.

### Données Disponibles

| Champ | Description |
|-------|-------------|
| `Date` | Date de l'enregistrement |
| `TYPE` | Type : 'NC' ou 'REC' |
| `Numero_COMMANDES` | N° de dossier |
| `Reference_COMMANDES` | Référence produit |
| `RaiSocTri_SOCIETES` | Nom du client |
| `QteComm_COMMANDES` | Quantité commandée |
| `QteNC` | Quantité non conforme |
| `CaracNC` | Caractéristique NC (Majeur/Mineur) |
| `NC` | Code NC |
| `DesNC` | Description de la NC |
| `Cause` | Cause de la NC |
| `RefFich` | Référence du fichier (RCL XX ou NCP XX) |

---

## 📈 STATISTIQUES PROPOSÉES

### 🎯 **1. INDICATEURS CLÉS (KPI)**

#### Vue d'ensemble (cartes résumé)

```
┌─────────────────────────────────────────────────────────────────┐
│  📊 Tableau de Bord Qualité                                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   🔴 NC      │  │   📞 REC     │  │   📊 TOTAL   │          │
│  │     125      │  │      48      │  │     173      │          │
│  │  Ce mois     │  │  Ce mois     │  │  Ce mois     │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   ⚠️ Majeurs │  │   ✓ Mineurs  │  │   📈 Taux    │          │
│  │      15      │  │     110      │  │    2.5%      │          │
│  │  Urgence     │  │  Normales    │  │  Non conf.   │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

**Indicateurs à calculer :**
- Nombre total de NC ce mois
- Nombre total de réclamations ce mois
- Nombre total d'enregistrements
- Nombre de NC majeures
- Nombre de NC mineures
- **Taux de non-conformité** = (Somme QteNC / Somme QteComm) × 100
- Évolution par rapport au mois précédent (▲ +12% ou ▼ -5%)

---

### 📅 **2. ÉVOLUTION TEMPORELLE**

#### A. Graphique en ligne : Tendance NC vs REC

```
Nombre de cas
    │
 25 │        ●──────●
    │       /        \
 20 │      /          ●────●
    │     /
 15 │    ●
    │
 10 │
    │
  5 │
    │
  0 └─────────────────────────────────────
      Jan  Fév  Mar  Avr  Mai  Jun  Jul
      
      ──●── NC     ──○── Réclamations
```

**Données :**
- Nombre de NC par mois (6 derniers mois)
- Nombre de réclamations par mois (6 derniers mois)

#### B. Graphique en barres : Comparaison mensuelle

```sql
SELECT 
    FORMAT(Date, 'yyyy-MM') as Mois,
    COUNT(CASE WHEN TYPE = 'NC' THEN 1 END) as NombreNC,
    COUNT(CASE WHEN TYPE = 'REC' THEN 1 END) as NombreREC
FROM WEB_PdtNC_RecClt
WHERE Date >= DATEADD(MONTH, -6, GETDATE())
GROUP BY FORMAT(Date, 'yyyy-MM')
ORDER BY Mois
```

---

### 👥 **3. ANALYSE PAR CLIENT**

#### Top 10 Clients avec le plus de NC/REC

```
Client                        | NC  | REC | Total | Taux NC %
------------------------------|-----|-----|-------|----------
IMPRIMERIE ABC                | 45  | 12  |  57   |   3.2%
SOCIÉTÉ XYZ                   | 32  |  8  |  40   |   2.1%
PRINTING SERVICES             | 28  |  5  |  33   |   1.9%
...
```

**SQL :**
```sql
SELECT 
    RaiSocTri_SOCIETES as Client,
    COUNT(CASE WHEN TYPE = 'NC' THEN 1 END) as NombreNC,
    COUNT(CASE WHEN TYPE = 'REC' THEN 1 END) as NombreREC,
    COUNT(*) as Total,
    CAST((SUM(CAST(QteNC AS FLOAT)) / NULLIF(SUM(CAST(QteComm_COMMANDES AS FLOAT)), 0)) * 100 AS DECIMAL(5,2)) as TauxNC
FROM WEB_PdtNC_RecClt
WHERE Date >= DATEADD(MONTH, -3, GETDATE())
GROUP BY RaiSocTri_SOCIETES
ORDER BY Total DESC
```

---

### 🔍 **4. ANALYSE DES CAUSES**

#### Répartition des causes principales

```
Graphique en secteurs (Camembert) :

          Calibrage machine (35%)
         /                        \
    Défaut matière (25%)          Erreur humaine (20%)
         \                        /
          Autres causes (20%)
```

**SQL :**
```sql
SELECT 
    Cause,
    COUNT(*) as Nombre,
    CAST(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM WEB_PdtNC_RecClt WHERE TYPE = 'NC') AS DECIMAL(5,2)) as Pourcentage
FROM WEB_PdtNC_RecClt
WHERE TYPE = 'NC' AND Cause IS NOT NULL AND Cause != ''
GROUP BY Cause
ORDER BY Nombre DESC
```

**TOP 5 des causes** :
1. Problème de calibrage machine
2. Défaut matière première
3. Erreur opérateur
4. Défaut d'impression
5. Problème de découpe

---

### 📦 **5. ANALYSE PAR PRODUIT/RÉFÉRENCE**

#### Références avec le plus de NC

```
Référence           | Nb NC | Qté NC | Qté Commandes | Taux %
--------------------|-------|--------|---------------|--------
REF-2025-001        |   8   |  450   |   15,000      |  3.0%
REF-2025-045        |   6   |  320   |   12,000      |  2.7%
REF-2025-023        |   5   |  280   |   10,500      |  2.7%
...
```

**SQL :**
```sql
SELECT 
    Reference_COMMANDES,
    COUNT(*) as NombreNC,
    SUM(QteNC) as QteTotaleNC,
    SUM(QteComm_COMMANDES) as QteTotaleCommandes,
    CAST((SUM(CAST(QteNC AS FLOAT)) / NULLIF(SUM(CAST(QteComm_COMMANDES AS FLOAT)), 0)) * 100 AS DECIMAL(5,2)) as TauxNC
FROM WEB_PdtNC_RecClt
WHERE TYPE = 'NC' AND Reference_COMMANDES IS NOT NULL
GROUP BY Reference_COMMANDES
ORDER BY NombreNC DESC
```

---

### 🎯 **6. ANALYSE DE GRAVITÉ**

#### Répartition Majeur vs Mineur

```
Graphique en barres :

Majeur     ████████████ (15%)
           ↑ Action urgente requise

Mineur     ████████████████████████████████████████████ (85%)
           ↑ Suivi standard

           0%    20%    40%    60%    80%    100%
```

**SQL :**
```sql
SELECT 
    ISNULL(CaracNC, 'Non spécifié') as Gravite,
    COUNT(*) as Nombre,
    CAST(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM WEB_PdtNC_RecClt WHERE TYPE = 'NC') AS DECIMAL(5,2)) as Pourcentage
FROM WEB_PdtNC_RecClt
WHERE TYPE = 'NC'
GROUP BY CaracNC
ORDER BY 
    CASE 
        WHEN CaracNC = 'Majeur' THEN 1
        WHEN CaracNC = 'Mineur' THEN 2
        ELSE 3
    END
```

---

### 📊 **7. TABLEAU DÉTAILLÉ AVEC FILTRES**

Interface interactive avec :
- **Filtres** :
  - Période (date début - date fin)
  - Type (NC / REC / Tous)
  - Client (liste déroulante)
  - Gravité (Majeur / Mineur)
  - Référence produit
  
- **Export** :
  - 📄 Export Excel
  - 📄 Export PDF
  - 📄 Export CSV

---

### 📈 **8. ANALYSE COMPARATIVE**

#### Comparaison période vs période

```
Indicateur              | Ce mois | Mois dernier | Évolution
------------------------|---------|--------------|----------
Nb de NC                |   125   |     142      |  ▼ -12%  ✓
Nb de réclamations      |    48   |      45      |  ▲ +7%   ⚠️
Taux NC global          |  2.5%   |    3.1%      |  ▼ -19%  ✓
NC majeures             |    15   |      18      |  ▼ -17%  ✓
```

---

### 🎯 **9. STATISTIQUES AVANCÉES**

#### A. Délai moyen de traitement
(Si vous ajoutez un champ date de clôture)

```
Délai moyen de résolution : 5,2 jours
  - NC mineures : 3,5 jours
  - NC majeures : 8,7 jours
  - Réclamations : 6,3 jours
```

#### B. Taux de récurrence
```
Clients avec récurrence > 3 NC :
  - Client A : 5 NC sur REF-2025-001
  - Client B : 4 NC sur REF-2025-023
```

#### C. Analyse saisonnière
```
Q1 2025: 245 NC | Q2 2025: 198 NC ▼ -19%
Pic en Mars : 95 NC (formation nouveau personnel)
```

---

## 🎨 PRÉSENTATION VISUELLE PROPOSÉE

### Layout de la page Statistiques

```
┌─────────────────────────────────────────────────────────────┐
│  📊 STATISTIQUES - Registre Qualité                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  [Filtres]  Période: [▼ Ce mois]  Type: [▼ Tous]           │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  🎯 INDICATEURS CLÉS                                   │ │
│  │  [Cartes KPI en ligne]                                 │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌──────────────────────┐  ┌──────────────────────┐        │
│  │  📈 ÉVOLUTION        │  │  👥 TOP CLIENTS      │        │
│  │  [Graphique ligne]   │  │  [Tableau classé]    │        │
│  └──────────────────────┘  └──────────────────────┘        │
│                                                              │
│  ┌──────────────────────┐  ┌──────────────────────┐        │
│  │  🔍 CAUSES           │  │  📦 PRODUITS         │        │
│  │  [Camembert]         │  │  [Barres]            │        │
│  └──────────────────────┘  └──────────────────────┘        │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  📊 TABLEAU DÉTAILLÉ                                   │ │
│  │  [Export Excel] [Export PDF]                           │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 RECOMMANDATIONS DE MISE EN ŒUVRE

### Phase 1 - Statistiques de Base (Priorité Haute)
✅ À implémenter en premier :
1. **Indicateurs KPI** (cartes résumé)
2. **Évolution temporelle** (graphique ligne)
3. **Top clients** (tableau)
4. **Filtres de base** (période, type)

### Phase 2 - Analyses Avancées (Priorité Moyenne)
📊 À ajouter ensuite :
5. **Analyse des causes** (camembert)
6. **Analyse par produit**
7. **Gravité Majeur/Mineur**
8. **Exports Excel/PDF**

### Phase 3 - Fonctionnalités Avancées (Priorité Basse)
🎯 Améliorations futures :
9. **Comparaisons période**
10. **Alertes automatiques** (seuils dépassés)
11. **Prédictions** (Machine Learning)
12. **Dashboard temps réel**

---

## 📚 BIBLIOTHÈQUES RECOMMANDÉES

### Backend (Python/Flask)
- **pandas** : Manipulation de données
- **numpy** : Calculs statistiques
- **openpyxl** : Export Excel

### Frontend (JavaScript)
- **Chart.js** : Graphiques simples et élégants
- **ApexCharts** : Graphiques interactifs avancés
- **DataTables** : Tableaux interactifs avec filtres
- **jsPDF** : Export PDF

---

## 💡 EXEMPLE DE CODE SQL POUR STATISTIQUES

### Vue SQL récapitulative
```sql
CREATE VIEW VUE_STATS_QUALITE AS
SELECT 
    YEAR(Date) as Annee,
    MONTH(Date) as Mois,
    TYPE,
    COUNT(*) as NombreCas,
    SUM(QteNC) as QteTotaleNC,
    SUM(QteComm_COMMANDES) as QteTotaleCommandes,
    CAST((SUM(CAST(QteNC AS FLOAT)) / NULLIF(SUM(CAST(QteComm_COMMANDES AS FLOAT)), 0)) * 100 AS DECIMAL(5,2)) as TauxNC,
    COUNT(CASE WHEN CaracNC = 'Majeur' THEN 1 END) as NombreMajeurs,
    COUNT(CASE WHEN CaracNC = 'Mineur' THEN 1 END) as NombreMineurs
FROM WEB_PdtNC_RecClt
GROUP BY YEAR(Date), MONTH(Date), TYPE
```

---

## ✅ CONCLUSION

**Les statistiques les plus utiles pour le Projet 12 sont :**

1. 📊 **KPI visuels** : Nombre de NC/REC, taux, évolution
2. 📈 **Tendances temporelles** : Graphiques d'évolution
3. 👥 **Analyse clients** : Qui génère le plus de NC/REC
4. 🔍 **Causes racines** : Identifier les problèmes récurrents
5. 📦 **Produits critiques** : Quelles références poser problème
6. ⚠️ **Gravité** : Prioriser les actions (Majeur vs Mineur)

Ces statistiques permettront de :
- ✅ Identifier les tendances
- ✅ Prioriser les actions correctives
- ✅ Suivre l'amélioration continue
- ✅ Prendre des décisions basées sur les données
- ✅ Présenter des rapports qualité aux dirigeants

---

*Document créé le 24 octobre 2025*  
*Pour le Projet 12 - Registre NC & Réclamations*
















