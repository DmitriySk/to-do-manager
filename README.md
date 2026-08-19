# Personal To-Do Manager

A full-stack multi-user to-do manager. Each user signs in with Google or GitHub SSO and manages their own private lists/projects and tasks, with search, filters, and real-time WebSocket notifications for overdue and due-soon tasks.

**Business scenario:** a user manages personal work across multiple projects and wants a simple system to plan tasks, set priorities and deadlines, and quickly see what requires attention today and this week.

**Core rules:** the system supports multiple users, each user sees only their own data, and there is no sharing of any kind (no invites, no public links, no shared lists).

## Tech stack

| Layer     | Choice |
| --------- | ------ |
| Frontend  | React 18 + Vite + TypeScript, Material UI (MUI) v6, TanStack React Query |
| Backend   | Python 3.12, FastAPI, SQLAlchemy 2.0 (async) + Alembic |
| Database  | PostgreSQL 16 |
| Auth      | OAuth2/OIDC via Authlib (Google + GitHub), httpOnly signed session cookie |
| Real-time | Native WebSocket (`GET /ws`), no extra broker |

## Architecture

```
/backend    FastAPI app, SQLAlchemy models, Alembic migrations, pytest suite
/frontend   React + Vite SPA
docker-compose.yml   Postgres + backend always on; frontend only with the "full" profile
```

## Prerequisites

- Python 3.12+
- Node.js 18+
- PostgreSQL 16 (local install) **or** Docker Desktop

## Local run

There are three supported ways to run the app locally. All three assume you've filled in OAuth credentials as described in [OAuth setup](#oauth-setup).

### Option A — everything natively (no Docker)

```bash
# 1. Start Postgres yourself and create two databases: todo, todo_test

# 2. Backend
cd backend
cp .env.example .env        # fill in DATABASE_URL, OAuth secrets, SESSION_SECRET
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000

# 3. Frontend (in a second terminal)
cd frontend
cp .env.example .env
npm install
npm run dev
```

Frontend: http://localhost:5173 · Backend: http://localhost:8000 · API docs: http://localhost:8000/docs

### Option B — Docker for Postgres + backend, frontend on the host

```bash
cd backend && cp .env.example .env   # fill in OAuth secrets, SESSION_SECRET
cd ..
docker-compose up                     # starts postgres (5432) + backend (8000)

# in a second terminal
cd frontend
cp .env.example .env
npm install
npm run dev                           # frontend on 5173, talks to backend on 8000
```

### Option C — everything in Docker

```bash
cd backend && cp .env.example .env   # fill in OAuth secrets, SESSION_SECRET
cd ..
docker-compose --profile full up     # starts postgres (5432) + backend (8000) + frontend (5173)
```

In every option the frontend is served on `http://localhost:5173` and the backend on `http://localhost:8000` — OAuth redirect URIs are the same regardless of which option you pick.

### If a Docker build fails with a certificate error

`pip install`/`npm install` inside a container fail with `CERTIFICATE_VERIFY_FAILED` on machines where local antivirus or a corporate proxy intercepts TLS (their root CA is trusted by the host but not by a fresh container). Fix:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/export-local-ca.ps1
docker compose build --no-cache backend
docker compose --profile full build --no-cache frontend
```

See `backend/certs/README.md` for details. The exported certificate is machine-specific and git-ignored — it never leaves your machine.

## OAuth setup

The backend needs one set of credentials per provider, both pointing at `http://localhost:8000`.

### Google OAuth

