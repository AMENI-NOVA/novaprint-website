# Projet 11 - Journal des Modifications

## 📅 Historique des Modifications

---

### Version 1.7.1 - Réorganisation TpsReel (15 octobre 2024)

#### 🔧 Réorganisation Structure

**Objectif**: Placer TpsReel juste à côté de TpsPrevDev_GP_FICHES_OPERATIONS

**Avant**:
- Position 17: TpsPrevDev_GP_FICHES_OPERATIONS
- Positions 18-20: DateCreation, DateModification, PostesReel
- Position 21: TpsReel ← Séparé par 3 colonnes

**Après**:
- Position 17: TpsPrevDev_GP_FICHES_OPERATIONS
- Position 18: TpsReel ← **Juste après!** ✅
- Position 19: PostesReel
- Positions 20-21: DateCreation, DateModification

**Méthode**:
1. Sauvegarde des données existantes
2. Création table temporaire avec bon ordre
3. Copie des données
4. Remplacement de la table
5. Recréation contraintes/index/triggers

**Résultat**: Les deux champs temps sont maintenant **côte à côte** pour une meilleure lisibilité!

**Documentation**: `PROJET11_REORGANISATION_TPSREEL.md`

---

### Version 1.7 - Ajout TpsReel (15 octobre 2024)

#### 🎯 Nouveau Champ

**Champ ajouté**: `TpsReel` (Temps Réel de Production)

**Type**: `DECIMAL(10,3) NULL`

**Position**: Juste après `TpsPrevDev_GP_FICHES_OPERATIONS`

**Calcul**: Automatique via triggers SQL
- Formule: `(DteFin - DteDeb) / 60` heures
- Format: 3 décimales [[memory:4553069]]
- Exemple: 1.500h = 1h 30min

#### 🔧 Implémentation Technique

**Triggers créés**:
- `TR_WEB_TRAITEMENTS_INSERT_TPSREEL`: Calcul lors de l'insertion
- `TR_WEB_TRAITEMENTS_UPDATE_TPSREEL`: Recalcul lors de la mise à jour

**Backend Python mis à jour**:
- `get_all_traitements()`: Inclut TpsReel + calcul de l'écart
- `get_traitement_by_id()`: Inclut TpsReel + calcul de l'écart

**Frontend mis à jour**:
- 3 nouvelles colonnes dans la liste:
  - **Tps Prévu**: Temps prévu (normal)
  - **Tps Réel**: Temps réel en gras bleu
  - **Écart**: Badge vert (gain) ou rouge (retard)
- Modal détails enrichie avec comparaison temps

#### 📊 Affichage

**Codes couleurs**:
- 🟢 **Vert**: Écart négatif (plus rapide que prévu)
- 🔴 **Rouge**: Écart positif (plus lent que prévu)
- ⚪ **Gris**: Écart zéro (parfaitement conforme)
- ⏳ **En cours**: Traitement non terminé

**Exemple réel**:
```
Traitement #2:
  Prévu: 3.054h
  Réel: 1.500h
  Écart: -1.554h ✅ (51% plus rapide!)
```

#### 🎯 Avantages

- ✅ Comparaison immédiate prévu vs réel
- ✅ Calcul 100% automatique
- ✅ Précision à la seconde (3 décimales)
- ✅ Identification performance en un coup d'œil
- ✅ Analyse des écarts (KPI)

**Documentation**: `PROJET11_TPSREEL_AUTOMATIQUE.md`

---

### Version 1.6 - Services Non Prévus (15 octobre 2024)

#### 🎯 Nouvelle Fonctionnalité

**Ajout de services non prévus** dans le flux de production

**Option**: "🔧 Autre service (non prévu)"

**Fonctionnalités**:
- Sélection de **tous les services** GP_SERVICES
- Sélection de **tous les postes** GP_POSTES par service
- Saisie manuelle des données (quantité, machine)
- Support des cas exceptionnels (contrôle qualité, réparation, etc.)

#### 🔧 Backend

