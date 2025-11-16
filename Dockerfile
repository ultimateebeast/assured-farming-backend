FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

WORKDIR /usr/src/app

# System dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       gcc \
       python3-dev \
       pkg-config \
       libcairo2-dev \
       libpango1.0-dev \
       libgdk-pixbuf-xlib-2.0-dev \
       libffi-dev \
       libssl-dev \
       libjpeg-dev \
       libfreetype6-dev \
       libxml2-dev \
       libxslt1-dev \
       zlib1g-dev \
       shared-mime-info \
       git \
       libpq-dev \
       netcat-openbsd \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy and install production requirements
COPY requirements-prod.txt ./
RUN pip install --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r requirements-prod.txt

# Copy app source (after installing deps for layer caching)
COPY . /usr/src/app/

# Copy start script into image and ensure executable
COPY start.sh /usr/src/app/start.sh
RUN chmod +x /usr/src/app/start.sh

# Use start.sh as the container CMD
CMD ["./start.sh"]
