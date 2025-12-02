# 📥 Import des données Excel - Projet 14

Ce script permet d'importer les données historiques depuis un fichier Excel vers la table `WEB_Suivi_Dechets`.

## 🎯 Objectif

Importer les données de l'année **2025** depuis votre fichier Excel existant vers la base de données, pour ensuite continuer à utiliser uniquement l'interface web du Projet 14.

---

## 📋 Prérequis

### 1. Installer les dépendances Python

Dans votre terminal PowerShell, depuis le dossier `C:\Apps` :

```powershell
.\venv\Scripts\activate
pip install pandas openpyxl
```

Ou installez toutes les dépendances :

```powershell
pip install -r requirements.txt
```

### 2. Préparer votre fichier Excel

Votre fichier Excel doit contenir les colonnes suivantes (les noms peuvent varier légèrement) :

| Nom de colonne Excel | Colonne dans la base de données |
|---------------------|----------------------------------|
| Date                | Date                             |
| Type de déchet      | Type                             |
| Quantité            | Quantite                         |
| Unité               | Unite                            |
| Bon de réception N° | Bon_Reception_Num                |
| Réceptionnaire      | Receptionnaire                   |

**Format de date accepté :** `DD/MM/YYYY` (ex: `04/01/2025`)

---

## 🚀 Utilisation

### Étape 1 : Placer votre fichier Excel

Placez votre fichier Excel dans le dossier `C:\Apps` et renommez-le `dechets_2025.xlsx` (ou notez son nom exact).

### Étape 2 : Activer l'environnement virtuel

```powershell
cd C:\Apps
.\venv\Scripts\activate
```

### Étape 3 : Exécuter le script

```powershell
python import_dechets_excel.py
```

### Étape 4 : Suivre les instructions

Le script vous demandera le chemin du fichier :

```
📂 Entrez le chemin du fichier Excel (ou appuyez sur Entrée pour 'dechets_2025.xlsx') :
```

- **Option 1** : Appuyez sur `Entrée` si votre fichier s'appelle `dechets_2025.xlsx`
- **Option 2** : Entrez le chemin complet, par exemple : `C:\Users\nom_utilisateur\Documents\mon_fichier.xlsx`

---

## ✅ Ce que fait le script

1. 📂 **Lit le fichier Excel** spécifié
2. 🔄 **Mappe les colonnes** automatiquement (gère les variantes orthographiques)
3. 📅 **Convertit les dates** de `DD/MM/YYYY` vers `YYYY-MM-DD`
4. 🗓️ **Filtre uniquement l'année 2025**
5. 🔍 **Vérifie les doublons** (date + type + quantité)
6. 💾 **Insère les enregistrements** dans la base de données
7. 📊 **Affiche un résumé** de l'import

---

## 📊 Exemple de résultat

```
================================================================================
📊 RÉSUMÉ DE L'IMPORT
================================================================================
✅ Enregistrements insérés : 38
⏭️  Doublons ignorés : 0
❌ Erreurs : 0
📁 Total traité : 38
================================================================================

🎉 Import terminé avec succès !
💡 Vous pouvez maintenant utiliser l'interface web du Projet 14.
```

---

## 🔧 Gestion des doublons

Le script vérifie automatiquement si un enregistrement existe déjà en comparant :
- ✅ Date
- ✅ Type de déchet
- ✅ Quantité

Si un doublon est détecté, il est ignoré et vous verrez un message :
```
⏭️  Ligne 5 : Doublon ignoré (2025-01-04 - papier offset - 885)
```

---

## ⚠️ Remarques importantes

1. **Import unique** : Ce script est conçu pour être exécuté **une seule fois** pour migrer vos données historiques.

2. **Après l'import** : Utilisez exclusivement l'interface web du Projet 14 pour saisir de nouveaux enregistrements.

3. **Année 2025 uniquement** : Seules les données de 2025 sont importées. Les autres années sont ignorées automatiquement.

4. **Vérification** : Après l'import, vérifiez dans l'interface web (section "Registre de suivi des déchets") que toutes vos données sont présentes.

---

## 🐛 Résolution de problèmes

### Erreur : `Fichier introuvable`
- Vérifiez le chemin du fichier
- Assurez-vous que le fichier existe bien dans le dossier indiqué

### Erreur : `No module named 'pandas'`
```powershell
pip install pandas openpyxl
```

### Erreur : `Colonnes manquantes`
- Vérifiez que votre fichier Excel contient bien toutes les colonnes requises
- Les noms peuvent avoir des variantes (ex: "Réceptionnaire" ou "Récéptionnaire")

### Erreur de connexion à la base de données
- Vérifiez que SQL Server est démarré
- Vérifiez les paramètres de connexion dans le script (ligne 7-13)

---

## 📞 Support

Si vous rencontrez des problèmes :
1. Vérifiez les messages d'erreur affichés par le script
2. Vérifiez que toutes les dépendances sont installées
3. Vérifiez la structure de votre fichier Excel

---

## ✨ Après l'import

Une fois l'import terminé avec succès :
1. ✅ Consultez vos données dans le Projet 14 : `http://localhost:5000/projet14/registre`
2. ✅ Le fichier Excel n'est plus nécessaire
3. ✅ Utilisez l'interface web pour toutes les futures saisies
4. 🗑️ Vous pouvez archiver ou supprimer le script `import_dechets_excel.py`














