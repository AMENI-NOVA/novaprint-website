# Projet 11 - Correction Erreur 500 (Services Non Prévus)

## 📅 Date de correction
20 octobre 2025

## 🔍 Problème Identifié

### Symptôme
```
POST http://localhost:5000/projet11/api/traitements
Error: Erreur 500: {
  "error": "Erreur lors de la création du traitement - Vérifiez les logs serveur"
}
```

L'erreur 400 a été corrigée mais maintenant une **erreur 500** se produit lors de l'enregistrement d'un service non prévu.

## 🔧 Corrections Appliquées

### 1. Correction de l'Objet Virtuel `fiche_data`

**Problème** : La création de l'objet virtuel utilisait une syntaxe incorrecte avec `type()` et des clés numériques qui ne fonctionnaient pas comme attributs.

**AVANT** (ligne 706-722) :
```python
fiche_data = type('obj', (object,), {
    0: None,  # Ne fonctionne pas comme attribut
    1: commande_data[0],
    # ...
})()
```
❌ Impossible d'accéder via `fiche_data[5]`

**APRÈS** (ligne 707-731) :
```python
class FicheDataVirtuelle:
    def __init__(self, commande_data, nom_poste_reel, nom_service):
        # Simuler les colonnes d'un résultat SQL par index
        self.data = [
            None,                    # [0] FT.ID
            commande_data[0],        # [1] ID_COMMANDE
            None,                    # [2] ID_POSTE
            # ... tous les champs
        ]
    
    def __getitem__(self, index):
        return self.data[index]

fiche_data = FicheDataVirtuelle(commande_data, nom_poste_reel, nom_service)
```
✅ Fonctionne correctement avec `fiche_data[5]`

### 2. Gestion de NULL pour les Services Non Prévus

**Problème** : Insérer `id_fiche_travail = 0` pourrait causer des problèmes avec les contraintes de la base de données.

**CORRECTION** (ligne 846-847) :
```python
# Pour les services non prévus, utiliser NULL au lieu de 0
id_fiche_insert = None if (not id_fiche_travail or id_fiche_travail == 0) else id_fiche_travail
```

Lors de l'INSERT, on utilise maintenant :
- `NULL` pour les services non prévus
- ID valide pour les services prévus

### 3. Logging Détaillé Ajouté

Pour faciliter le debugging, ajout de nombreux logs :

```python
# Vérification des types de dates
print(f"[DEBUG] dte_deb type: {type(dte_deb)}, value: {dte_deb}")
print(f"[DEBUG] dte_fin type: {type(dte_fin)}, value: {dte_fin}")

# Données à insérer
print(f"[DEBUG] Données à insérer:")
print(f"  - id_fiche_travail: {id_fiche_travail}")
print(f"  - numero_commande: {fiche_data[5]}")
print(f"  - nom_service: {fiche_data[14]}")

# Résultats SQL
print("[DEBUG] INSERT réussi")
print("[DEBUG] COMMIT réussi")

# Erreurs détaillées
print(f"[ERREUR] INSERT ou COMMIT échoué: {type(e).__name__}: {e}")
traceback.print_exc()
```

### 4. Gestion d'Erreurs Améliorée

**Try/Catch autour du calcul TpsReel** :
```python
try:
    duree_secondes = (dte_fin - dte_deb).total_seconds()
    tps_reel = duree_secondes / 3600.0
    print(f"[DEBUG] TpsReel calculé: {tps_reel:.3f}h")
except Exception as e:
    print(f"[ERREUR] Calcul TpsReel échoué: {e}")
    tps_reel = None
```

**Try/Catch autour de l'INSERT SQL** :
```python
try:
    cursor.execute("""INSERT INTO WEB_TRAITEMENTS ...""")
    print("[DEBUG] INSERT réussi")
    cursor.commit()
    print("[DEBUG] COMMIT réussi")
except Exception as e:
    print(f"[ERREUR] INSERT ou COMMIT échoué: {type(e).__name__}: {e}")
    traceback.print_exc()
    raise
```

## 📊 Flux de Débogage

Avec les nouveaux logs, voici ce que vous devriez voir dans la console du serveur Flask :

### Service Non Prévu - Flux Normal

