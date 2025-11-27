# The Shinobi Project

A digital agency website for local business infrastructure and innovation.

## Project Structure

```
the-shinobi-project/
├── backend/          # Django settings
├── portfolio/        # Django portfolio app (API)
├── frontend/         # Next.js frontend
├── manage.py
└── venv/
```

## Quick Start

### Backend (Django)

```bash
# Activate virtual environment
source venv/bin/activate

# Run migrations
python manage.py migrate

# Seed portfolio data
python manage.py seed_projects

# Create superuser (for admin)
python manage.py createsuperuser

# Run server
python manage.py runserver 8000
```

### Frontend (Next.js)

```bash
cd frontend

# Install dependencies
npm install

# Run dev server
npm run dev
```

## URLs

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000/api/
- **Admin:** http://localhost:8000/admin/

## API Endpoints

- `GET /api/projects/` - List all projects
- `GET /api/projects/{slug}/` - Get project by slug
- `GET /api/projects/featured/` - List featured projects
- `GET /api/projects/categories/` - List all categories
- `POST /api/contact/` - Submit contact form