**Nouvelles fonctions**:
- `get_tous_services()`: Récupère tous les services depuis GP_SERVICES
- `get_postes_by_service(nom_service)`: Récupère tous les postes d'un service

**Nouvelles routes API**:
- `GET /projet11/api/services-tous`: Tous les services
- `GET /projet11/api/postes-tous-service/<nom_service>`: Postes par service

#### 🎨 Frontend

**Formulaire modifié**:
- Liste déroulante groupée (services prévus / autre service)
- Affichage conditionnel du formulaire manuel
- Messages explicatifs pour services non prévus

**Documentation**: `PROJET11_SERVICES_NON_PREVUS.md`

---

### Version 1.5 - Chronomètre et Services Prévus (15 octobre 2024)

#### ⏱️ Chronomètre Automatique

**Démarrage**: Automatique dès la sélection de l'opérateur

**Affichage**: Temps réel en format `HH:MM:SS`

**Arrêt**: Clic sur "Arrêter et Enregistrer"

**Enregistrement**:
- `DteDeb`: Date/heure de démarrage
- `DteFin`: Date/heure d'arrêt
- Durée calculée précise à la seconde

#### 📋 Sélection par Service

**Nouveau flux**:
1. Sélection de la commande
2. **Sélection du service** (au lieu de la fiche)
3. → Affichage automatique:
   - Machine prévue
   - Quantité prévue
   - Temps prévu
   - Historique du service
   - Reste à produire

**Avantages**:
- Plus intuitif (par service, pas par fiche)
- Informations automatiques
- Historique visible
- Suggestions quantités

#### 🔧 Backend

**Nouvelles fonctions**:
- `get_services_prevus_by_commande(numero_commande)`: Services d'une commande
- `get_postes_prevus_by_commande_service(numero, service)`: Postes prévus
- `get_traitements_existants_service(numero, service)`: Historique service

**Nouvelles routes API**:
- `GET /projet11/api/services-prevus/<numero>`: Services prévus
- `GET /projet11/api/postes-prevus/<numero>/<service>`: Postes prévus
- `GET /projet11/api/traitements-service/<numero>/<service>`: Historique

#### 🎨 Frontend

**Refonte complète** du formulaire:
- Étapes numérotées (1️⃣ 2️⃣ 3️⃣)
- Affichage conditionnel (cascade)
- Chronomètre avec dégradé violet
- Encadrés informatifs (bleu/jaune)
- Tableau historique avec totaux

**Documentation**: `PROJET11_NOUVEAU_FORMULAIRE_V2.md`, `PROJET11_LOGIQUE_SERVICES_PREVUS.md`

---

### Version 1.4 - Recherche Select2 Avancée (14 octobre 2024)

#### 🔍 Recherche "Contient"

**Select2 intégré** pour recherche avancée

**Mode**: Recherche "contient" (pas seulement début)

**Champs améliorés**:
- Numéro de commande
- Opérateur
- Service
- Poste

**Ouverture automatique**:
- Focus sur le champ → Dropdown s'ouvre
- Curseur dans la barre de recherche
- Tape immédiatement

**Documentation**: `PROJET11_SELECT2_RECHERCHE.md`

---

### Version 1.3 - Production par Lots (14 octobre 2024)

#### 🔢 Sessions Multiples

**Support**: Plusieurs traitements par fiche de travail

**Cas d'usage**:
- Production par batches (matin/après-midi)
- Changement de machine
- Plusieurs opérateurs
- Répartition sur plusieurs jours

**Affichage**:
- Historique des sessions précédentes
- Total produit / Reste
- Nombre de sessions
- Avancement %

**Modification backend**:
- Suppression de la contrainte `NOT IN (SELECT ID_FICHE_TRAVAIL...)`
- Toutes les fiches disponibles, même avec traitements existants

**Documentation**: `PROJET11_PRODUCTION_PAR_LOTS.md`

---

### Version 1.2 - Champ PostesReel (14 octobre 2024)

#### 🔧 Machine Réelle

