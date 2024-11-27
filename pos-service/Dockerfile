# Step 1: Use a base Python image
FROM python:3.11-slim

# Schritt 2: Setze das Arbeitsverzeichnis im Container
WORKDIR /app

# Schritt 3: Kopiere die requirements.txt und installiere Abhängigkeiten
COPY requirements.txt /app/

# Installiere die in requirements.txt angegebenen Pakete
RUN pip install --no-cache-dir -r requirements.txt

# Install curl
RUN apt-get update && apt-get install -y curl

# Schritt 4: Kopiere den restlichen Code in den Container
COPY src/ /app/src/

# Schritt 5: Exponiere den Port, falls erforderlich (z.B. für API-Endpunkte)
# EXPOSE 8000  # Falls du eine Web-App hast, die auf einem Port läuft

# Schritt 6: Befehl zum Ausführen des Python-Skripts
CMD ["python", "src/app.py"]