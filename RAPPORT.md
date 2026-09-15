# Rendu — Challenge backend Django (repositories)

## 1. Compréhension du sujet

Le sujet demande une application **back-end uniquement**, en Python / Django, pour gérer un inventaire de repositories de code. Il ne s’agit pas d’héberger du git : il s’agit de **déclarer** des repositories, d’y rattacher des fichiers avec des métadonnées, de les **rechercher**, et de **signaler** les fichiers à risque opérationnel (gros fichiers, configuration, sécurité, documentation manquante).

Les livrables attendus sont un projet exécutable, des modèles cohérents, des routes/API, une logique métier lisible, une base exploitable (SQLite acceptée), des tests, une documentation d’installation, et des exemples de requêtes. Le rendu suit cette ossature en 13 parties. Une distinction claire est faite entre l’aide d’une IA et le travail de relecture / compréhension (sections 11 et 12).

## 2. Choix techniques

- **Python 3** et **Django 5.1** : cadre demandé, ORM, migrations, tests intégrés.
- **Django REST Framework** : API JSON, pagination, filtres, interface browsable utile pour tester sans front-end.
- **django-filter** : recherche par nom (contient), langage et type.
- **SQLite** : zéro service externe, adapté à un challenge local.
- **Logique métier hors des vues** (`repositories/services.py`) : les règles « fichier critique » restent testables sans HTTP.
- **Pas d’authentification** : hors sujet ; l’API est ouverte en local (`DEBUG=True`).

## 3. Architecture du projet Django

- `config/` : projet Django (`settings`, `urls`, WSGI/ASGI).
- `repositories/` : unique application métier.
- `manage.py` : point d’entrée des commandes.
- `requirements.txt` : dépendances figées.
- Commande `seed_demo` : jeu de données pour tester rapidement.

Flux : HTTP → ViewSet DRF → Serializer / Filter → Model ORM → SQLite. Les flags critiques sont calculés à la lecture par `assess_file()`, pas stockés en base, pour rester alignés avec les règles courantes (seuil de taille, etc.).

## 4. Modèles de données

**Repository**

- `name` (unique), `description`, `owner`
- `created_at`, `updated_at`

**RepositoryFile**

- lien `ForeignKey` vers `Repository` (`related_name="files"`, suppression en cascade)
- `name`, `path`, `file_type`, `language`, `size_bytes`, `description`, `added_at`
- contrainte d’unicité `(repository, path)` : un même chemin ne peut pas être déclaré deux fois dans un repository

`file_type` est un choix : `source`, `config`, `security`, `documentation`, `other`.

## 5. Routes, vues ou API développées

Toutes les routes sont préfixées par `/api/` :

- `POST /api/repositories/` — création
- `GET /api/repositories/` — liste (compteurs de fichiers / fichiers critiques)
- `GET /api/repositories/{id}/` — détail + fichiers
- `GET|POST /api/repositories/{id}/files/` — liste ou ajout de fichiers
- `GET /api/files/` — recherche (`name`, `language`, `type` ou `file_type`, `repository`)
- `GET /api/files/critical/` — sous-ensemble des fichiers critiques
- `GET /api/files/{id}/` — détail d’un fichier

Les ViewSets DRF couvrent aussi PUT/PATCH/DELETE sur un repository (utile en admin API, non exigé explicitement).

## 6. Logique métier mise en place

- Un repository est un conteneur nommé, unique, avec un propriétaire.
- Un fichier appartient à un seul repository et porte des métadonnées d’inventaire (pas le contenu binaire du fichier).
- La recherche combine filtres exacts / insensibles à la casse (langage, type) et un filtre « contient » sur le nom.
- Les compteurs `files_count` et `critical_files_count` sont exposés à la liste et au détail pour un usage opérations (prioriser les repos à risque).
- Les règles critiques sont centralisées dans `assess_file()` afin d’éviter de dupliquer des `if` dans les vues.

## 7. Gestion des fichiers critiques

Un fichier est critique s’il vérifie **au moins un** critère :

1. taille ≥ `CRITICAL_FILE_SIZE_BYTES` (100 000 octets, réglable dans `config/settings.py`) ;
2. type `config`, ou nom/chemin contenant des indices (`settings`, `.env`, `docker-compose`, etc.) ;
3. type `security`, ou nom/chemin contenant des indices (`secret`, `id_rsa`, `.pem`, `token`, etc.) ;
4. `description` vide ou uniquement des espaces.

La réponse JSON inclut `is_critical` (booléen) et `critical_reasons` (liste de motifs). L’endpoint `/api/files/critical/` filtre côté serveur.

Limite volontaire : ce n’est **pas** une analyse de contenu (pas de scan de secrets dans le fichier). Seules les métadonnées déclarées sont utilisées.

## 8. Tests réalisés

Deux modules :

- `repositories/tests/test_services.py` : règles critiques (taille, config, sécurité, description manquante, fichier source « sain »).
- `repositories/tests/test_api.py` : création / liste / détail, ajout de fichier, recherche par nom / langage / type, endpoint critique.

