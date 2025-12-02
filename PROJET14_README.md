# 📋 Projet 14 - Registre de suivi des déchets

## 📄 Description

Le **Projet 14** permet de gérer le registre de suivi des déchets collectés par l'entreprise Novaprint. Il s'agit d'un système de gestion conforme au formulaire FOR-SMI-38 (Version 02 du 28/09/2018).

---

## 🗄️ Structure de la base de données

### Table : `WEB_Suivi_Dechets`

| Colonne | Type | Description | Contraintes |
|---------|------|-------------|-------------|
| `ID` | INT | Identifiant unique | PRIMARY KEY, AUTO_INCREMENT |
| `Date` | DATE | Date de collecte | NOT NULL, DEFAULT GETDATE() |
| `Type` | NVARCHAR(100) | Type de déchet | NOT NULL |
| `Quantite` | DECIMAL(10,2) | Quantité collectée | NOT NULL |
| `Unite` | NVARCHAR(20) | Unité de mesure | NOT NULL, DEFAULT 'kg' |
| `Bon_Reception_Num` | NVARCHAR(50) | Numéro du bon de réception | NULL |
| `Receptionnaire` | NVARCHAR(200) | Nom du fournisseur collecteur | NULL |
| `Date_Creation` | DATETIME | Date de création de l'enregistrement | DEFAULT GETDATE() |

---

## 🎯 Fonctionnalités

### 1. Enregistrement des déchets
- **Date** : Par défaut la date du jour, modifiable
- **Type de déchet** : Liste de recherche avec saisie libre
  - Types prédéfinis :
    - Papier Offset
    - Carton blanc gris
    - Carton blanc bois
  - Possibilité d'ajouter un type personnalisé
- **Quantité** : Champ numérique décimal
- **Unité** : Par défaut "kg", modifiable
- **Bon de réception N°** : Champ texte optionnel
- **Réceptionnaire** : Nom du fournisseur qui a collecté le déchet

### 2. Visualisation des enregistrements
- Liste complète des déchets enregistrés
- Affichage du mois de collecte pour chaque enregistrement
- Tri par date décroissante

### 3. Gestion des enregistrements
- ✏️ **Modifier** un enregistrement existant
- 🗑️ **Supprimer** un enregistrement
- 🔄 **Réinitialiser** le formulaire

### 4. Statistiques
- 📊 **Statistiques globales** :
  - Total d'enregistrements
  - Quantité totale collectée
  - Nombre de types de déchets
  - Moyenne par enregistrement
  
- 📈 **Graphiques** :
  - Répartition par type de déchet (graphique en donut)
  - Évolution mensuelle sur 12 mois (graphique en barres)
  
- 📋 **Tableaux détaillés** :
  - Détails par type de déchet
  - Quantités totales et moyennes

---

## 📂 Structure des fichiers

```
C:\Apps\
├── logic/
│   └── projet14.py                 # Logique métier et fonctions de base de données
├── routes/
│   └── projet14_routes.py          # Routes Flask et endpoints API
├── templates/
│   ├── projet14.html               # Page principale du registre
│   └── projet14_stats.html         # Page des statistiques
└── PROJET14_README.md              # Cette documentation
```

---

## 🔌 Routes disponibles

| Route | Méthode | Description |
|-------|---------|-------------|
| `/projet14/` | GET | Page principale (sélection de section) |
| `/projet14/registre` | GET | Section Registre de suivi des déchets |
| `/projet14/saisie` | GET | Section Saisie (ouvre popup automatiquement) |
| `/projet14/statistiques` | GET | Section Statistiques |
| `/projet14/liste` | GET | Liste des déchets en JSON |
| `/projet14/get_types` | GET | Types prédéfinis en JSON |
| `/projet14/ajouter` | POST | Ajouter un nouvel enregistrement |
| `/projet14/modifier/<id>` | GET, POST | Récupérer ou modifier un enregistrement |
| `/projet14/supprimer/<id>` | POST, DELETE | Supprimer un enregistrement |
| `/projet14/api/statistiques` | GET | Statistiques en JSON |
| `/projet14/mois/<annee>/<mois>` | GET | Déchets pour un mois donné |

---

## 🎨 Technologies utilisées

