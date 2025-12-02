# Projet 11 - Correction du Décalage Horaire

## 📅 Date de correction
20 octobre 2025

## 🔍 Problème Identifié

### Symptômes
Les heures de début (`DteDeb`) et de fin (`DteFin`) enregistrées dans la base de données ne correspondaient pas aux heures affichées sur le PC de l'utilisateur. Un décalage d'environ **1 heure** était observé.

### Cause Racine
Le système capturait l'heure locale du navigateur mais la **convertissait en UTC** avant de l'enregistrer :
- Le navigateur utilisait `new Date().toISOString()` qui convertit automatiquement en UTC
- En France : UTC+1 (hiver) ou UTC+2 (été)
- **Exemple** : Si le PC affichait 14h00, le système enregistrait 13h00 (UTC)

### Diagnostic Technique

#### Avant la correction :
```javascript
// JavaScript (client)
chronoStart = new Date();              // 14:00:00 (heure locale)
$('#dte_deb').val(chronoStart.toISOString());  // "2025-10-20T13:00:00.000Z" (UTC)
```

```python
# Python (serveur)
data['dte_deb'] = datetime.fromisoformat(data['dte_deb'].replace('Z', '+00:00'))
# Enregistre: 13:00:00 en base
```

```python
# Affichage
"dte_deb": row.DteDeb.strftime('%Y-%m-%d %H:%M:%S')
# Affiche: 13:00:00 (alors que l'utilisateur avait vu 14:00:00)
```

## ✅ Solution Implémentée

### Option Choisie : Enregistrer l'Heure Locale
Plutôt que de convertir en UTC, le système enregistre maintenant directement **l'heure locale du navigateur**.

### Avantages
- ✅ Simplicité : pas de conversion timezone
- ✅ Cohérence : l'heure enregistrée = l'heure affichée
- ✅ Adapté : l'application est utilisée dans un seul fuseau horaire

## 🔧 Modifications Apportées

### 1. Frontend (`templates/projet11_nouveau.html`)

#### Nouvelle fonction `formatDateTimeLocal()`
```javascript
/**
 * Formate une date en heure locale pour SQL Server (sans conversion UTC)
 * Format: YYYY-MM-DDTHH:MM:SS (sans le 'Z' qui indique UTC)
 */
function formatDateTimeLocal(date) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    const seconds = String(date.getSeconds()).padStart(2, '0');
    
    return `${year}-${month}-${day}T${hours}:${minutes}:${seconds}`;
}
```

#### Modification de `demarrerChrono()`
```javascript
// AVANT
$('#dte_deb').val(chronoStart.toISOString());  // UTC

// APRÈS
$('#dte_deb').val(formatDateTimeLocal(chronoStart));  // Heure locale
```

#### Modification de la soumission du formulaire
```javascript
// AVANT
$('#dte_fin').val(now.toISOString());  // UTC

// APRÈS  
$('#dte_fin').val(formatDateTimeLocal(now));  // Heure locale
```

### 2. Backend (`routes/projet11_routes.py`)

#### Fonction `api_create_traitement()`
```python
# AVANT
data['dte_deb'] = datetime.fromisoformat(data['dte_deb'].replace('Z', '+00:00'))

# APRÈS
if 'T' in data['dte_deb']:
    date_str = data['dte_deb'].replace('Z', '')  # Enlever le Z si présent
    if '.' in date_str:
        # Avec millisecondes: 2025-10-20T14:30:00.123
        data['dte_deb'] = datetime.strptime(date_str.split('.')[0], '%Y-%m-%dT%H:%M:%S')
    else:
        # Sans millisecondes: 2025-10-20T14:30:00
        data['dte_deb'] = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S')
```

#### Fonction `api_update_traitement()`
Même logique appliquée pour la mise à jour des traitements.

### 3. Logique Métier (`logic/projet11.py`)

#### Fonction `update_traitement()`
```python
# AVANT
if isinstance(dte_deb, str):
    dte_deb = datetime.fromisoformat(dte_deb.replace('Z', '+00:00'))

# APRÈS
if isinstance(dte_deb, str):
    date_str = dte_deb.replace('Z', '')
    if '.' in date_str:
        dte_deb = datetime.strptime(date_str.split('.')[0], '%Y-%m-%dT%H:%M:%S')
    else:
        dte_deb = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S')
```

## 📊 Format des Dates

### Format Envoyé (JavaScript → Python)
```
2025-10-20T14:30:00
```
- **Pas de 'Z'** à la fin (qui indiquerait UTC)
- Représente l'**heure locale** du PC de l'utilisateur

### Format Stocké (Base de Données)
```sql
DteDeb: 2025-10-20 14:30:00
DteFin: 2025-10-20 15:45:00
```
- Type SQL Server : `datetime`
- Pas de timezone (SQL Server standard)
- Représente l'**heure locale**

### Format Affiché (Python → HTML)
```python
row.DteDeb.strftime('%Y-%m-%d %H:%M:%S')
# Résultat: "2025-10-20 14:30:00"
```
- L'heure affichée correspond à l'heure capturée

## 🧪 Test de Validation

### Scénario de test
1. L'utilisateur commence un traitement à **14h00** (selon son PC)
2. L'utilisateur termine le traitement à **15h30** (selon son PC)
3. Le système enregistre :
   - `DteDeb` = 2025-10-20 **14:00:00** ✅
   - `DteFin` = 2025-10-20 **15:30:00** ✅
   - `TpsReel` = **1.500 h** ✅

### Validation
- ✅ L'heure de début affichée = heure du PC au démarrage
- ✅ L'heure de fin affichée = heure du PC à l'arrêt
- ✅ Le temps calculé est correct (1h30)
- ✅ Aucun décalage horaire

## 📝 Notes Importantes

### Rétrocompatibilité
Le code gère toujours l'ancien format avec 'Z' (UTC) :
```python
date_str = data['dte_deb'].replace('Z', '')  # Enlève le Z s'il existe
```

### Multi-timezone
⚠️ **Limitation** : Si l'application devait être utilisée dans plusieurs fuseaux horaires différents, il faudrait :
- Enregistrer en UTC
- Stocker le timezone de l'utilisateur
- Convertir lors de l'affichage

Actuellement, l'application suppose que tous les utilisateurs sont dans le **même fuseau horaire**.

## 📂 Fichiers Modifiés

| Fichier | Lignes modifiées | Description |
|---------|------------------|-------------|
| `templates/projet11_nouveau.html` | 844-857, 864, 933 | Ajout `formatDateTimeLocal()`, modification capture heures |
| `routes/projet11_routes.py` | 84-119, 143-169 | Parsing dates locales (create & update) |
| `logic/projet11.py` | 869-893 | Parsing dates locales (calcul TpsReel) |

## ✅ Résultat Final

**AVANT** : Heure PC = 14h00 → Base de données = 13h00 ❌  
**APRÈS** : Heure PC = 14h00 → Base de données = 14h00 ✅

Le décalage horaire a été **corrigé avec succès** ! 🎉





















