# Stage 1: Build React/webpack frontend
FROM node:22-alpine AS frontend-build

WORKDIR /build

# Copy package files first for better layer caching
COPY backend/frontend/package*.json backend/frontend/
RUN cd backend/frontend && npm ci

# Copy remaining frontend source
COPY backend/frontend/ backend/frontend/

# CESIUM_TOKEN is embedded in the webpack bundle at build time.
# dotenv-webpack's systemvars: true picks this up from the environment.
ARG CESIUM_TOKEN=""
ENV CESIUM_TOKEN=${CESIUM_TOKEN}

RUN cd backend/frontend && npm run build

# Stage 2: Django backend + ingestion scripts
FROM python:3.12-slim

WORKDIR /app

# mysqlclient requires the MySQL C client library headers
RUN apt-get update && apt-get install -y --no-install-recommends \
        pkg-config \
        default-libmysqlclient-dev \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .

# Include ingestion scripts — the seed service runs this image
# with a different working_dir and command (see docker-compose.yml)
COPY ingestion/ /ingestion/

# Webpack outputs to backend/frontend/static/{frontend/,cesium/}
COPY --from=frontend-build /build/backend/frontend/static/ frontend/static/

EXPOSE 8000