1. Go to the [Google Cloud Console](https://console.cloud.google.com/apis/credentials) → create/select a project.
2. Configure the OAuth consent screen (External, testing mode is fine for local dev).
3. Create an **OAuth client ID** → Application type: **Web application**.
4. Authorized redirect URI: `http://localhost:8000/auth/callback/google`
5. Copy the **Client ID** and **Client Secret** into `backend/.env` as `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET`.

### GitHub OAuth

1. Go to [GitHub → Settings → Developer settings → OAuth Apps](https://github.com/settings/developers) → **New OAuth App**.
2. Homepage URL: `http://localhost:5173`
3. Authorization callback URL: `http://localhost:8000/auth/callback/github`
4. Copy the **Client ID** and generate a **Client Secret** into `backend/.env` as `GITHUB_CLIENT_ID` / `GITHUB_CLIENT_SECRET`.

## List deletion policy

Deleting a list/project **cascades**: it deletes the list and all tasks inside it in one step (enforced both at the database level via `ON DELETE CASCADE` and in the API). This was chosen over "block deletion until empty" for a simpler UX — the UI shows a confirmation dialog stating how many tasks will be removed before the delete happens.

## WebSocket protocol

**Endpoint:** `GET /ws` (same origin as the REST API, e.g. `ws://localhost:8000/ws`)

**Authentication:** the same httpOnly session cookie used by the REST API is sent automatically on the WebSocket handshake. If the cookie is missing or invalid, the server closes the connection with code `4401` before accepting it.

**Notification rules:**
- `overdue` — task status is not `done` **and** `due_date < today`
- `due_soon` — task status is not `done` **and** `due_date` is within the next 3 days (inclusive of today)

**Scheduling:** on connect, the server immediately sends an initial notification batch. While connected, it re-checks and re-sends periodically. The default interval is **30 seconds**, overridable per-connection via a `subscribe` message, clamped server-side to **10–300 seconds**.

### Server → client messages

Notification batch (sent immediately on connect, then every interval):
```json
{
  "type": "notification_batch",
  "generated_at": "2026-08-19T12:00:00Z",
  "notifications": [
    {
      "id": "overdue:42",
      "task_id": 42,
      "list_id": 7,
      "kind": "overdue",
      "title": "Submit report",
      "due_date": "2026-08-15",
      "priority": "high"
    }
  ]
}
```

Acknowledgement of a `subscribe` message:
```json
{ "type": "subscribed", "interval_seconds": 30, "enabled_types": ["overdue", "due_soon"] }
```

### Client → server messages

`subscribe` — sent once after the connection opens, carrying the client's preferences. This **changes server behavior**: it updates the check interval and which notification kinds this connection receives.
```json
{ "type": "subscribe", "interval_seconds": 30, "enabled_types": ["overdue", "due_soon"] }
```

`ack` — sent when the user dismisses a notification in the UI. This **changes server behavior**: the acknowledged notification is excluded from subsequent batches for the lifetime of that connection (in-memory; does not persist across reconnects).
```json
{ "type": "ack", "notification_id": "overdue:42" }
```

## API overview

Full interactive documentation (OpenAPI/Swagger) is auto-generated at `http://localhost:8000/docs` once the backend is running. Summary:

| Method | Path | Description |
| ------ | ---- | ----------- |
| GET | `/auth/login/{google\|github}` | Start OAuth login |
| GET | `/auth/callback/{google\|github}` | OAuth callback, sets session cookie |
| POST | `/auth/logout` | Clear session |
| GET | `/auth/me` | Current user, or 401 |
| POST | `/auth/test-login` | Mock SSO login for tests (only when `ENABLE_TEST_AUTH=true`) |
| GET | `/api/lists` | List the current user's lists |
| POST | `/api/lists` | Create a list |
| PATCH | `/api/lists/{id}` | Rename a list |
| DELETE | `/api/lists/{id}` | Delete a list (cascades tasks) |
| GET | `/api/tasks` | List tasks — query params: `list_id`, `status`, `priority`, `due_category` (`overdue\|today\|next_7_days\|all`), `q` (search title/description) |
| POST | `/api/tasks` | Create a task |
| GET | `/api/tasks/{id}` | Get one task |
| PATCH | `/api/tasks/{id}` | Update any task field, including quick status change |
| DELETE | `/api/tasks/{id}` | Delete a task |
| POST | `/api/dev/seed` | Create sample lists/tasks for the current user (only when `ENABLE_DEV_ENDPOINTS=true`) |
| GET | `/ws` | WebSocket notifications, see above |

Every list/task endpoint is scoped to the authenticated user; requests against another user's resources return `404`.

## Sample data

Two ways to seed sample data (lists + tasks, including deliberately overdue/due-soon ones so notifications show up immediately):

- **Via API:** log in, then `POST http://localhost:8000/api/dev/seed` (e.g. `curl -b cookies.txt -X POST http://localhost:8000/api/dev/seed`, or call it from `/docs`). Enabled by default locally (`ENABLE_DEV_ENDPOINTS=true`).
- **Via script:** `cd backend && python seed.py <provider> <provider_user_id>`, e.g. `python seed.py google local-dev-user`. Creates the user if it doesn't exist yet — useful before you've logged in through the UI once.

## Running tests

```bash
cd backend
pip install -r requirements.txt   # if not already installed
# ensure DATABASE_URL_TEST in .env points at a reachable Postgres database
pytest -v
```

The test database's schema is created and dropped automatically by the test suite (`tests/conftest.py`); it does not use Alembic migrations. Tests cover:

- **`test_auth.py`** — SSO login success path via the `/auth/test-login` mock/stub provider endpoint.
- **`test_lists_tasks.py`** — a user can create a list, create a task in it, filter and search tasks, and cascade-delete a list.
- **`test_authorization.py`** — a user cannot read, edit, or delete another user's lists or tasks (404 on every attempt).
- **`test_websocket_notifications.py`** — overdue/due-soon notifications are computed correctly against a frozen clock, the initial WebSocket batch reflects them, `subscribe` changes server-side connection state, and `ack` excludes a notification.

## Known limitations

- WebSocket `ack` state is in-memory per connection and does not persist across reconnects.
- The session cookie is not marked `Secure` by default (suitable for local HTTP development only) — set it before deploying over HTTPS.
- No password/email-based login — SSO only, per the spec.

## Acceptance checklist self-check

- [x] A new user can log in with Google and GitHub
- [x] A user can create lists, create tasks, and use search/filters
- [x] Data is private per user and cannot be accessed cross-account
- [x] While connected, the app receives real-time notifications for overdue and due-soon tasks
- [x] The WebSocket flow includes client→server messages (`subscribe`, `ack`) that change server behavior
- [x] Tests pass locally (`pytest -v`)
- [x] This README documents local run, OAuth setup, WebSocket protocol, API, and test command
