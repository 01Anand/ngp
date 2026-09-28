---
name: onlineshopping-backend
description: 'Use when working on the onlineshopping FastAPI backend (backend/) — adding/editing routes, models, schemas, auth, product/cart/order logic, image uploads, or dependency/env issues. Covers project structure, run/test commands, auth model, currency (INR), image upload static serving, and known pitfalls like duplicate uvicorn processes on port 8000.'
---

# Onlineshopping Backend (FastAPI)

## Stack
- FastAPI 0.115.0 + SQLAlchemy 2.0.35 (async) + asyncpg 0.31.0 + PostgreSQL (`postgresql+asyncpg://postgres:postgres@localhost:5432/onlineshopping`)
- JWT auth via `python-jose`, password hashing via `passlib[bcrypt]` + `bcrypt==4.0.1` (pinned — newer bcrypt breaks passlib)
- Pydantic 2.13.5 + pydantic-settings 2.15.0, `greenlet==3.5.6` (bumped for Python 3.14 wheel availability, but project actually runs on the `.venv` Python 3.12 interpreter)
- File uploads via `python-multipart`, served with `fastapi.staticfiles.StaticFiles`

## Structure (`backend/app/`)
- `main.py` — app factory, `lifespan`, CORS, static mount, router registration, `/api/health`
- `config.py` — `Settings` (DATABASE_URL, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, BACKEND_CORS_ORIGINS/`cors_origins`), plus `BASE_DIR` / `UPLOAD_DIR` (`app/static/uploads`)
- `database.py` — async engine + `Base`
- `models.py` — SQLAlchemy models (User, Product, CartItem, Order, OrderItem)
- `schemas.py` — Pydantic request/response schemas (`ProductCreate`, `ProductUpdate`, `ProductPublicOut`, `DiscountUpdate`, etc.)
- `security.py` — password hashing + JWT helpers
- `routers/{auth,products,cart,orders}.py` — route handlers

## Run / verify
```bash
cd backend && source .venv/bin/activate && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
curl -s http://localhost:8000/api/health   # {"status":"ok"}
```
Install deps: `pip install -q -U -r requirements.txt`. Sanity-check imports: `python -c "from app.main import app; print(len(app.routes))"`.

## Auth model
- Roles: `user` (buyer) and `seller` (enum in schemas — register payload must send `role: "user"|"seller"` and `name`, not `full_name`/`buyer`).
- JWT bearer tokens; `get_current_seller` dependency gates seller-only routes.

## Product pricing & currency
- All monetary fields (`price`, `final_price`, `line_total`, `total_amount`, etc.) are plain numeric values with **no currency symbol server-side** — currency formatting (₹) is a frontend-only concern (see frontend skill). Do not add a `$`/currency string on the backend.
- Discount set via `PATCH /api/products/{id}/discount`; `final_price` is computed server-side and included in `ProductPublicOut`/`CartItemOut`/`OrderItemOut`.

## Image uploads
- `POST /api/products/upload-image` (seller-only): validates content-type against a whitelist (`image/jpeg|png|webp|gif`), enforces a 5MB max, saves under `UPLOAD_DIR` with a `uuid4().hex`-generated filename (never trust user filenames — path traversal risk), returns `{"image_url": "/static/uploads/<uuid>.jpg"}`.
- `Product.image_url` stores that relative path, not an absolute URL.
- **Critical ordering bug (already hit once):** `app.mount("/static", StaticFiles(directory=UPLOAD_DIR.parent))` runs at **import time**. If `UPLOAD_DIR.mkdir(...)` only happens inside `lifespan()` (which runs after import), every `--reload` cycle crashes the worker with `RuntimeError: Directory '.../app/static' does not exist`, making the server look "hung"/unreachable. Fix: call `UPLOAD_DIR.mkdir(parents=True, exist_ok=True)` at module level in `main.py` *before* the `app.mount(...)` call, not only in `lifespan`.

## Known pitfall: duplicate backend processes on port 8000
A stray conda environment (`aifundamentals`, Python 3.14, path `/opt/homebrew/Caskroom/miniconda/base/envs/aifundamentals`) has repeatedly been used to launch `uvicorn app.main:app --reload --port 8000` from this same `backend/` directory, binding the same port as the correct `.venv` (Python 3.12) server. macOS then randomly load-balances requests between both processes, causing confusing intermittent failures (e.g. registration "not working").
- Diagnose: `lsof -i :8000 | cat` then `ps -p <pid> -o pid,ppid,command | cat` for every listener.
- The correct process's binary path is `.../backend/.venv/bin/uvicorn ... --host 0.0.0.0 --port 8000 --reload`. Anything from `.../miniconda/base/envs/aifundamentals/...` is stray — kill it (`kill <pid>`), also kill its `--multiprocessing-fork` child if present.
- Always re-verify with `lsof -i :8000 | cat` and a `curl http://localhost:8000/api/health` after killing, before trusting further test results.

## Testing a new endpoint quickly
```bash
BASE=http://localhost:8000/api
TOKEN=$(curl -s -X POST $BASE/auth/register -H 'Content-Type: application/json' \
  -d '{"name":"Test Seller","email":"seller@test.com","password":"password123","role":"seller"}' \
  | python3 -c "import sys,json;print(json.load(sys.stdin)['access_token'])")
curl -s -X POST $BASE/products/upload-image -H "Authorization: Bearer $TOKEN" -F "file=@/tmp/test.jpg;type=image/jpeg"
```
