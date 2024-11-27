FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update && apt-get install -y curl

COPY src/ /app/src/

EXPOSE 8081

#CMD ["python", "src/main.py"]
CMD ["python", "-m", "bytewax.run", "src/refactored.py"]