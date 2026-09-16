# API

Interactive OpenAPI documentation is available at `/docs` when the API is running.

| Area            | Endpoints                                                                                                |
| --------------- | -------------------------------------------------------------------------------------------------------- |
| Auth            | `POST /api/auth/register`, `/login`; `GET /me`                                                           |
| Catalogue       | `GET /api/products`, `/products/{id}`, `/categories`                                                     |
| Cart            | `GET /api/cart`, `POST /items`, `PUT/DELETE /items/{id}`, `DELETE /api/cart`                             |
| Profile         | `GET /api/orders`, `/orders/{id}`, `GET/POST /api/addresses`                                             |
| Payments        | `POST /api/payments/create-order`, `/verify`                                                             |
| Admin           | `/api/admin/dashboard`, `/orders`, `/users`; product/category mutation endpoints                         |
| Reviews         | `GET/POST /api/products/{id}/reviews`, `PUT/DELETE /api/reviews/{id}`, helpful vote and report endpoints |
| Recommendations | `/api/recommendations`, `/personalized`, `/products/{id}/similar`, `/frequently-bought-together`         |

All non-public calls require `Authorization: Bearer <JWT>`. Admin calls require a database-backed ADMIN role.

Review creation requires a PAID order containing that product, and that proof is never accepted from the browser. Public review listings contain only approved reviews and are paginated.
