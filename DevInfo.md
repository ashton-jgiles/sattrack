## Backend

```bash
cd backend
pip install -r requirements.txt
python manage.py migrate --fake-initial
python manage.py migrate
```

## Frontend

```bash
cd backend/frontend
npm install
```

## Run

```bash
# Terminal 1
cd backend
python manage.py runserver

# Terminal 2
cd backend/frontend
npm run dev
```
