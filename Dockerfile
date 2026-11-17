# 1. Imagen base: Python 3.13 "slim" (liviana = menos paquetes = menos vulnerabilidades).
#    Se usa 3.13 porque requirements.txt no fija versión de Django y la última (6.x) exige Python >= 3.12.
FROM python:3.13-slim

# 2. Sin archivos .pyc y con logs inmediatos (se ven al tiro en GitHub Actions)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 3. Carpeta de trabajo dentro del contenedor (equivale a la raíz del repo)
WORKDIR /app

# 4. Primero SOLO requirements.txt: si no cambian las dependencias, Docker reutiliza esta capa en caché
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 5. Luego el resto del proyecto (lo que excluye .dockerignore no entra, ej: .env)
COPY . .

# 6. Usuario sin privilegios: si alguien vulnera el contenedor, no es root
RUN useradd --create-home appuser && chown -R appuser /app
USER appuser

# 7. manage.py está en backend/
WORKDIR /app/backend

EXPOSE 8000

# 8. 0.0.0.0 = escuchar en todas las interfaces, para poder entrar desde fuera del contenedor
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
