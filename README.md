# 🏢 Système Multi-Tenant pour Restaurant Management

## 📖 Vue d'ensemble

Ce système transforme votre workflow n8n de gestion de restaurant en une **plateforme multi-tenant sécurisée** permettant de gérer plusieurs restaurants indépendamment avec :

- ✅ **Isolation complète des données** par restaurant
- ✅ **Gestion d'erreurs robuste** avec logs détaillés
- ✅ **Authentification par API Key**
- ✅ **Monitoring et analytics** en temps réel
- ✅ **Sécurité renforcée** et audit trail

---

## 🚀 Démarrage Rapide

### Installation en 5 étapes

#### 1️⃣ Préparer Airtable (1h)
- Créer table "API Logs"
- Ajouter champ "Restaurant" à toutes les tables
- Créer 2 restaurants de test

#### 2️⃣ Modifier le workflow n8n (2h)
- Ajouter "Global Error Handler"
- Modifier filtres Airtable
- Ajouter gestion d'erreurs

#### 3️⃣ Copier les codes (30min)
- Utiliser `node-codes-ready-to-use.md`
- Copier-coller dans n8n

#### 4️⃣ Tester (1h)
- Utiliser `test-scripts.md`
- Valider l'isolation

#### 5️⃣ Mettre en production (30min)
- Activer le workflow
- Configurer le monitoring

---

## 📁 Fichiers disponibles

| Fichier | Description | Usage |
|---------|-------------|-------|
| **MIGRATION_GUIDE.md** | Guide complet étape par étape | Pendant la migration |
| **airtable-setup.md** | Configuration Airtable | Avant de commencer |
| **node-codes-ready-to-use.md** | Codes à copier-coller | Implémentation |
| **test-scripts.md** | Tests et validation | Après migration |
| **multi-tenant-error-handler.js** | Bibliothèque JS | Pour développeurs |

---

## 🏗️ Architecture Simplifiée

```
Frontend (API Key) → Webhook → Auth → Router IA → Branches métier → Airtable
                                           ↓
                                     Error Handler
                                           ↓
                                      Logs (Airtable)
```

---

## 📊 Fonctionnalités Multi-Tenant

- ✅ Isolation complète des données par restaurant
- ✅ API Key unique par restaurant
- ✅ Logs séparés et traçables
- ✅ Gestion d'erreurs standardisée
- ✅ Monitoring en temps réel

---

## 🔐 Sécurité

Chaque requête Airtable est automatiquement filtrée :

```javascript
filterByFormula: "={Restaurant} = '{{ $('Global Error Handler').item.json.restaurant_id }}'"
```

**Garantit** : Restaurant A ne peut JAMAIS voir les données de Restaurant B

---

## 🚀 Prêt à démarrer ?

1. Ouvrez `MIGRATION_GUIDE.md`
2. Suivez les étapes
3. Testez avec `test-scripts.md`
4. Déployez ! 🎉

---

**Version** : 1.0.0
**Status** : ✅ Production Ready