Lancement : `python manage.py test repositories`.

## 9. Documentation d’installation et d’utilisation

Voir `README.md` : venv, `pip install`, `migrate`, `seed_demo`, `runserver`, tableau des endpoints, exemples `curl`.

## 10. Difficultés rencontrées

- **Périmètre « repository de code »** : le sujet peut être lu comme un mini-Git. Le choix retenu est un **inventaire de métadonnées**, plus réaliste sans front-end ni stockage d’objets.
- **Fichiers critiques** : les critères du sujet sont ouverts (« etc. »). Ils ont été rendus **explicites, configurables et testés**, plutôt que laissés implicites.
- **Compteurs critiques** : calculer `is_critical` en base aurait figé les règles. Le calcul à la volée est plus juste, au prix d’une itération Python acceptable à petite échelle.
- **Windows** : commandes d’installation documentées pour PowerShell ; `curl` Windows accepte `^` pour continuer une ligne.

## 11. Ce que j’ai fait avec l’aide de l’IA

J’ai utilisé **iA**  comme assistant de développement, pas comme substitut à la compréhension du sujet.

L’IA a produit la majeure partie du code et d’une première documentation :

- l’ossature Django (`config/`, application `repositories/`, `requirements.txt`, `.gitignore`) ;
- les modèles `Repository` / `RepositoryFile`, les serializers, ViewSets DRF, filtres et la fonction `assess_file` ;
- les tests (`test_services.py`, `test_api.py`) et la commande `seed_demo` ;
- une première version du `README.md` et de ce rapport, calée sur l’ossature en 13 parties.

Lors d’un second échange, j’ai demandé à l’IA de **comparer le projet au cahier des charges** (périmètre, API, tests, structure du rendu, distinction IA / travail personnel). Elle a confirmé que le back-end était conforme, a signalé que la section 12 d’origine était trop vague (formulation du type « ou je dois avant envoi »), et a proposé une réécriture de ces deux sections.

**Limites de cette aide :** le code généré n’est pas une garantie de qualité ; il faut le relire. `SECRET_KEY` et `DEBUG=True` sont du développement local, pas de la production. Il n’y a pas d’authentification. Les règles « fichier critique » sont des heuristiques sur métadonnées (faux positifs / faux négatifs possibles). L’application n’héberge pas le contenu binaire des fichiers. L’IA ne passe pas un oral à ma place : si je ne sais pas expliquer un endpoint ou un critère, ce n’est pas assimilé.

## 12. Ce qui relève de mon travail personnel

Le code n’est pas « écrit à la main ligne à ligne ». Mon travail, c’est le **cadrage**, la **relecture** et la **responsabilité du rendu**.

Concrètement :

- **Compréhension du sujet.** J’ai lu le cahier : back-end Django uniquement, gestion de repositories, fichiers et métadonnées, recherche, fichiers critiques, tests, documentation, ossature 13 points, mention obligatoire de l’IA. J’ai écarté l’idée d’un clone de GitHub / d’un dépôt git réel : le besoin est un **inventaire déclaratif** accessible par API.
- **Validation des choix techniques.** J’ai retenu (et assume) Python + Django + DRF + SQLite, parce que c’est ce que le sujet autorise / recommande, et que ça reste exécutable sans service externe. J’ai accepté de mettre les règles critiques dans `services.py` plutôt que dans les vues, pour pouvoir les tester hors HTTP.
- **Contrôle de conformité.** J’ai fait vérifier le projet contre le cahier (fonctionnalités, absence de front-end métier, migrations, tests, README, exemples de requêtes, structure du rapport). J’ai corrigé le point faible identifié : ces sections 11 et 12, qui doivent dire clairement ce qui vient de l’IA et ce qui vient de moi.
- **Ce que je dois pouvoir expliquer.** La relation Repository → fichiers ; les champs demandés (nom, chemin, type, langage, taille, date d’ajout) ; la recherche `name` / `language` / `type` ; les quatre critères critiques (taille, config, sécurité, description vide) ; le fait que `is_critical` n’est pas stocké en base mais calculé à la lecture.

Je n’attribue pas à « mon travail personnel » la génération initiale des fichiers Python : elle a été faite avec l’IA. Sans relecture du sujet, sans choix assumés, et sans distinction honnête ici, le rendu ne serait qu’un projet généré — ce que le cahier refuse.

## 13. Conclusion et pistes d’amélioration

Le projet couvre le cahier des charges : CRUD repositories, fichiers et métadonnées, recherche, fichiers critiques, tests, documentation, exemples. Pistes si le temps le permettait :

- authentification (token) et permissions par propriétaire ;
- stocker le contenu ou un hash du fichier, avec scan de secrets ;
- annoter `is_critical` en base (champ dénormalisé) pour de gros volumes ;
- OpenAPI (`drf-spectacular`) ;
- PostgreSQL et Docker Compose pour un déploiement plus proche de la prod.
