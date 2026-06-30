# Pizza42 Online Ordering — Implementation Plan

## Dependencies
- `react-router-dom` — routing
- `bootstrap` + `react-bootstrap` — UI

## Folder Structure
```
src/
  main.jsx                          # Auth0Provider (unchanged)
  App.jsx                           # BrowserRouter + Layout + Routes
  App.css                           # Bootstrap overrides
  routes/
    Home.jsx                        # Hardcoded menu, "Add to Cart" buttons
    Cart.jsx                        # Cart items, qty controls, subtotal
    Checkout.jsx                    # Multi-step: address → confirm → place
    Profile.jsx                     # Orders from user['pizza42/orders']
  components/
    Layout.jsx                      # Navbar (Brand, Cart, Profile, Login/Logout)
    ProtectedRoute.jsx              # Redirects unauthenticated users
    PizzaCard.jsx                   # Single menu item display
    CartItem.jsx                    # Line item in cart
    OrderCard.jsx                   # Single order in profile
  context/
    CartContext.jsx                 # Cart state (useReducer + localStorage)
  api/
    client.js                       # Base fetch wrapper (orders.bongawonga.com)
    orders.js                       # placeOrder() — POST /api/orders
  data/
    menu.js                         # Hardcoded menu: pepperoni, sausage, hawaiian
  mocks/
    orders.js                       # Fake pizza42/orders for dev
```

## Routes

| Path | Component | Auth | Behavior |
|---|---|---|---|
| `/` | Home | No | Show 3 pizza cards with "Add to Cart" |
| `/cart` | Cart | No | List items, qty +/- , remove, subtotal, "Checkout" |
| `/checkout` | Checkout | Yes | Multi-step: address → review → place order |
| `/profile` | Profile | Yes | Orders list from user['pizza42/orders'] |

## Cart State (CartContext)
- `useReducer` with actions: ADD_ITEM, REMOVE_ITEM, UPDATE_QTY, CLEAR_CART
- Persisted to localStorage
- Exposed via useCart() hook
- Item shape: `{ id, name, price, quantity }`

## Checkout Flow
1. ProtectedRoute redirects to login if not authenticated
2. Step 1 — Delivery address: name, street, city, zip
3. Step 2 — Review order: items, address, total
4. Step 3 — Place order: POST /api/orders → clear cart → redirect to /profile

## Profile Page
- Reads user['pizza42/orders'] from Auth0 user object
- If claim missing, inject mock data
- Renders OrderCard components

## API Layer
- Base URL: https://orders.bongawonga.com
- client.js: thin fetch wrapper with Bearer token
- orders.js: placeOrder(orderData) → POST /api/orders → returns order

## Mock Data
- Menu: hardcoded Pepperoni $12.99, Sausage $13.99, Hawaiian $11.99
- Orders: injected fake claim when real claim absent
- API: placeOrder resolves with fake order object
