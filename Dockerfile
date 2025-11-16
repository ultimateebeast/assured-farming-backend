FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

WORKDIR /usr/src/app

# Install system deps needed to build pycairo / weasyprint / xhtml2pdf and common Python build tools
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

COPY requirements.txt ./

# install production dependencies only to keep image small and compatible
COPY requirements-prod.txt ./
RUN pip install --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r requirements-prod.txt


COPY . /usr/src/app/

COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
