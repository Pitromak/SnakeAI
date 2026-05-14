# Używamy lekkiej wersji Pythona
FROM python:3.11-slim

# Instalujemy biblioteki systemowe potrzebne dla Pygame i GUI
RUN apt-get update && apt-get install -y \
    libsdl2-dev \
    libsdl2-image-dev \
    libsdl2-mixer-dev \
    libsdl2-ttf-dev \
    libx11-6 \
    python3-tk \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Instalacja zależności Pythona
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kopiowanie kodu źródłowego
COPY . .

# Przekierowanie strumienia wideo (dla X11)
ENV DISPLAY=host.docker.internal:0.0

CMD ["python", "app.py"]