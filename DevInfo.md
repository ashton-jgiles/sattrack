## Team Setup (After Cloning)

# 1. Clone

git clone https://github.com/yourteam/sattrack.git
cd sattrack

- Open the folder in VSCode — you will be prompted to install all recommended extensions. Click **Install All**.

# 2. Database — in any Database tool where you can connect to localhost

Run & "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -u <your_username> -p -e "source db/01_create.sql"
Then enter your MySQL Password

cd ingestion
python seed.py

# Should output

# Seed complete in 20s

Verfiy in DBeaver on Satellite Table if record exists

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
