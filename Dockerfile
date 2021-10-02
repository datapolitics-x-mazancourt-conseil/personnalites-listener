# syntax=docker/dockerfile:1
FROM python:3

# Récupère la librairie datapolitics core et la clé d'accès
WORKDIR /datapolitics/lib
RUN apt-get update
RUN apt-get install -y git
RUN git clone https://antoine-datapolitics:5n7LtftnAFxCKTNRE42w@bitbucket.org/antoine-datapolitics/datapolitics-core.git
WORKDIR /datapolitics/lib/datapolitics-core
RUN python setup.py sdist
RUN pip3 install dist/datapolitics_core-0.0.3.tar.gz

# Prépare le planification
RUN apt-get install -y cron
COPY schedule.cron /etc/cron.d/schedule.cron
RUN chmod 0644 /etc/cron.d/schedule.cron && crontab /etc/cron.d/schedule.cron

# installe toutes les locales (notamment pour support des dates)
RUN apt-get install -y locales locales-all

# installe les dépendances externes
WORKDIR /datapolitics/app
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

# copie le code de la plateforme
COPY . .
COPY database.ini.example database.ini

# lance la génération des analyses
RUN chmod +x build_charts.sh
# CMD ["cron", "-f"] (si planification)
# CMD ["sh", "build_charts.sh"] (si exécution une seule fois)