```
[DEBUG API] Données reçues: {'id_fiche_travail': 0, 'numero_commande': '25-1234', ...}
[INFO API] Service non prévu détecté
[INFO API] Appel à create_traitement()
[DEBUG] Début create_traitement avec data: {...}
[DEBUG] id_fiche_travail: 0
[INFO] Service non prévu détecté - Traitement sans fiche de travail
[DEBUG] matricule reçu: 42, type: <class 'int'>
[DEBUG] Opérateur trouvé: DOE John
[DEBUG] dte_deb type: <class 'datetime.datetime'>, value: 2025-10-20 14:00:00
[DEBUG] dte_fin type: <class 'datetime.datetime'>, value: 2025-10-20 15:30:00
[DEBUG] TpsReel calculé à la création: 1.500h
[DEBUG] Données à insérer:
  - id_fiche_travail: 0
  - numero_commande: 25-1234
  - nom_service: FACONNAGE
  - nom_poste: 
  - postes_reel: Déchiqutage
[DEBUG] INSERT réussi
[DEBUG] COMMIT réussi
[SUCCESS API] Traitement créé avec ID: 12345
```

### Service Non Prévu - Avec Erreur

Si une erreur se produit, vous verrez quelque chose comme :

```
[DEBUG API] Données reçues: {...}
[INFO API] Service non prévu détecté
[INFO API] Appel à create_traitement()
[DEBUG] Début create_traitement avec data: {...}
[INFO] Service non prévu détecté - Traitement sans fiche de travail
Erreur: Commande 25-1234 non trouvée
```

Ou :

```
[DEBUG] dte_deb type: <class 'str'>, value: 2025-10-20T14:00:00
[DEBUG] dte_fin type: <class 'datetime.datetime'>, value: 2025-10-20 15:30:00
[ERREUR] Calcul TpsReel échoué: unsupported operand type(s) for -: 'datetime.datetime' and 'str'
```

Ou :

```
[DEBUG] Données à insérer: ...
[ERREUR] INSERT ou COMMIT échoué: ProgrammingError: ('42000', ...)
Traceback (most recent call last):
  ...
```

## 🧪 Test à Effectuer

### Étape 1 : Redémarrer le serveur Flask

**Important** : Redémarrez votre serveur Flask pour que les nouvelles modifications soient prises en compte :

```powershell
# Arrêter le serveur (Ctrl+C)
# Puis relancer
python app.py
```

### Étape 2 : Réessayer l'Enregistrement

1. Sélectionnez une commande
2. Choisissez "🔧 Autre service (non prévu)"
3. Sélectionnez un service (ex: FACONNAGE)
4. Sélectionnez une machine (ex: Déchiqutage)
5. Remplissez tous les champs
6. Cliquez sur "Arrêter et Enregistrer"

### Étape 3 : Observer les Logs

**Dans la console du serveur Flask**, vous devriez voir une LONGUE liste de logs commençant par `[DEBUG]`, `[INFO]`, ou `[ERREUR]`.

## 📝 Action Requise

**Si vous obtenez toujours une erreur 500**, veuillez :

1. **Copier TOUS les logs** de la console du serveur Flask (depuis `[DEBUG API] Données reçues:` jusqu'à la fin)
2. **Me les transmettre** pour que je puisse identifier l'erreur exacte

Les nouveaux logs devraient révéler précisément où le problème se situe :
- ❌ Conversion de date ?
- ❌ Récupération de la commande ?
- ❌ Calcul du TpsReel ?
- ❌ INSERT SQL ?
- ❌ Contrainte de la base de données ?

## 📂 Fichiers Modifiés

| Fichier | Lignes | Description |
|---------|--------|-------------|
| `logic/projet11.py` | 707-731 | Création classe `FicheDataVirtuelle` |
| `logic/projet11.py` | 824-835 | Logging dates + gestion erreur calcul |
| `logic/projet11.py` | 838-843 | Logging données à insérer |
| `logic/projet11.py` | 845-910 | Try/catch INSERT + logging détaillé |

## 🎯 Prochaines Étapes

1. ✅ Redémarrer le serveur Flask
2. ✅ Réessayer l'enregistrement d'un service non prévu
3. ✅ Observer les logs dans la console
4. ✅ Si erreur persiste, copier les logs et me les transmettre

**Les logs détaillés devraient maintenant nous dire EXACTEMENT ce qui ne va pas !** 🔍

---

💡 **Note** : Si l'erreur est liée à la structure de la table `WEB_TRAITEMENTS` (contraintes, types de colonnes, etc.), les logs SQL nous le diront clairement.


















