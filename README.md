# SatTrack

A satellite tracking platform for visualizing and managing Earth-orbiting satellites, built with Django and React. This project was developed in CPSC 471 at the Univeristy of Calgary, Calgary, Alberta, Canada and was designed to implement a relational database system in MySQL. Where possible we attempted to follow best practice for repository setup, code organization and code structure as well as best security practices attainable within the development time available. One area where best practice was not upheld was in views.py files where we intentially didnt user djangos models and serializers to create interfaces between django and the database as we wanted to display our SQL queries in the codebase itself.

---

## GitHub Repository

GitHub Repository: https://github.com/ashton-jgiles/sattrack

---

## Running the App

There are three ways to run SatTrack.

| Option                                                                  | Requirements                | Best for                                |
| ----------------------------------------------------------------------- | --------------------------- | --------------------------------------- |
| [1 — Pull pre-built image](#option-1--pull-pre-built-image-recommended) | Docker Desktop only         | Fastest setup, no build step            |
| [2 — Clone and run with Docker](#option-2--clone-and-run-with-docker)   | Docker Desktop + Git        | Building from source, no local installs |
| [3 — Clone and run locally](#option-3--clone-and-run-locally)           | MySQL + Python + Node + Git | Local development without Docker        |

---

### Option 1 — Pull Pre-Built Image (Recommended)

Downloads the pre-built image from GitHub — no compilation required.

**Requirements:** [Docker Desktop](https://www.docker.com/products/docker-desktop/)

**1. Download the required files**

```bash
curl -O https://raw.githubusercontent.com/ashton-jgiles/sattrack/main/docker-compose.yml
curl -O https://raw.githubusercontent.com/ashton-jgiles/sattrack/main/.env.example
```

**2. Create your environment file**

```bash
cp .env.example .env
```

Open `.env` and fill in `SECRET_KEY`. You can generate one with Python if you have it installed, or use any random 50-character string:

```bash
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

> `CESIUM_TOKEN` is already baked into the pre-built image — leave it blank.

**3. Pull the image and start the app**

```bash
docker-compose pull
docker-compose up
```

**4. Visit the app**

```
http://localhost:8000
```

> The first run takes ~2 minutes while the database is seeded. Subsequent runs start in seconds.

---

### Option 2 — Clone and Run with Docker

Builds the image locally from source. Docker handles all Node, Python, and MySQL — nothing else needs to be installed.

**Requirements:** [Docker Desktop](https://www.docker.com/products/docker-desktop/) + Git

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

| Variable       | Required | How to get it                                                                                     |
| -------------- | -------- | ------------------------------------------------------------------------------------------------- |
| `SECRET_KEY`   | Yes      | Run `python -c "import secrets; print(secrets.token_urlsafe(50))"`                                |
| `CESIUM_TOKEN` | Yes      | Get a free token at [ion.cesium.com](https://ion.cesium.com) — baked into the image at build time |
| `DB_PASSWORD`  | No       | Leave blank for local development                                                                 |

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

### Option 3 — Clone and Run Locally

Runs the backend and frontend directly on your machine without Docker.

**Requirements:** Git, [MySQL 8.0](https://dev.mysql.com/downloads/mysql/), [Python 3.12+](https://www.python.org/downloads/), [Node 22+](https://nodejs.org/)

**1. Clone the repository**

```bash
git clone https://github.com/ashton-jgiles/sattrack.git
cd sattrack
```

**2. Create the database**

Connect to your local MySQL instance and run the schema script:

```bash
mysql -u root -p -e "source db/01_create.sql"
```

**3. Seed the database**

```bash
cd backend
pip install -r requirements.txt
cd ../ingestion
python seed.py
```

> Outputs `Seed complete` after 20–60 seconds.

**4. Create your environment file**

```bash
cp .env.example .env
```

Open `.env` and fill in the following:

| Variable       | Required | How to get it                                                      |
| -------------- | -------- | ------------------------------------------------------------------ |
| `SECRET_KEY`   | Yes      | Run `python -c "import secrets; print(secrets.token_urlsafe(50))"` |
| `CESIUM_TOKEN` | Yes      | Get a free token at [ion.cesium.com](https://ion.cesium.com)       |
| `DB_PASSWORD`  | Yes      | Your local MySQL root password                                     |
| `DB_HOST`      | —        | Leave as `localhost`                                               |

**5. Start the backend**

```bash
cd backend
python manage.py migrate --fake-initial
python manage.py runserver
```

**6. Start the frontend** (new terminal)

```bash
cd backend/frontend
npm install
npm run dev
```

**7. Visit the app**

```
http://localhost:8000
```

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

---

## User Guide

### Landing Page

Basic landing page where users can see basic stats and login to the system.

![Landing Page](docs/userGuide/Screenshot%202026-04-11%20184916.png)

---

### Login Page

Basic login page where a user can either login, create their account, or return to the landing page.

![Login Page](docs/userGuide/Screenshot%202026-04-11%20184947.png)

---

### Create Account Page

Create account page where users enter all the necessary information for their account.

![Create Account](docs/userGuide/Screenshot%202026-04-11%20185024.png)

---

### Main Dashboard

Logged in as an admin user — depending on your user level the number of pages in the left sidebar will be different. This is the home page with stat cards at the top and a list of active satellites on the right. You can select any satellite from the list to see it highlighted on the globe and view its details.

![Main Dashboard](docs/userGuide/Screenshot%202026-04-11%20185112.png)

Selecting a satellite opens its full details panel above the globe.

![Satellite Detail](docs/userGuide/Screenshot%202026-04-11%20185253.png)

---

### Datasets

Datasets page where you can view a high-level overview of each dataset and the satellites contained in it.

![Datasets](docs/userGuide/Screenshot%202026-04-11%20185321.png)

Clicking a dataset opens a details popup with additional metadata.

![Dataset Details Popup](docs/userGuide/Screenshot%202026-04-11%20185349.png)

---

### User Profile

User profile page where you can change your name, username, and password. All user types have access to this page.

![User Profile](docs/userGuide/Screenshot%202026-04-11%20185416.png)

---

### Visualizations

Restricted to Scientist users and above (level 2+). Shows charts and stats derived from the satellite database.

![Visualizations](docs/userGuide/Screenshot%202026-04-11%20185506.png)

---

### Reviews

Restricted to Data Analyst users and above (level 3+). Shows datasets pending review.

![Reviews - Pending](docs/userGuide/Screenshot%202026-04-11%20185610.png)

Previously reviewed (closed) datasets can be viewed by clicking **View Closed**.

![Reviews - Closed](docs/userGuide/Screenshot%202026-04-11%20185646.png)

A dataset pending review shows its details along with Approve and Reject actions.

![Reviews - Pending Review Sample](docs/userGuide/Screenshot%202026-04-11%20185717.png)

---

### Manage Datasets

Admin only. View all datasets regardless of review status. Datasets can be added, edited, or deleted from this page.

![Manage Datasets](docs/userGuide/Screenshot%202026-04-11%20185759.png)

Edit an existing dataset via the edit modal.

![Edit Dataset Modal](docs/userGuide/Screenshot%202026-04-11%20185847.png)

Add a new dataset via the add modal.

![Add Dataset Modal](docs/userGuide/Screenshot%202026-04-11%20185858.png)

---

### Manage Satellites

Admin only. View, edit, and delete existing satellites. Deleted satellites within the retention window can be recovered. New satellites can be added via a three-step wizard.

![Manage Satellites](docs/userGuide/Screenshot%202026-04-11%20185919.png)

Edit an existing satellite via the edit modal.

![Edit Satellite Modal](docs/userGuide/Screenshot%202026-04-11%20190040.png)

**Step 1** — Select a dataset to import a satellite from.

![Add Satellite - Step 1](docs/userGuide/Screenshot%202026-04-11%20190058.png)

**Step 2** — Select a satellite from the dataset that is not already in the database.

![Add Satellite - Step 2](docs/userGuide/Screenshot%202026-04-11%20190116.png)

**Step 3** — Fill in any missing information and confirm.

![Add Satellite - Step 3](docs/userGuide/Screenshot%202026-04-11%20190145.png)

---

### Settings

Admin only. Manage users — remove accounts, change access levels, and edit user details. Also provides a button to refresh satellite trajectory data (data is static and not live-piped from CelesTrak).

![Settings](docs/userGuide/Screenshot%202026-04-11%20190230.png)

Edit a user via the edit user modal.

![Edit User Modal](docs/userGuide/Screenshot%202026-04-11%20190355.png)

---
