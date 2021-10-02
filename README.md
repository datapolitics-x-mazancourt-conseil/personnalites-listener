# Bienvue sur l'exemple de projet Analytics

## Introduction

Un projet Analytics est un projet qui vise à réaliser une analyse de données ou un tableau de bord sur un sujet spécifique. Il y a un projet Analytics par périmètre d'analyse.

Chaque projet analytics est packagé dans un conteneur Docker qui lui est propre.

Ce conteneur gère les 3 étapes de ce pipeline simplifié : 

- Extract : Télécharger les données depuis les sources 

- Transform : Préparer les données pour l'analyse

- Analyse : Analyser les données et générer les graphiques

Si une planification est prévue (ex : rafraichissement périodique des analyses), elle est également gérée par ce même conteneur

## Pré-requis

Pour mettre en place un projet analytics, il est nécessaire d'avoir un environnement plateforme fonctionnel (voir dépôt datapolitics-platform)


## Installation 

### Etape 1 : effectuer une copie de ce repository 

Dans le dossier local de votre choix, exécuter :

*git clone https://{USER_NAME_BITBUCKET}@bitbucket.org/antoine-datapolitics/sample-analytics-app.git*

*renommer le dossier avec le nom souhaité (analytics-X, où X est le sujet de l'analyse*

*supprimer le dosser .git pour effacer l'historique*

*exécuter git init pour réinitialiser un dépôt git*

*créer un dépôt bitbucket destiné dédié à ce projet*

*Pousser le projet sur ce nouveau respo*

### Etape 2 : ouvrir le dossier local dans le conteneur sous Visual Studio

*Ouvrir Visual Studio*

*Sélectionner la commande 'Open Folder In Container', puis le dossier analytics-X*

*Laisser docker démarrer l'ensemble des composants*

*Assurez vous que l'interpréteur sélectionné est bien /usr/local/bin/python3.9*

*Lancez la commande `python analyse.py` et vérifiez que vous avez bien généré un nouveau graphique visible dans la plateforme

## check-list création d'une analyse

### S'enquérir de la taille des données

Dans le cas par défaut, on part du principe que les données sont de taille petite (de l'ordre de quelques dizaines de MO maximum). Les données sont alors stockées directement dans le conteneur.

2 cas peuvent justifier un fonctionnement différent : 

1) Si les données sont de tailles plus importante, il faut les stocker ailleurs (ex : Buckets Google Storage)

2) Si les données sont récupérées mais pas disponibles en ligne de manière pérenne, il faudra également les stocker (ex : Buckets Google Storage)

Sujet à réouvrir quand nous rencontrerons le problème.

### Faire l'analyse

- compléter extract.py : script qui télécharge les données depuis les sources 

- compléter transform.py : script qui transforme et prépare les données pour l'analyse

- compéter analyse.py : script qui analyse les données et générer les graphiques


### Customiser les visuels 

- Si vous utilisez les visuels standards de la plateforme, vous n'avez pas à faire de travaux front.

- Si vous souhaitez créer une visualisation spécifique, il vous faudra éditer le CSS et le JS de la plateforme (voir documentation plateforme)


### Paramétrer la planification

- Décommenter dans Dockerfile la bonne ligne en fonction de la planification choisie (planification ou exécution une fois pour toute)

- Si planification, éditer *schedule.cron* pour configurer la planification choisie. Par défaut, les scripts seront exécutés chaque jour à 2H du matin


### Inclure le nouveau projet Analytics à la production (à faire par l'administrateur)

- Créer un repo sur hub.docker.com, le relier au dépôt bitbucket correspondant, et déclencher un build

- Editer *docker-compose.yml* du projet docker-compose pour ajouter l'étape de build correspondant à l'ajout de cette nouvelle analyse

```
  analytics-X:
    image: antoinebacalu/analytics-X
    container_name: analytics-X
    depends_on:
      - postgres
    networks:
      - datapolitics-net
```

- Sur le serveur de production, pull la dernière version de *docker-compose.yml* et run l'image.
