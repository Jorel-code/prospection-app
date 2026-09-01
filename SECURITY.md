# Politique de sécurité

## Gestion des secrets
Toutes les clés API, identifiants SMTP et jetons d'accès sont stockés
exclusivement dans des variables d'environnement (`.env`, jamais commité).
Voir `.env.example` pour la liste des variables attendues.

## Authentification
- Mots de passe hachés avec Argon2 (jamais stockés en clair).
- Sessions gérées par JWT, expiration après 24h.

## Protections en place
- Rate-limiting (Flask-Limiter) sur toutes les routes, renforcé sur
  l'authentification et les routes consommant l'IA/l'envoi.
- En-têtes de sécurité automatiques (Flask-Talisman).
- CORS restreint à l'origine du frontend autorisé.
- Scan de sécurité automatique du code (Bandit) à chaque push via CI.
- Dépendances surveillées automatiquement (Dependabot).

## Signaler une faille
En cas de découverte d'une vulnérabilité, contacter jorelbrayan02@gmail.com avant
toute divulgation publique.
