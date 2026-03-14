## Team Setup (After Cloning)

# 1. Clone

git clone https://github.com/yourteam/sattrack.git
cd sattrack

- Open the folder in VSCode — you will be prompted to install all recommended extensions. Click **Install All**.

# 2. Database — in any Database tool where you can connect to localhost

# CREATE DATABASE sattrack;

# Run db/01_create.sql

# 3. Environment

Create a file called .env and copy and past the code in .env example and fill it with the database connection information

Generate your secret key and add it to the secret key field using this
python -c "import secrets; print(secrets.token_urlsafe(50))"

# Fill in DB_PASSWORD and SECRET_KEY in .env

# 4. Backend

cd backend
pip install -r requirements.txt
python manage.py migrate --fake-initial
python manage.py runserver

# 5. Frontend (new terminal)

cd backend/frontend
npm install
npm run dev

# 6. Visit http://localhost:8000

## Branch Strategy

main ← protected, submission only
dev ← all features merge here
feature/sc-xxx-description ← branch from dev, PR back to dev

- Require 1 approval on all PRs
- No direct pushes to main or dev
- Branch naming follows Shortcut story IDs

## Schema Changes

1. Make change locally in DBeaver
2. Write db/migrations/04_description.sql
3. Update corresponding models.py
4. Commit both files and open PR
5. Teammates pull and run the migration file in DBeaver

## Important Info

A sample endpoint has been setup using <localhost>/api/satellite/test. The code is inside the satellite folder to use as reference for creating future endpoints. The default page is the homepage when openning localhost. Going to <localhost>/login will show a new page for login. All of the code for routing to new pages can be found in the src directory of the frontend directory. All the table models have been setup for each table in our database. See models.py in the satellites directory as an example for what the tabel models look like.

## Endpoint Testing

Run this in the database to generate a sample satellite to test how apis work on the frontend use the method above by visiting <localhost>/api/satellite/test to see the backend result. The /login page will show this data for now will be changed later. When you view the login page after running the insert code below you should see the satellite name and its orbit type so youll see Test Satellite - LEO on the page. Make sure to use the delete operation below to clean up the database

-- INSERT test satellite
INSERT INTO satellite (
name,
description,
orbit_type,
norad_id,
object_id,
classification,
dataset_id
) VALUES (
'Test Satellite',
'Temporary test entry — delete after testing',
'LEO',
'99999',
'TEST-001',
'U',
1
);

DELETE FROM satellite
WHERE norad_id = '99999';
