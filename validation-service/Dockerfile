FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ /app/src/

# Ensure PYTHONPATH is set to include /app/src
ENV PYTHONPATH=/app/src

EXPOSE 8000

# Correct CMD to reference the app inside src folder
CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000"]