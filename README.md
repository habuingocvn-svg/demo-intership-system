# Internship System — Setup Guide (Step 3)

## Prerequisites
- Python 3.10+
- PostgreSQL 14+
- Git

---

## 1. Clone / open the project
```bash
cd internship-system
```

## 2. Create a virtual environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac / Linux
source venv/bin/activate
```

## 3. Install dependencies
```bash
pip install -r requirements.txt
```

## 4. Create the PostgreSQL database
```bash
psql -U postgres
```
Inside psql:
```sql
CREATE DATABASE internship_db;
\q
```

## 5. Configure environment variables
Copy `.env` and fill in your values:
```
DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/internship_db
SECRET_KEY=any-random-string
JWT_SECRET_KEY=another-random-string
```

## 6. Run database migrations
```bash
flask --app run.py db init
flask --app run.py db migrate -m "initial schema"
flask --app run.py db upgrade
```

Or apply the raw SQL directly:
```bash
psql -U postgres -d internship_db -f database/schema.sql
```

## 7. Start the server
```bash
python run.py
```
Server runs at → http://localhost:5000

---

## Project structure
```
internship-system/
├── run.py                   # entry point
├── requirements.txt
├── .env                     # environment variables (never commit this)
├── database/
│   └── schema.sql
├── backend/
│   ├── __init__.py          # app factory
│   ├── config.py
│   ├── models/
│   │   └── models.py        # all SQLAlchemy models
│   ├── routes/              # one file per feature (Step 4)
│   │   ├── auth.py
│   │   ├── students.py
│   │   ├── companies.py
│   │   ├── internships.py
│   │   ├── applications.py
│   │   └── admin.py
│   ├── schemas/             # marshmallow schemas (Step 4)
│   ├── services/            # business logic (Step 4)
│   ├── middleware/          # auth guards (Step 4)
│   └── utils/               # helpers (Step 4)
└── frontend/
    ├── templates/           # HTML files (Step 5)
    └── static/
        ├── css/
        ├── js/
        └── images/
```

---

## API endpoints (preview — built in Step 4)
| Method | URL | Description |
|--------|-----|-------------|
| POST | /api/auth/register | Register new user |
| POST | /api/auth/login | Login, get JWT token |
| GET | /api/internships | List all open internships |
| POST | /api/internships | Company posts new internship |
| POST | /api/applications | Student applies |
| PATCH | /api/applications/:id | Accept / reject / withdraw |
| GET | /api/admin/users | Admin lists all users |
| PATCH | /api/admin/users/:id/ban | Admin bans a user |
