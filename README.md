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

## Protecting server code when pushing

To avoid breaking the server when you `git push`, enable the provided local git hooks and use CI checks:

- Enable local hooks (one-time):

```bash
git config core.hooksPath .githooks
```

- The repository includes `.githooks/pre-push` (bash) and `.githooks/pre-push.ps1` (PowerShell). These run `pytest` and abort the push if tests fail.

- CI: GitHub Actions workflow is added at `.github/workflows/ci.yml`. It runs backend tests and builds the frontend on push and pull requests.

- For stronger protection, enable branch protection rules in your GitHub repo settings (require status checks such as the `CI` workflow before merging to `main`).