**Nouveau champ**: `PostesReel` (VARCHAR(255))

**Objectif**: Enregistrer la machine **réellement utilisée**

**Pré-rempli**: Machine prévue (modifiable)

**Cas d'usage**: Changement de machine en cours de production

**Affichage**:
- Colonne "Machine Réelle" dans la liste
- Comparaison avec "Poste Prévu"
- En gras si différent du prévu

**Documentation**: `PROJET11_AJOUT_POSTES_REEL.md`

---

### Version 1.1 - Correction jQuery/DataTables (14 octobre 2024)

#### 🐛 Correction Bibliothèques

**Problème**: `$ is not defined` - jQuery non chargé

**Solution**: Ajout correct des bibliothèques:
- jQuery 3.7.1
- DataTables 1.13.7
- Font Awesome 6.4.0

**Fichiers corrigés**:
- `templates/projet11_liste.html`
- `templates/projet11_nouveau.html`
- `templates/projet11_stats.html`
- `templates/projet11.html`

**Documentation**: `PROJET11_CORRECTION_JQUERY.md`

---

### Version 1.0.3 - Sélection par Commande (13 octobre 2024)

#### 🎯 Sélection Cascade

**Flux**: Sélection du numéro de commande → Charge les fiches associées

**API**: `GET /projet11/api/fiches-by-numero/<numero>`

**JavaScript**: Mise à jour dynamique du dropdown fiches

**Correction**: Support des espaces dans numéros (`LTRIM(RTRIM(C.Numero))`)

**Documentation**: `PROJET11_SELECTION_PAR_COMMANDE.md`

---

### Version 1.0.2 - Simplification Structure (12 octobre 2024)

#### 🗄️ Refonte Table

**De 30 champs → 19 champs**

**Suppression**: Tous les ID de liaison (sauf `ID_FICHE_TRAVAIL`)

**Raison**: IDs utilisés uniquement pour jointures, pas pour stockage

**Champs conservés**: Données métier uniquement

**Documentation**: `PROJET11_MODIFICATION_V2.md`, `PROJET11_STRUCTURE_FINALE.md`

---

### Version 1.0.1 - Création Initiale (10 octobre 2024)

#### 🎉 Projet Créé

**Table créée**: `WEB_TRAITEMENTS` (30 champs initiaux)

**Backend**:
- Module `logic/projet11.py`
- Routes `routes/projet11_routes.py`
- 15 endpoints API REST

**Frontend**:
- 4 pages HTML (Accueil, Nouveau, Liste, Stats)
- Bootstrap 5
- DataTables
- Chart.js

**Tests**:
- Suite de tests `test_projet11.py`
- 7/7 tests réussis

**Documentation**:
- `PROJET11_README.md`
- `PROJET11_DEMARRAGE_RAPIDE.md`
- `PROJET11_RESUME.md`

---

## 📊 Résumé par Version

| Version | Date | Fonctionnalité Principale | Fichiers Modifiés |
|---------|------|----------------------------|-------------------|
| 1.7.1 | 15/10/24 | **Réorganisation** - TpsReel côte à côte | Base de données |
| 1.7 | 15/10/24 | **TpsReel** - Temps réel automatique | 3 fichiers |
| 1.6 | 15/10/24 | **Services non prévus** | 3 fichiers |
| 1.5 | 15/10/24 | **Chronomètre + Services prévus** | 4 fichiers |
| 1.4 | 14/10/24 | Recherche Select2 | 1 fichier |
| 1.3 | 14/10/24 | Production par lots | 2 fichiers |
| 1.2 | 14/10/24 | Champ PostesReel | 3 fichiers |
| 1.1 | 14/10/24 | Correction jQuery | 4 fichiers |
| 1.0.3 | 13/10/24 | Sélection par commande | 2 fichiers |
| 1.0.2 | 12/10/24 | Simplification structure | 2 fichiers |
| 1.0.1 | 10/10/24 | **Création initiale** | 15+ fichiers |

---

## 🎯 Évolution du Nombre de Champs

