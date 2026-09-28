---
name: onlineshopping-frontend
description: 'Use when working on the onlineshopping React (Vite) frontend (frontend/) — pages, components, cart/auth context, API client, image display, or currency formatting. Covers project structure, run commands, resolveImageUrl/formatCurrency helpers, and styling conventions.'
---

# Onlineshopping Frontend (Vite + React)

## Stack
- Vite + React (JSX, hooks), `react-router-dom`, `axios`
- No CSS framework — custom dark/glassmorphism theme in `src/index.css`

## Structure (`frontend/src/`)
- `api/client.js` — shared axios instance (`baseURL = ${API_ORIGIN}/api`), attaches `Authorization: Bearer <token>` from `localStorage`, plus two helpers:
  - `resolveImageUrl(path)` — converts a backend-relative path (e.g. `/static/uploads/xxx.jpg`) into an absolute URL using `API_ORIGIN` (static files are served outside the `/api` prefix, so this can't just reuse `baseURL`). Passes through already-absolute `http(s)://` or `data:` URLs unchanged.
  - `formatCurrency(amount)` — returns `` `₹${Number(amount).toFixed(2)}` ``. **All monetary values must be rendered through this helper** — never hardcode `$` or format numbers manually inline.
- `components/` — `Navbar.jsx`, `ProductCard.jsx` (buyer-facing product tile), `ProtectedRoute.jsx`
- `pages/` — `Products.jsx` (shop/home), `Cart.jsx`, `Checkout.jsx`, `Orders.jsx`, `Login.jsx`, `Register.jsx`, `SellerDashboard.jsx` (seller product CRUD + image upload)
- `context/` — `AuthContext.jsx` (user/token state), `CartContext.jsx` (cart state + add/update/remove)

## Run
```bash
cd frontend && npm run dev -- --port 5173
```
Check it's serving: `curl -s http://localhost:5173/ | head -20`.

## Currency
- The backend returns plain numbers (`price`, `final_price`, `line_total`, `total_amount`, `subtotal`, `total_discount`) with no currency symbol.
- The frontend is the single source of truth for currency display: import `formatCurrency` from `../api/client` and wrap every price/total before rendering, e.g. `{formatCurrency(product.final_price)}`. Do not reintroduce `$` in JSX or template literals.
- Form labels referencing price should say `Price (₹)`, not `Price ($)`.

## Images
- Product images are uploaded via `SellerDashboard.jsx`'s file input (`POST /products/upload-image`, `multipart/form-data`), which stores the returned relative path in `form.image_url`.
- Anywhere a product image is rendered (`ProductCard.jsx`, `Cart.jsx`, `SellerDashboard.jsx` list), wrap the `src` with `resolveImageUrl(product.image_url)` — a bare relative path won't resolve correctly against the page origin.
- Keep placeholder/fallback images (inline SVG `data:` URIs) as the `||` fallback when `image_url` is empty.

## Conventions
- Pages fetch data with the shared `client` from `api/client.js`, not raw `fetch`/`axios.create()` elsewhere.
- Keep form state as flat objects with a generic `update(field) => (e) => setForm(...)` pattern (see `SellerDashboard.jsx`, `Checkout.jsx`).
- Styling: add new component-specific rules to `src/index.css` near related existing rules (e.g. `.image-preview` was added next to `.seller-product-row img`); no CSS modules/styled-components.
