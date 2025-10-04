# Site Web Novaprint

Application web Flask pour la gestion des projets d'impression avec intégration Crystal Reports.

## 🚀 Fonctionnalités

- **Gestion des projets** : 10 projets différents avec des fonctionnalités spécialisées
- **Base de données** : Intégration SQL Server avec connexion sécurisée
- **Rapports** : Génération de rapports avec Crystal Reports
- **Interface web** : Interface utilisateur moderne avec Flask et templates HTML
- **Gestion des voyages** : Système de suivi des livraisons et expéditions
- **Contrôle qualité** : Outils de backup et restauration des données

## 🛠️ Technologies utilisées

- **Backend** : Python Flask
- **Base de données** : SQL Server
- **Rapports** : Crystal Reports
- **Frontend** : HTML, CSS, JavaScript
- **Authentification** : SQL Server Trusted Connection

## 📁 Structure du projet

```
├── app.py                 # Application Flask principale
├── db.py                  # Configuration et gestion de la base de données
├── requirements.txt       # Dépendances Python
├── logic/                 # Logique métier des projets
│   ├── projet1.py
│   ├── projet2.py
│   └── ...
├── routes/                # Routes Flask
├── templates/             # Templates HTML
├── static/                # Fichiers statiques (CSS, images)
├── crystalreport/         # Fichiers Crystal Reports
└── uploads/               # Fichiers uploadés
```

## 🔧 Installation

1. **Cloner le dépôt**
   ```bash
   git clone https://github.com/AMENI-NOVA/novaprint-website.git
   cd novaprint-website
   ```

2. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configuration de la base de données**
   - Modifier `db.py` avec vos paramètres SQL Server
   - Créer la base de données `novaprint_restored`

4. **Lancer l'application**
   ```bash
   python app.py
   ```

## 📊 Projets disponibles

- **Projet 1** : Gestion des commandes
- **Projet 2** : Suivi des devis
- **Projet 3** : Gestion des clients
- **Projet 4** : Planification des productions
- **Projet 5** : Contrôle qualité
- **Projet 6** : Gestion des voyages
- **Projet 7** : Statistiques avancées
- **Projet 8** : Rapports personnalisés
- **Projet 9** : Analyses de performance
- **Projet 10** : Tableau de bord

## 🔐 Configuration

### Base de données
```python
DB_CONFIG = {
    "DRIVER": "{SQL Server}",
    "SERVER": "VOTRE_SERVEUR",
    "DATABASE": "novaprint_restored",
    "Trusted_Connection": "yes",
    "TrustServerCertificate": "yes"
}
```

### Variables d'environnement
Créez un fichier `.env` :
```
FLASK_ENV=development
SECRET_KEY=votre_cle_secrete
DATABASE_URL=votre_url_base_donnees
```

## 🚀 Déploiement

### Production
```bash
# Installer Gunicorn
pip install gunicorn

# Lancer en production
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

### Docker (optionnel)
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

## 📝 Utilisation

1. **Accéder à l'application** : http://localhost:5000
2. **Navigation** : Utilisez le menu pour accéder aux différents projets
3. **Rapports** : Générez des rapports via l'interface Crystal Reports
4. **Données** : Consultez et modifiez les données via les formulaires

## 🤝 Contribution

1. Fork le projet
2. Créer une branche feature (`git checkout -b feature/nouvelle-fonctionnalite`)
3. Commit les changements (`git commit -m 'Ajouter nouvelle fonctionnalité'`)
4. Push vers la branche (`git push origin feature/nouvelle-fonctionnalite`)
5. Ouvrir une Pull Request

## 📄 Licence

Ce projet est sous licence privée pour Novaprint.

## 📞 Support

Pour toute question ou support, contactez l'équipe de développement Novaprint.

---

**Développé avec ❤️ par l'équipe Novaprint**