### Backend
- **Flask** : Framework web Python
- **pyodbc** : Connexion à SQL Server
- **SQL Server** : Base de données

### Frontend
- **HTML5** / **CSS3** : Structure et style
- **JavaScript** / **jQuery** : Interactivité
- **Select2** : Liste de recherche avec saisie libre
- **Chart.js** : Graphiques statistiques
- **Bootstrap 5** : Framework CSS

---

## 💡 Utilisation

### Page principale

1. Accédez à http://localhost:5000/projet14/
2. Sélectionnez une section :
   - **📋 Registre** : Voir et gérer les déchets
   - **➕ Saisie** : Ajouter un nouveau fichier
   - **📊 Statistiques** : Consulter les statistiques

### Ajouter un déchet

1. Cliquez sur **➕ Saisie d'un nouveau fichier**
2. La popup s'ouvre automatiquement
3. Remplissez le formulaire :
   - Date (par défaut aujourd'hui)
   - Type de déchet (sélectionnez ou saisissez)
   - Quantité (numérique)
   - Unité (par défaut "kg")
   - Bon de réception N° (optionnel)
   - Réceptionnaire (optionnel)
4. Cliquez sur **💾 Enregistrer**

### Modifier un déchet

1. Cliquez sur le bouton **✏️ Modifier** dans la liste
2. Modifiez les champs souhaités dans le modal
3. Cliquez sur **💾 Enregistrer les modifications**

### Supprimer un déchet

1. Cliquez sur le bouton **🗑️ Supprimer** dans la liste
2. Confirmez la suppression

### Consulter les statistiques

1. Cliquez sur le lien **📈 Voir les statistiques**
2. Explorez les graphiques et tableaux détaillés

---

## 📊 Exemples de requêtes SQL

### Récupérer tous les déchets
```sql
SELECT * FROM WEB_Suivi_Dechets ORDER BY Date DESC;
```

### Total par type
```sql
SELECT 
    Type,
    SUM(Quantite) as Total_Quantite,
    COUNT(*) as Nombre_Enregistrements
FROM WEB_Suivi_Dechets
GROUP BY Type
ORDER BY Total_Quantite DESC;
```

### Total par mois
```sql
SELECT 
    FORMAT(Date, 'yyyy-MM') as Mois,
    SUM(Quantite) as Total_Quantite
FROM WEB_Suivi_Dechets
GROUP BY FORMAT(Date, 'yyyy-MM')
ORDER BY Mois;
```

---

## ✅ Validation des données

### Champs obligatoires
- ✅ Date
- ✅ Type de déchet
- ✅ Quantité
- ✅ Unité

### Champs optionnels
- Bon de réception N°
- Réceptionnaire

### Règles de validation
- La quantité doit être un nombre décimal positif
- La date ne peut pas être vide
- Le type ne peut pas être vide
- L'unité par défaut est "kg"

---

## 🔐 Sécurité

- Validation des données côté serveur
- Protection contre les injections SQL via paramétrage des requêtes
- Gestion des erreurs avec messages appropriés
- Confirmations avant suppression

---

## 📈 Améliorations futures possibles

1. 🔍 **Filtres avancés** :
   - Filtrer par période
   - Filtrer par type
   - Recherche textuelle

2. 📥 **Export** :
   - Export Excel
   - Export PDF
   - Export CSV

3. 📧 **Notifications** :
   - Alertes par email
   - Rappels de collecte

4. 👥 **Multi-utilisateurs** :
   - Authentification
   - Historique des modifications
   - Permissions

5. 📱 **Responsive** :
   - Version mobile optimisée
   - Application progressive (PWA)

---

## 🐛 Dépannage

### Le serveur ne démarre pas
```bash
# Vérifier que le port 5000 est libre
netstat -ano | findstr :5000

# Redémarrer le serveur
python app.py
```

### Erreur de connexion à la base de données
- Vérifier les paramètres dans `db.py`
- S'assurer que SQL Server est en cours d'exécution
- Vérifier les droits d'accès

### La table n'existe pas
```bash
# Recréer la table
python create_table_projet14.py
```

---

## 📞 Support

Pour toute question ou problème, contactez l'équipe de développement.

---

**Date de création** : 27 octobre 2025  
**Version** : 1.0  
**Statut** : ✅ Opérationnel

