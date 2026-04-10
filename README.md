# SatTrack

A satellite tracking platform for visualizing and managing Earth-orbiting satellites, built with Django and React. This project was developed in CPSC 471 at the Univeristy of Calgary, Calgary, Alberta, Canada and was designed to implement a relational database system in MySQL. Where possible we attempted to follow best practice for repository setup, code organization and code structure as well as best security practices attainable within the development time available. One area where best practice was not upheld was in views.py files where we intentially didnt user djangos models and serializers to create interfaces between django and the database as we wanted to display our SQL queries in the codebase itself.

---

## GitHub Repository

GitHub Repository: https://github.com/ashton-jgiles/sattrack

---

## Running the App

There are two ways to run SatTrack — pulling the pre-built image from GitHub, or cloning the repo and building locally.

### Requirements

Both paths require **Docker Desktop**:

- [Download Docker Desktop](https://www.docker.com/products/docker-desktop/) (Windows / Mac / Linux)

No Python, Node, or MySQL installation needed.

---

### Option 1 — Pull from GitHub (Recommended)

The fastest way to run SatTrack. Downloads the pre-built image — no compilation required.

**1. Download the required files**

```bash
curl -O https://raw.githubusercontent.com/ashton-jgiles/sattrack/main/docker-compose.yml
curl -O https://raw.githubusercontent.com/ashton-jgiles/sattrack/main/.env.example
```

**2. Create your environment file**

```bash
cp .env.example .env
```

Open `.env` and fill in `SECRET_KEY`:

```bash
# Generate a secret key by running this in your terminal:
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

**3. Pull the image and start the app**

```bash
docker-compose pull
docker-compose up
```

**4. Visit the app**

```
http://localhost:8000
```

> The first run takes ~2 minutes while the database is seeded with satellite data. Subsequent runs start in seconds.

---

### Option 2 — Clone and Build

For developers who want to run or modify the source code.

**Additional requirements:**

- Git
- Node 22+
- Python 3.14+

**1. Clone the repository**

```bash
git clone https://github.com/ashton-jgiles/sattrack.git
cd sattrack
```

**2. Create your environment file**

```bash
cp .env.example .env
```

Open `.env` and fill in the following:

| Variable       | How to get it                                                      |
| -------------- | ------------------------------------------------------------------ |
| `SECRET_KEY`   | Run `python -c "import secrets; print(secrets.token_urlsafe(50))"` |
| `CESIUM_TOKEN` | Get a free token at [ion.cesium.com](https://ion.cesium.com)       |
| `DB_PASSWORD`  | Leave blank for local development                                  |

**3. Build and start**

```bash
docker-compose up --build
```

**4. Visit the app**

```
http://localhost:8000
```

> The first run takes ~2 minutes while the image builds and the database is seeded. Subsequent `docker-compose up` calls start in seconds.

---

## Stopping the App

```bash
# Stop containers (preserves database)
docker-compose down

# Stop and wipe the database (full reset)
docker-compose down -v
```

## Database Access (Any Database Manager)

While the containers are running, connect to the containerized MySQL database:

| Field    | Value                                        |
| -------- | -------------------------------------------- |
| Host     | `localhost`                                  |
| Port     | `3307`                                       |
| Database | `sattrack`                                   |
| Username | `root`                                       |
| Password | _(your `DB_PASSWORD` from `.env`, or blank)_ |

---

## Using the System

Using the seeded database we have four different user types to test user level access and user subclasses. The following seeded users are given for testing

| Role         | Username      | Password       |
| ------------ | ------------- | -------------- |
| Admin        | `admin01`     | `admin123`     |
| Data Analyst | `analyst01`   | `analyst123`   |
| Scientist    | `scientist01` | `scientist123` |
| Amateur      | `amateur01`   | `amateur123`   |

Additionally you can create your own user in the local system. For more information on specific systems within SatTrack please refer to the final report document in the docs/ folder and find sections on the visual interface and user guide at the bottom of that document.

---
