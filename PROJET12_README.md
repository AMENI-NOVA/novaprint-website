# 📋 Projet 12 - Registre de suivi des Produits Non Conformes et des Réclamations Clients

## 📌 Description

Le Projet 12 est un système de gestion et de suivi des produits non conformes (NC) et des réclamations clients. Il permet d'enregistrer, de consulter et de gérer tous les cas de non-conformité et réclamations dans un tableau interactif.

## 🎯 Fonctionnalités

### 1️⃣ Sélection du type de registre
- **Produits NC** : Suivi des produits non conformes (TYPE = "NC")
- **Réclamations clients** : Suivi des réclamations clients (TYPE = "REC")

### 2️⃣ Saisie de données dans un tableau
L'interface présente un tableau avec les colonnes suivantes :

| Colonne | Description | Type de champ |
|---------|-------------|---------------|
| **DATE** | Date de l'enregistrement | Date picker |
| **RÉFÉRENCE** | Référence de la commande | Liste déroulante (COMMANDES.Reference) |
| **CLIENT** | Nom du client | Liste déroulante (SOCIETES.RaiSocTri) |
| **N° DE DOSSIER** | Numéro de commande | Liste déroulante (COMMANDES.Numero) |
| **NC** | Code ou identifiant de la NC | Champ texte |
| **DESCRIPTION DE LA NC** | Description détaillée | Zone de texte |
| **CAUSE** | Cause de la non-conformité | Zone de texte |
| **ACTIONS** | Enregistrer ou supprimer | Boutons d'action |

### 3️⃣ Fonctionnalités du tableau
- ➕ **Ajouter une ligne** : Bouton pour créer une nouvelle ligne de saisie
- 💾 **Enregistrer** : Sauvegarde l'enregistrement dans la base de données
- 🗑️ **Supprimer** : Supprime un enregistrement existant
- 🔄 **Filtrage automatique** : Les données affichées changent selon le type sélectionné (NC ou REC)

## 🗄️ Structure de la base de données

### Table : `WEB_PdtNC_RecClt`

```sql
CREATE TABLE WEB_PdtNC_RecClt (
    ID INT IDENTITY(1,1) PRIMARY KEY,
    Date DATETIME NULL,
    TYPE NVARCHAR(10) NULL,              -- 'NC' ou 'REC'
    NC NVARCHAR(500) NULL,
    DesNC NVARCHAR(MAX) NULL,
    Cause NVARCHAR(MAX) NULL,
    Numero_COMMANDES NVARCHAR(100) NULL,
    Reference_COMMANDES NVARCHAR(200) NULL,
    RaiSocTri_SOCIETES NVARCHAR(200) NULL
)
```

### Données de référence

Les listes déroulantes récupèrent les données depuis :
- **Références** : `COMMANDES.Reference`
- **Clients** : `SOCIETES.RaiSocTri`
- **Numéros** : `COMMANDES.Numero`

⚠️ **Important** : Aucune modification n'est effectuée dans les tables `COMMANDES` ou `SOCIETES`. Toutes les données sont stockées uniquement dans `WEB_PdtNC_RecClt`.

## 📁 Fichiers du projet

```
C:\Apps\
├── create_table_projet12.py         # Script de création de la table
├── logic/
│   └── projet12.py                   # Logique métier
├── routes/
│   └── projet12_routes.py            # Routes API Flask
├── templates/
│   └── projet12.html                 # Interface utilisateur (tableau)
└── app.py                            # Application Flask (avec routes enregistrées)
```

## 🔧 Installation

### 1. Créer la table dans la base de données

```bash
python create_table_projet12.py
```

### 2. Démarrer le serveur Flask

```bash
python app.py
```

### 3. Accéder à l'application

Ouvrir dans le navigateur :
- **URL directe** : `http://localhost:5000/projet12`
- **Depuis le menu** : Cliquer sur "📋 NC & Réclamations" dans la barre de navigation

