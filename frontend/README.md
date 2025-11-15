This folder is a placeholder for an optional React SPA that consumes the DRF endpoints.

Recommended quick start:

1. Create app with Vite or CRA and put in this folder.
2. Use JWT for API auth (store access token in memory, refresh via refresh token endpoint).
3. Example endpoints:
   - POST /api/v1/accounts/token/ -> obtain JWT
   - GET /api/v1/marketplace/listings/
