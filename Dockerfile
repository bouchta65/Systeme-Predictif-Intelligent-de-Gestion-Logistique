    # Utiliser une image officielle Python comme base
    FROM python:3.11-slim

    # Définir le répertoire de travail dans le conteneur
    WORKDIR /src

    # Installer Java (nécessaire pour Spark) et quelques utilitaires
    RUN apt-get update && \
        apt-get install -y default-jre-headless && \
        rm -rf /var/lib/apt/lists/*

    # Installer PySpark et les librairies Python 
    COPY requirements.txt /src/
    
    RUN pip install --default-timeout=1000 --no-cache-dir -r requirements.txt
    # Copier le code source de ton projet dans le conteneur
    COPY . /src

    # Exposer le port pour Streamlit
    EXPOSE 1234 8888

    # Commande par défaut pour lancer ton application Streamlit
    CMD ["streamlit", "run", "view/app.py", "--server.port=1234", "--server.address=0.0.0.0"]