## 🛠️ Fonctions principales

### Fichier `logic/projet12.py`

| Fonction | Description |
|----------|-------------|
| `get_liste_references()` | Récupère toutes les références de commandes |
| `get_liste_clients()` | Récupère tous les clients (RaiSocTri) |
| `get_liste_numeros()` | Récupère tous les numéros de commandes |
| `ajouter_enregistrement()` | Ajoute un nouvel enregistrement NC/REC |
| `get_liste_enregistrements(type)` | Récupère les enregistrements filtrés par type |
| `supprimer_enregistrement(id)` | Supprime un enregistrement par ID |

### Fichier `routes/projet12_routes.py`

| Route | Méthode | Description |
|-------|---------|-------------|
| `/projet12` | GET | Page principale |
| `/projet12/get_references` | GET | API - Liste des références |
| `/projet12/get_clients` | GET | API - Liste des clients |
| `/projet12/get_numeros` | GET | API - Liste des numéros |
| `/projet12/ajouter` | POST | API - Ajouter un enregistrement |
| `/projet12/liste?type=XX` | GET | API - Liste des enregistrements |
| `/projet12/supprimer/<id>` | DELETE | API - Supprimer un enregistrement |

## 🎨 Interface utilisateur

### Design
- ✅ Présentation en **tableau interactif**
- ✅ Design moderne et responsive
- ✅ Listes déroulantes pré-remplies
- ✅ Validation et messages d'alerte
- ✅ Nouvelle ligne en surbrillance verte
- ✅ Actions intuitives (💾 Enregistrer, 🗑️ Supprimer)

### Workflow utilisateur
1. Sélectionner le type de registre (NC ou REC)
2. Cliquer sur "➕ Ajouter une ligne"
3. Remplir les champs dans le tableau
4. Cliquer sur "💾 Enregistrer"
5. Les données apparaissent immédiatement dans le tableau

## 📊 Exemples d'utilisation

### Ajouter un produit non conforme
1. Sélectionner "🔴 Registre de suivi des produits NC"
2. Cliquer sur "➕ Ajouter une ligne"
3. Saisir :
   - Date : 21/10/2025
   - Référence : REF-2025-001
   - Client : SOCIÉTÉ ABC
   - N° de dossier : CMD-12345
   - NC : NC-001
   - Description : Défaut d'impression sur 50 exemplaires
   - Cause : Calibrage incorrect de la machine
4. Cliquer sur "💾 Enregistrer"

### Ajouter une réclamation client
1. Sélectionner "📞 Registre de suivi des réclamations clients"
2. Suivre le même processus de saisie

## 🔗 Intégration

Le Projet 12 est intégré dans :
- **Menu de navigation** : "📋 NC & Réclamations"
- **Page d'accueil** : "📋 Projet 12 – Registre NC & Réclamations Clients"
- **Blueprint Flask** : `projet12_bp`

## ✅ Tests

Pour vérifier que tout fonctionne :

```bash
# 1. Vérifier que la table existe
python -c "from db import get_db_cursor; print('Table OK')"

# 2. Tester les routes
curl http://localhost:5000/projet12/get_references
curl http://localhost:5000/projet12/get_clients
curl http://localhost:5000/projet12/liste?type=NC
```

## 📝 Notes techniques

- **Framework** : Flask (Python)
- **Base de données** : SQL Server
- **Frontend** : HTML5, CSS3, JavaScript vanilla
- **Responsive** : Oui
- **AJAX** : Oui (pour les opérations CRUD)

## 🚀 Améliorations futures possibles

- [ ] Export Excel des registres
- [ ] Filtres avancés (par date, client, etc.)
- [ ] Statistiques et graphiques
- [ ] Notifications par email
- [ ] Pièces jointes (photos, documents)
- [ ] Suivi des actions correctives

---

**Date de création** : 21 octobre 2025  
**Version** : 1.0  
**Auteur** : Novaprint Tunisie




















