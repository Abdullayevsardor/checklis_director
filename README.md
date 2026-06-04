# checklis_director
checklis_director

## Deployment

This project includes a backend API and a Vite + React frontend.

### Docker deployment

1. Copy environment files:
   - `cp .env.example .env`
   - `cp checklist-frontend/.env.example checklist-frontend/.env`
2. Update `.env` values for your production environment.
3. Build and run:
   - `docker-compose up --build`

The backend will be available on `http://localhost:8000`, and the frontend preview on `http://localhost:5173`.

### Local environment

- Backend: `uvicorn app.main:app --reload --host 127.0.0.1 --port 8000`
- Frontend: `npm install` then `npm run dev` in `checklist-frontend`
