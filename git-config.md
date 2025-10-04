# Configuration Git pour le workspace Novaprint

## 🔐 Informations du compte Git configurées

### Utilisateur
- **Nom d'utilisateur** : AMENI-NOVA
- **Email** : ameni.nova@example.com

### Configuration globale
```bash
git config --global user.name "AMENI-NOVA"
git config --global user.email "ameni.nova@example.com"
git config --global credential.helper store
```

### Configuration locale (projet)
```bash
git config user.name "AMENI-NOVA"
git config user.email "ameni.nova@example.com"
```

## 🔑 Authentification GitHub

### Option 1 : Personal Access Token (Recommandé)
1. Allez sur GitHub → Settings → Developer settings → Personal access tokens
2. Créez un nouveau token avec les permissions :
   - `repo` (accès complet aux dépôts)
   - `workflow` (si vous utilisez GitHub Actions)
3. Utilisez le token comme mot de passe lors des opérations Git

### Option 2 : SSH Keys
```bash
# Générer une clé SSH
ssh-keygen -t ed25519 -C "ameni.nova@example.com"

# Ajouter la clé à ssh-agent
ssh-add ~/.ssh/id_ed25519

# Copier la clé publique
cat ~/.ssh/id_ed25519.pub
```
Puis ajoutez la clé publique dans GitHub → Settings → SSH and GPG keys

## 📁 Dépôt configuré
- **URL** : https://github.com/AMENI-NOVA/novaprint-website.git
- **Branches** : main, develop
- **Statut** : Connecté et synchronisé

## 🚀 Commandes utiles

### Vérifier la configuration
```bash
git config --list
git remote -v
git status
```

### Authentification automatique
```bash
# La première fois, Git demandera vos identifiants
git push origin develop

# Les identifiants seront sauvegardés automatiquement
```

### Changer de compte (si nécessaire)
```bash
git config --global --unset user.name
git config --global --unset user.email
git config --global --unset credential.helper
```

## ⚠️ Sécurité
- Ne partagez jamais votre Personal Access Token
- Utilisez des tokens avec des permissions minimales
- Régénérez régulièrement vos tokens
- Ne commitez jamais de fichiers de configuration avec des identifiants

## 📝 Notes
- Le workspace est configuré pour utiliser le compte AMENI-NOVA
- Tous les commits seront associés à ce compte
- L'authentification est configurée pour être persistante