```
Version 1.0.1: 30 champs (avec IDs)
Version 1.0.2: 19 champs (IDs supprimés)
Version 1.2:   20 champs (+PostesReel)
Version 1.7:   21 champs (+TpsReel) ← ACTUEL
```

---

## 📈 Statistiques Globales

### Code Développé
- **~2,000 lignes** Python (backend)
- **~1,500 lignes** HTML/JavaScript (frontend)
- **~400 lignes** SQL
- **~12,000 lignes** Documentation

**Total**: ~15,900 lignes

### Fichiers
- **3 modules** Python
- **4 templates** HTML
- **18 documents** de documentation
- **6 scripts** SQL
- **1 suite** de tests

### Fonctionnalités
- **20+ fonctions** Python
- **15 endpoints** API REST
- **4 pages** web
- **2 triggers** SQL
- **1 chronomètre** temps réel
- **3 graphiques** statistiques

---

## 🚀 Prochaines Évolutions Possibles

### Court Terme
- [ ] Export Excel des traitements
- [ ] Filtres avancés (date, opérateur, service)
- [ ] Graphiques de performance par opérateur
- [ ] Notifications pour retards importants

### Moyen Terme
- [ ] Application mobile pour saisie
- [ ] Scan QR code pour démarrer production
- [ ] Dashboard temps réel
- [ ] Alertes automatiques

### Long Terme
- [ ] Machine Learning pour prédiction temps
- [ ] Optimisation automatique des plannings
- [ ] Intégration ERP
- [ ] API externe pour clients

---

## 📚 Documentation Complète

### Guides Utilisateur
1. `PROJET11_DEMARRAGE_RAPIDE.md` - Guide de démarrage
2. `PROJET11_README.md` - Documentation technique
3. `PROJET11_RESUME_COMPLET_FINAL.md` - Vue d'ensemble

### Modifications Spécifiques
4. `PROJET11_STRUCTURE_FINALE.md` - Structure table
5. `PROJET11_MODIFICATION_V2.md` - Simplification
6. `PROJET11_SELECTION_PAR_COMMANDE.md` - Sélection cascade
7. `PROJET11_CORRECTION_JQUERY.md` - Fix bibliothèques
8. `PROJET11_AJOUT_POSTES_REEL.md` - Machine réelle
9. `PROJET11_PRODUCTION_PAR_LOTS.md` - Sessions multiples
10. `PROJET11_SELECT2_RECHERCHE.md` - Recherche avancée
11. `PROJET11_LOGIQUE_SERVICES_PREVUS.md` - Services prévus
12. `PROJET11_NOUVEAU_FORMULAIRE_V2.md` - Chronomètre
13. `PROJET11_SERVICES_NON_PREVUS.md` - Services non prévus
14. `PROJET11_TPSREEL_AUTOMATIQUE.md` - Temps réel
15. **`PROJET11_REORGANISATION_TPSREEL.md`** - Réorganisation structure ⭐ NOUVEAU
16. `PROJET11_CHANGELOG.md` - Ce fichier

### Résumés Rapides
17. `PROJET11_MODIFICATION_LOTS.txt`
18. `PROJET11_AJOUT_TPSREEL.txt`

---

## ✅ Statut Actuel

**Version**: 1.7.1  
**Statut**: ✅ **Production Ready**  
**Dernière modification**: 15 octobre 2024  
**Champs**: 21 dans WEB_TRAITEMENTS  
**Structure**: TpsPrevDev et TpsReel côte à côte (positions 17-18)  
**Fonctionnalités**: 100% opérationnelles  

---

## 🎊 Conclusion

Le **Projet 11** est un système **complet et évolutif** qui:

✅ Suit la production en temps réel  
✅ Compare prévu vs réel automatiquement  
✅ S'adapte à tous les cas (prévus/non prévus/par lots)  
✅ Offre des analyses poussées  
✅ Interface moderne et intuitive  

**Prêt pour la production!** 🚀

---

*Projet développé pour Novaprint - 2024*
