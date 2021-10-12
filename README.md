<div align="center" id="top"> 


  <!-- <a href="https://{{app_url}}.netlify.app">Demo</a> -->
</div>

<h1 align="center">twitter-listener</h1>

<br>

## :dart: A propos ##

Ce projet récupère l'ensemble des tweets postés par les candidats à la présidentielle 2022. 


## :white_check_mark: Requirements ##

- Python 3.7+
- Docker et un compte hub.docker.com (si vous souhaitez utiliser Docker)
- Un fichier .env à la racine du projet avec les variables d'environnement suivantes : 
  - BEARER_TOKEN (à récupérer depuis console twitter developers)
  - ELASTIC_URL = l'url du serveur elastic search ou seront déversées les données
  - ELASTIC_PORT = le port du serveur elastic search
  - ELASTIC_USERNAME = le nom d'utilisateur
  - ELASTIC_PWD = le mot de passe


## :white_check_mark: Lancement avec Docker ##

sudo docker run -e BEARER_TOKEN=BEARER_TOKEN -e ELASTIC_URL=ELASTIC_URL -e ELASTIC_PORT=ELASTIC_PORT -e SENDER_EMAIL=SENDER_EMAIL -e ELASTIC_USERNAME=ELASTIC_USERNAME -e ELASTIC_PWD=ELASTIC_PWD antoinebacalu/twitter-listener
